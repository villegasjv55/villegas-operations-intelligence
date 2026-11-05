"""Business metrics. Each KPI is calculated in Pandas AND in SQL so we can verify they agree."""
from src.database import run_query


def load_order_facts():
    return run_query("SELECT * FROM order_facts")


# ---------- Pandas versions (from the clean order_facts table) ----------

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


# ---------- SQL versions (straight from the raw tables) ----------

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


def compare():
    p = kpis_pandas(load_order_facts())
    s = kpis_sql()
    print(f"{'KPI':<18}{'Pandas':>16}{'SQL':>16}   Match")
    print("-" * 58)
    for key in p:
        match = "YES" if abs(p[key] - s[key]) < 0.01 else "NO"
        print(f"{key:<18}{p[key]:>16,}{s[key]:>16,}   {match}")


if __name__ == "__main__":
    compare()
