"""Module 02: Sales Analytics - categories, states, payments, peaks, repeat customers."""
import pandas as pd

from src.database import run_query
from src.logistics import STATE_NAMES

PAYMENT_LABELS = {
    "credit_card": "Credit card",
    "boleto": "Boleto (bank slip)",
    "voucher": "Voucher",
    "debit_card": "Debit card",
}

# One row per item sold, with its English category and its order's results
ITEM_SALES_SQL = """
SELECT i.order_id,
       i.price,
       i.freight_value,
       p.category,
       f.purchase_month,
       f.customer_state,
       f.is_delivered,
       f.is_late,
       f.review_score
FROM order_items i
JOIN products_clean p ON i.product_id = p.product_id
JOIN order_facts f    ON i.order_id = f.order_id
"""

# One row per payment, with its order's month
PAYMENTS_SQL = """
SELECT pay.order_id,
       pay.payment_type,
       pay.payment_installments,
       pay.payment_value,
       f.purchase_month
FROM payments pay
JOIN order_facts f ON pay.order_id = f.order_id
WHERE pay.payment_type <> 'not_defined'
"""


def load_item_sales():
    return run_query(ITEM_SALES_SQL)


def load_payments():
    return run_query(PAYMENTS_SQL)


def pretty_category(name):
    """'bed_bath_table' -> 'Bed bath table'"""
    return str(name).replace("_", " ").capitalize()


def category_performance(items):
    """One row per category, biggest revenue first."""
    item_level = items.groupby("category").agg(
        items_sold=("order_id", "size"),
        revenue=("price", "sum"),
        freight=("freight_value", "sum"),
        avg_price=("price", "mean"),
    )
    per_order = items.drop_duplicates(["category", "order_id"])
    order_level = per_order.groupby("category").agg(
        orders=("order_id", "nunique"),
        avg_review=("review_score", "mean"),
    )
    delivered = per_order[per_order["is_delivered"] == 1]
    late = delivered.groupby("category")["is_late"].mean().rename("late_rate")

    out = item_level.join(order_level).join(late)
    out["late_rate"] *= 100
    out["freight_pct"] = 100 * out["freight"] / out["revenue"]
    out["revenue_share"] = 100 * out["revenue"] / out["revenue"].sum()
    out = out.reset_index()
    out["category"] = out["category"].map(pretty_category)
    return out.sort_values("revenue", ascending=False).round(2)


def state_sales(facts):
    """Revenue and orders by customer state, biggest first."""
    out = facts.groupby("customer_state").agg(
        orders=("order_id", "nunique"),
        revenue=("revenue", "sum"),
    ).reset_index()
    out["avg_order_value"] = out["revenue"] / out["orders"]
    out["revenue_share"] = 100 * out["revenue"] / out["revenue"].sum()
    out["state_name"] = out["customer_state"].map(STATE_NAMES)
    return out.sort_values("revenue", ascending=False).round(2)


def payment_mix(payments):
    out = payments.groupby("payment_type").agg(
        orders=("order_id", "nunique"),
        value=("payment_value", "sum"),
    ).reset_index()
    out["value_share"] = 100 * out["value"] / out["value"].sum()
    out["payment"] = out["payment_type"].map(PAYMENT_LABELS).fillna(out["payment_type"])
    return out.sort_values("value", ascending=False).round(2)


def installment_plans(payments):
    """How credit card payments are split: paid in full vs. installments."""
    cc = payments[payments["payment_type"] == "credit_card"].copy()
    cc["plan"] = pd.cut(
        cc["payment_installments"],
        bins=[-1, 1, 3, 6, 10, 100],
        labels=["1 (paid in full)", "2-3", "4-6", "7-10", "11+"],
    )
    out = cc.groupby("plan", observed=True).agg(
        payments=("order_id", "size"),
        avg_value=("payment_value", "mean"),
    ).reset_index()
    out["share"] = 100 * out["payments"] / out["payments"].sum()
    return out.round(2)


def repeat_customer_rate(facts):
    """% of unique customers who placed 2 or more orders."""
    orders_per_customer = facts.groupby("customer_unique_id")["order_id"].nunique()
    if orders_per_customer.empty:
        return 0.0
    return 100 * (orders_per_customer >= 2).mean()


def peak_vs_delay(facts):
    """Each month's order volume next to its on-time delivery rate."""
    from src.analytics import monthly_on_time

    volume = facts.groupby("purchase_month")["order_id"].nunique().rename("orders")
    on_time = monthly_on_time(facts).set_index("month")
    out = on_time.join(volume, how="inner").reset_index()
    return out.rename(columns={"index": "month"})


# ---------- Plain-English summaries ----------

def category_insight(cats):
    if cats.empty:
        return "No sales in this selection."
    top = cats.iloc[0]
    top10_share = cats.head(10)["revenue_share"].sum()
    big = cats[cats["orders"] >= 200]
    text = (f"<b>{top['category']}</b> is the biggest category with <b>{top['revenue_share']:.1f}%</b> "
            f"of revenue. The top 10 categories bring in <b>{top10_share:.0f}%</b> of all revenue. ")
    if not big.empty:
        worst = big.sort_values("avg_review").iloc[0]
        costly = big.sort_values("freight_pct", ascending=False).iloc[0]
        text += (f"Among categories with 200+ orders, <b>{worst['category']}</b> has the lowest reviews "
                 f"({worst['avg_review']:.2f}★), and <b>{costly['category']}</b> has the highest "
                 f"shipping cost at <b>{costly['freight_pct']:.0f}%</b> of the product price.")
    return text


def state_insight(states):
    if states.empty:
        return "No sales in this selection."
    top = states.iloc[0]
    top3 = states.head(3)
    return (f"<b>{top['state_name']}</b> alone brings in <b>{top['revenue_share']:.0f}%</b> of revenue. "
            f"The top three states ({', '.join(top3['state_name'])}) make up "
            f"<b>{top3['revenue_share'].sum():.0f}%</b>. Sales are concentrated in the southeast, "
            f"the same region where deliveries are fastest.")


def payment_insight(mix, plans):
    if mix.empty:
        return "No payments in this selection."
    top = mix.iloc[0]
    text = f"<b>{top['payment']}</b> accounts for <b>{top['value_share']:.0f}%</b> of all money paid. "
    if not plans.empty:
        full = plans[plans["plan"] == "1 (paid in full)"]
        split_share = 100 - (full["share"].iloc[0] if not full.empty else 0)
        text += f"<b>{split_share:.0f}%</b> of credit card payments are split into installments"
        if len(plans) >= 2:
            first, last = plans.iloc[0], plans.iloc[-1]
            text += (f", and bigger purchases get split more: the average payment is "
                     f"R$ {first['avg_value']:,.0f} when paid in full vs R$ {last['avg_value']:,.0f} "
                     f"with {last['plan']} installments.")
        else:
            text += "."
    return text


def peak_insight(peaks):
    if len(peaks) < 3:
        return "Pick at least 3 months to compare busy and quiet months."
    r = peaks["orders"].corr(peaks["on_time_rate"])
    busiest = peaks.sort_values("orders", ascending=False).iloc[0]
    month = pd.to_datetime(busiest["month"]).strftime("%b %Y")
    text = (f"The busiest month was <b>{month}</b> with <b>{busiest['orders']:,}</b> orders and "
            f"<b>{busiest['on_time_rate']:.1f}%</b> on time. ")
    if r <= -0.3:
        text += (f"Across all months, <b>busier months tend to have worse on-time delivery</b> "
                 f"(correlation {r:.2f}), so carrier capacity should be planned ahead of peak season.")
    elif r >= 0.3:
        text += (f"Across all months, busier months actually had <b>better</b> on-time delivery "
                 f"(correlation {r:.2f}), so volume alone does not explain the delays.")
    else:
        text += (f"Across all months there is <b>no strong link</b> between volume and on-time delivery "
                 f"(correlation {r:.2f}). Delays come mostly from other causes, such as specific sellers "
                 f"and regions.")
    return text


def main():
    from src.analytics import load_order_facts

    items, payments, facts = load_item_sales(), load_payments(), load_order_facts()
    print("Top 5 categories by revenue:")
    cols = ["category", "orders", "revenue", "revenue_share", "avg_review", "late_rate"]
    print(category_performance(items).head(5)[cols].to_string(index=False))
    print("\nPayment mix:")
    print(payment_mix(payments)[["payment", "orders", "value_share"]].to_string(index=False))
    print(f"\nRepeat customer rate: {repeat_customer_rate(facts):.2f}%")


if __name__ == "__main__":
    main()
    