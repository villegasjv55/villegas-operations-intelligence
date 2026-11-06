"""Module 03: Seller & Logistics Performance."""
from src.analytics import load_order_facts
from src.database import run_query

# Sellers need at least this many orders to be ranked fairly
MIN_SELLER_ORDERS = 30

STATE_NAMES = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia",
    "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás",
    "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul", "RO": "Rondônia",
    "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo", "SE": "Sergipe",
    "TO": "Tocantins",
}

# One row per item sold, with its seller, its order's delivery results,
# and whether the seller missed the deadline to hand it to the carrier.
ITEM_FACTS_SQL = """
SELECT i.order_id,
       i.order_item_id,
       i.seller_id,
       s.seller_state,
       i.price,
       i.freight_value,
       CASE WHEN o.order_delivered_carrier_date IS NULL THEN NULL
            WHEN o.order_delivered_carrier_date > i.shipping_limit_date THEN 1.0
            ELSE 0.0 END AS missed_handoff,
       f.purchase_month,
       f.customer_state,
       f.is_delivered,
       f.is_late,
       f.handoff_days,
       f.review_score
FROM order_items i
JOIN orders o      ON i.order_id = o.order_id
JOIN order_facts f ON i.order_id = f.order_id
LEFT JOIN sellers s ON i.seller_id = s.seller_id
"""

STATE_CENTERS_SQL = """
SELECT geolocation_state AS customer_state,
       AVG(geolocation_lat) AS lat,
       AVG(geolocation_lng) AS lng
FROM geolocation
WHERE geolocation_lat BETWEEN -34 AND 6
  AND geolocation_lng BETWEEN -74 AND -34
GROUP BY geolocation_state
"""


def load_item_facts():
    return run_query(ITEM_FACTS_SQL)


def state_centers():
    """Map position of each state: the average of its zip-code coordinates inside Brazil."""
    return run_query(STATE_CENTERS_SQL)


def seller_scorecard(items, min_orders=MIN_SELLER_ORDERS):
    """One row per seller, worst late-delivery rate first."""
    item_level = items.groupby("seller_id").agg(
        items_sold=("order_id", "size"),
        revenue=("price", "sum"),
        missed_handoff_rate=("missed_handoff", "mean"),
    )
    per_order = items.drop_duplicates(["seller_id", "order_id"])
    order_level = per_order.groupby("seller_id").agg(
        seller_state=("seller_state", "first"),
        orders=("order_id", "nunique"),
        avg_handoff_days=("handoff_days", "mean"),
        avg_review=("review_score", "mean"),
    )
    delivered = per_order[per_order["is_delivered"] == 1]
    late = delivered.groupby("seller_id")["is_late"].mean().rename("late_rate")

    card = order_level.join(item_level).join(late)
    card["missed_handoff_rate"] *= 100
    card["late_rate"] *= 100
    card = card[card["orders"] >= min_orders]
    return card.reset_index().sort_values("late_rate", ascending=False).round(2)


def state_performance(facts):
    """Delivery results by customer state, slowest first."""
    d = facts[facts["is_delivered"] == 1]
    out = d.groupby("customer_state").agg(
        orders=("order_id", "count"),
        avg_delivery_days=("delivery_days", "mean"),
        late_rate=("is_late", "mean"),
        avg_review=("review_score", "mean"),
    ).reset_index()
    out["late_rate"] *= 100
    out["state_name"] = out["customer_state"].map(STATE_NAMES)
    return out.round(2).sort_values("avg_delivery_days", ascending=False)


def late_rate_colors(rates):
    """Cyan for the lowest late rate, red for the highest, blended in between."""
    lo, hi = rates.min(), rates.max()
    spread = (hi - lo) or 1
    colors = []
    for r in rates:
        t = (r - lo) / spread
        colors.append([int(34 + 205 * t), int(211 - 143 * t), int(238 - 170 * t), 230])
    return colors


# ---------- Plain-English summaries ----------

def seller_insight(card):
    if card.empty:
        return f"Not enough sellers with {MIN_SELLER_ORDERS}+ orders in this selection."
    bottom = card.head(10)
    text = (f"<b>{len(card):,}</b> sellers had {MIN_SELLER_ORDERS}+ orders. The typical (median) "
            f"seller delivers <b>{card['late_rate'].median():.1f}%</b> of orders late, but the "
            f"bottom 10 range from <b>{bottom['late_rate'].min():.1f}%</b> to "
            f"<b>{bottom['late_rate'].max():.1f}%</b>. ")
    slow = card[card["missed_handoff_rate"] > 10]
    fast = card[card["missed_handoff_rate"] <= 10]
    if not slow.empty and not fast.empty:
        gap = slow["late_rate"].mean() - fast["late_rate"].mean()
        text += (f"Sellers who miss the shipping deadline on more than 10% of items deliver "
                 f"<b>{slow['late_rate'].mean():.1f}%</b> of orders late vs "
                 f"<b>{fast['late_rate'].mean():.1f}%</b> for everyone else")
        text += (", so slow handoffs are a real driver of late deliveries."
                 if gap > 2 else ", so handoff speed alone does not explain late deliveries.")
    return text


def state_insight(states):
    if states.empty:
        return "No delivered orders in this selection."
    slow, fast = states.iloc[0], states.iloc[-1]
    big = states.sort_values("orders", ascending=False).iloc[0]
    worst = states.sort_values("late_rate", ascending=False).iloc[0]
    return (f"Customers in <b>{slow['state_name']}</b> wait <b>{slow['avg_delivery_days']:.1f} days</b> "
            f"on average, versus <b>{fast['avg_delivery_days']:.1f}</b> in {fast['state_name']}. "
            f"<b>{big['state_name']}</b>, the biggest market with {big['orders']:,} delivered orders, "
            f"averages {big['avg_delivery_days']:.1f} days and {big['late_rate']:.1f}% late. "
            f"The promised date is missed most often in <b>{worst['state_name']}</b> "
            f"({worst['late_rate']:.1f}% late).")


def main():
    items = load_item_facts()
    print(f"Item rows: {len(items):,}")
    print(f"Missed handoff rate: {100 * items['missed_handoff'].mean():.1f}%")
    card = seller_scorecard(items)
    print(f"\nSellers with {MIN_SELLER_ORDERS}+ orders: {len(card)}")
    print("\nBottom 5 sellers by late rate:")
    cols = ["seller_id", "seller_state", "orders", "late_rate", "missed_handoff_rate", "avg_review"]
    print(card.head(5)[cols].to_string(index=False))
    print("\nSlowest 5 states:")
    print(state_performance(load_order_facts()).head(5).to_string(index=False))


if __name__ == "__main__":
    main()