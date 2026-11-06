"""Module 04: Operations Performance - order flow, fulfillment stages, cancellations, exceptions."""
import pandas as pd

from src.database import run_query

# Statuses where an order is finished, one way or another
CLOSED_STATUSES = {"delivered", "canceled", "unavailable"}

# One row per order, with the time spent in each stage of fulfillment (in days)
OPS_SQL = """
SELECT o.order_id,
       o.order_status,
       f.purchase_month,
       f.customer_state,
       f.is_delivered,
       f.is_late,
       f.days_late,
       f.has_date_issue,
       f.review_score,
       f.revenue,
       o.order_purchase_timestamp      AS purchased_at,
       o.order_estimated_delivery_date AS promised_date,
       o.order_delivered_customer_date AS delivered_at,
       julianday(o.order_approved_at) - julianday(o.order_purchase_timestamp)
           AS approval_days,
       julianday(o.order_delivered_carrier_date) - julianday(o.order_approved_at)
           AS handoff_days,
       julianday(o.order_delivered_customer_date) - julianday(o.order_delivered_carrier_date)
           AS transit_days
FROM orders o
JOIN order_facts f ON o.order_id = f.order_id
"""


def load_ops():
    ops = run_query(OPS_SQL)
    for col in ["purchased_at", "promised_date", "delivered_at"]:
        ops[col] = pd.to_datetime(ops[col])
    return ops


def snapshot_date():
    """The day the data was frozen: the last purchase in the dataset."""
    last = run_query("SELECT MAX(order_purchase_timestamp) FROM orders").iloc[0, 0]
    return pd.to_datetime(last).normalize()


def clean_delivered(ops):
    """Delivered orders whose stage times are all present and make sense."""
    d = ops[(ops["is_delivered"] == 1) & (ops["has_date_issue"] == 0)]
    d = d.dropna(subset=["approval_days", "handoff_days", "transit_days"])
    return d[(d["approval_days"] >= 0) & (d["handoff_days"] >= 0) & (d["transit_days"] >= 0)]


def overdue_orders(ops, snapshot):
    """Orders that never arrived and whose promised date has already passed."""
    still_open = ~ops["order_status"].isin(CLOSED_STATUSES)
    return ops[still_open & (ops["promised_date"] < snapshot)]


def ops_kpis(ops, snapshot):
    total = len(ops)
    canceled = ops["order_status"].isin(["canceled", "unavailable"]).sum()
    clean = clean_delivered(ops)
    return {
        "late_delivered": int(ops["is_late"].sum()),
        "overdue": len(overdue_orders(ops, snapshot)),
        "cancel_rate": 100 * canceled / total if total else 0,
        "approval_hours": 24 * clean["approval_days"].mean(),
        "handoff_days": clean["handoff_days"].mean(),
        "transit_days": clean["transit_days"].mean(),
    }


def status_breakdown(ops):
    out = ops["order_status"].value_counts().rename_axis("status").reset_index(name="orders")
    out["share"] = (100 * out["orders"] / out["orders"].sum()).round(2)
    return out


def stage_comparison(ops):
    """Average days in each stage, for on-time vs. late orders."""
    stages = {
        "approval_days": "Payment approval",
        "handoff_days": "Seller handoff",
        "transit_days": "Carrier transit",
    }
    d = clean_delivered(ops)
    grouped = d.groupby("is_late")[list(stages)].mean()
    grouped.index = grouped.index.map({0: "On time", 1: "Late"})
    out = grouped.reset_index().melt(id_vars="is_late", var_name="stage", value_name="days")
    out["stage"] = out["stage"].map(stages)
    return out.rename(columns={"is_late": "delivery"}).round(2)


def exception_list(ops, snapshot):
    """Every order that needs follow-up: delivered late, or never delivered and overdue."""
    late = ops[ops["is_late"] == 1].copy()
    late["issue"] = "Delivered late"
    late["days_over"] = late["days_late"]

    overdue = overdue_orders(ops, snapshot).copy()
    overdue["issue"] = "Never delivered, past promised date"
    overdue["days_over"] = (snapshot - overdue["promised_date"]).dt.days

    cols = ["order_id", "issue", "order_status", "customer_state", "purchased_at",
            "promised_date", "delivered_at", "days_over", "review_score", "revenue"]
    out = pd.concat([late, overdue])[cols]
    return out.sort_values("days_over", ascending=False)


# ---------- Plain-English summaries ----------

def stage_insight(comparison):
    pivot = comparison.pivot(index="stage", columns="delivery", values="days")
    if not {"On time", "Late"}.issubset(pivot.columns):
        return "Not enough late and on-time orders in this selection to compare."
    pivot["extra"] = pivot["Late"] - pivot["On time"]
    worst = pivot["extra"].idxmax()
    total_extra = pivot["extra"].sum()
    share = 100 * pivot.loc[worst, "extra"] / total_extra if total_extra > 0 else 0
    return (f"Late orders spend <b>{total_extra:.1f} extra days</b> in fulfillment compared with "
            f"on-time orders. Most of that time is lost in <b>{worst.lower()}</b>: "
            f"{pivot.loc[worst, 'Late']:.1f} days vs {pivot.loc[worst, 'On time']:.1f} for on-time "
            f"orders, or <b>{share:.0f}%</b> of the extra time. That is the stage to fix first.")


def status_insight(status, kpis):
    delivered = status.loc[status["status"] == "delivered", "share"]
    delivered_share = delivered.iloc[0] if not delivered.empty else 0
    text = (f"<b>{delivered_share:.1f}%</b> of orders were delivered. "
            f"<b>{kpis['cancel_rate']:.1f}%</b> were canceled or unavailable. ")
    if kpis["overdue"]:
        text += (f"<b>{kpis['overdue']:,}</b> orders never arrived even though their promised date "
                 f"has passed. Those customers are the most at risk of never buying again.")
    return text


def exceptions_insight(exceptions):
    if exceptions.empty:
        return "No late or overdue orders in this selection."
    late = exceptions[exceptions["issue"] == "Delivered late"]
    overdue = exceptions[exceptions["issue"] != "Delivered late"]
    by_state = exceptions["customer_state"].value_counts()
    text = (f"<b>{len(exceptions):,}</b> orders need follow-up: <b>{len(late):,}</b> arrived late "
            f"and <b>{len(overdue):,}</b> never arrived. ")
    if not late.empty:
        text += f"Half of the late orders were at least <b>{late['days_over'].median():.0f} days</b> late. "
    text += (f"<b>{by_state.index[0]}</b> has the most exceptions by count "
             f"({by_state.iloc[0]:,}, {100 * by_state.iloc[0] / len(exceptions):.0f}% of the list).")
    return text


def main():
    ops = load_ops()
    snap = snapshot_date()
    print(f"Data snapshot date: {snap.date()}\n")
    for key, value in ops_kpis(ops, snap).items():
        print(f"{key:<16}{value:>12,.2f}")
    print("\nAverage days per stage:")
    print(stage_comparison(ops).to_string(index=False))
    print(f"\nOrders on the exception list: {len(exception_list(ops, snap)):,}")


if __name__ == "__main__":
    main()