"""Business metrics. Core KPIs are calculated in Pandas AND in SQL so we can verify they agree."""
import pandas as pd

from src.database import run_query

# Months with fewer orders than this are treated as incomplete
MIN_MONTHLY_ORDERS = 500


def load_order_facts():
    return run_query("SELECT * FROM order_facts")


def complete_months(df):
    """Months with enough orders to compare fairly, sorted oldest to newest."""
    counts = df.groupby("purchase_month")["order_id"].nunique()
    return sorted(counts[counts >= MIN_MONTHLY_ORDERS].index)


# ---------- Pandas versions ----------

def kpis_pandas(df):
    delivered = df[df["is_delivered"] == 1]
    orders_with_items = df.loc[df["revenue"] > 0, "order_id"].nunique()
    return {
        "revenue": round(df["revenue"].sum(), 2),
        "freight": round(df["freight"].sum(), 2),
        "orders": int(df["order_id"].nunique()),
        "avg_order_value": round(df["revenue"].sum() / orders_with_items, 2),
        "on_time_rate": round(100 * (1 - delivered["is_late"].mean()), 2),
        "avg_review": round(df["review_score"].mean(), 2),
    }


def monthly_revenue_pandas(df):
    return (
        df.groupby("purchase_month", as_index=False)["revenue"].sum()
        .rename(columns={"purchase_month": "month"})
    )


def monthly_on_time(df):
    delivered = df[df["is_delivered"] == 1]
    out = delivered.groupby("purchase_month", as_index=False)["is_late"].mean()
    out["on_time_rate"] = (100 * (1 - out["is_late"])).round(1)
    return out.rename(columns={"purchase_month": "month"})[["month", "on_time_rate"]]


def review_by_delay(df):
    """Average review for on-time orders vs. orders grouped by how late they were."""
    d = df[(df["is_delivered"] == 1) & df["review_score"].notna()].copy()
    d["delay_group"] = pd.cut(
        d["days_late"],
        bins=[-1, 0, 3, 7, 14, 10_000],
        labels=["On time", "1-3 days late", "4-7 days late",
                "8-14 days late", "15+ days late"],
    )
    out = d.groupby("delay_group", observed=True).agg(
        orders=("order_id", "count"),
        avg_review=("review_score", "mean"),
        detractor_rate=("review_score", lambda s: 100 * (s <= 2).mean()),
    )
    return out.reset_index().round(2)


def late_vs_on_time_pandas(df):
    d = df[(df["is_delivered"] == 1) & df["review_score"].notna()]
    out = d.groupby("is_late", as_index=False)["review_score"].mean()
    out["status"] = out["is_late"].map({1: "late", 0: "on_time"})
    return out.rename(columns={"review_score": "avg_review"})[["status", "avg_review"]]


# ---------- SQL versions (from the raw tables) ----------

ON_TIME_SQL = """
SELECT 100.0 * SUM(CASE WHEN date(order_delivered_customer_date)
                          <= date(order_estimated_delivery_date)
                        THEN 1 ELSE 0 END) / COUNT(*)
FROM orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL
"""

AVG_REVIEW_SQL = """
SELECT AVG(order_score) FROM (
    SELECT AVG(review_score) AS order_score FROM reviews GROUP BY order_id
)
"""

LATE_VS_ON_TIME_SQL = """
SELECT CASE WHEN date(o.order_delivered_customer_date)
                 > date(o.order_estimated_delivery_date)
            THEN 'late' ELSE 'on_time' END AS status,
       AVG(r.order_score) AS avg_review
FROM orders o
JOIN (SELECT order_id, AVG(review_score) AS order_score
      FROM reviews GROUP BY order_id) r
  ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY status
"""


def _value(sql):
    return run_query(sql).iloc[0, 0]


def kpis_sql():
    return {
        "revenue": round(_value("SELECT SUM(price) FROM order_items"), 2),
        "freight": round(_value("SELECT SUM(freight_value) FROM order_items"), 2),
        "orders": int(_value("SELECT COUNT(DISTINCT order_id) FROM orders")),
        "avg_order_value": round(_value(
            "SELECT SUM(price) / COUNT(DISTINCT order_id) FROM order_items"), 2),
        "on_time_rate": round(_value(ON_TIME_SQL), 2),
        "avg_review": round(_value(AVG_REVIEW_SQL), 2),
    }


def monthly_revenue_sql():
    return run_query("""
        SELECT strftime('%Y-%m', o.order_purchase_timestamp) AS month,
               SUM(i.price) AS revenue
        FROM order_items i
        JOIN orders o ON i.order_id = o.order_id
        GROUP BY month
        ORDER BY month
    """)


def late_vs_on_time_sql():
    return run_query(LATE_VS_ON_TIME_SQL)


def compare():
    facts = load_order_facts()
    p = kpis_pandas(facts)
    s = kpis_sql()
    print(f"{'KPI':<18}{'Pandas':>16}{'SQL':>16}   Match")
    print("-" * 58)
    for key in p:
        match = "YES" if abs(p[key] - s[key]) < 0.01 else "NO"
        print(f"{key:<18}{p[key]:>16,}{s[key]:>16,}   {match}")
    print("\nReview score by delivery delay:")
    print(review_by_delay(facts).to_string(index=False))


if __name__ == "__main__":
    compare()