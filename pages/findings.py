"""Findings & Recommendations."""
import streamlit as st

from src import findings, insights, operations, sales, shared
from src.style import hero, insight, kpi_card, section_title


@st.cache_data
def get_ops():
    return operations.load_ops()


start, end = shared.selected_months()
facts_all = shared.order_facts()
items_all = shared.item_facts()
ops_all = get_ops()
facts = facts_all[facts_all["purchase_month"].between(start, end)]
items = items_all[items_all["purchase_month"].between(start, end)]
ops = ops_all[ops_all["purchase_month"].between(start, end)]

hero(
    "Villegas Analytics · Operations Intelligence",
    "Findings & Recommendations",
    f"Three actions the data supports, with the numbers behind them · "
    f"{insights.fmt_month(start)} to {insights.fmt_month(end)}",
)

r = findings.review_impact(facts, ops)
s = findings.seller_impact(items)
g = findings.state_impact(facts, ops)
repeat = sales.repeat_customer_rate(facts)

if r is None or s is None or g is None:
    st.warning("Not enough data in the selected months. Widen the month range in the sidebar.")
    st.stop()

# ---------- Summary ----------
row = st.columns(4)
kpi_card(row[0], "Late deliveries", f"{r['late_share']:.1f}%", "of delivered, reviewed orders")
kpi_card(row[1], "…but cause", f"{r['late_detractor_share']:.0f}%", "of all 1-2 star reviews")
kpi_card(row[2], "Avoidable bad reviews", f"{r['avoidable']:,.0f}",
         f"{r['avoidable_share']:.0f}% of all 1-2 star reviews")
kpi_card(row[3], "Repeat customers", f"{repeat:.1f}%", "so every unhappy customer counts")

insight(
    f"<b>The core problem:</b> late deliveries are a small share of orders but a large share of "
    f"unhappy customers. On-time orders average <b>{r['on_time_review']:.2f}★</b>; late orders "
    f"average <b>{r['late_review']:.2f}★</b>. With only <b>{repeat:.1f}%</b> of customers ever "
    f"ordering again, a bad first delivery is very likely the last one."
)


def recommendation(number, title, found, actions, impact, key):
    with st.container(border=True, key=key):
        st.markdown(f"### {number}. {title}")
        left, right = st.columns([3, 2])
        with left:
            st.markdown("**What we found**")
            st.markdown(found)
            st.markdown("**What to do**")
            st.markdown(actions)
        with right:
            insight(f"<b>Expected impact</b><br>{impact}")


# ---------- Recommendation 1 ----------
section_title("Recommendations")
stage_text = ""
if r["stage"]:
    stage_text = (f"\n- Most of the extra time is lost in **{r['stage'].lower()}**: "
                  f"{r['stage_late']:.1f} days for late orders vs {r['stage_on_time']:.1f} for "
                  f"on-time orders ({r['stage_share']:.0f}% of the extra time).")
recommendation(
    1, "Catch at-risk orders before they become late",
    f"- Late orders are **{r['late_share']:.1f}%** of reviewed deliveries but cause "
    f"**{r['late_detractor_share']:.0f}%** of all 1-2 star reviews.\n"
    f"- Average review: **{r['on_time_review']:.2f}★** on time vs **{r['late_review']:.2f}★** late."
    f"{stage_text}",
    "- Flag any order that misses its seller handoff deadline or is still in transit close to its "
    "promised date.\n"
    "- Message those customers **before** the promised date with an honest update, and offer a "
    "small voucher if the order will be late.\n"
    "- Review carrier contracts on the slowest routes, since carrier transit is where late orders "
    "lose the most time.",
    f"If late orders were rated like on-time orders, about <b>{r['avoidable']:,.0f}</b> fewer "
    f"1-2 star reviews, or <b>{r['avoidable_share']:.0f}%</b> of all bad reviews in this period.",
    "card_rec1",
)

# ---------- Recommendation 2 ----------
recommendation(
    2, "Put sellers who miss shipping deadlines on a performance plan",
    f"- **{s['flagged']}** of {s['ranked']} ranked sellers miss their shipping deadline on more than "
    f"{s['threshold']}% of items. They handle **{s['flagged_order_share']:.0f}%** of ranked "
    f"sellers' orders.\n"
    f"- Their late-delivery rate is **{s['flagged_late']:.1f}%** vs **{s['rest_late']:.1f}%** for "
    f"everyone else.",
    "- Send every seller a weekly scorecard: missed handoff rate, late rate and reviews.\n"
    "- Give sellers above the threshold 30 days to improve, with support on packing and pickup "
    "scheduling.\n"
    "- If they don't improve, limit their listings in distant states, where delays hurt most.",
    f"If these sellers delivered on time as often as everyone else, about "
    f"<b>{s['avoided']:,.0f}</b> late deliveries would be avoided in this period.",
    "card_rec2",
)

# ---------- Recommendation 3 ----------
worst_list = ", ".join(f"{name} ({rate:.1f}%)" for name, rate in zip(g["worst_names"], g["worst_rates"]))
recommendation(
    3, "Fix promised delivery dates where they are missed most",
    f"- The national late rate is **{g['national']:.1f}%**, but five states are far above it: "
    f"{worst_list}.\n"
    f"- Elsewhere, promised dates are padded: on-time orders arrive on average "
    f"**{g['avg_days_early']:.0f} days early**.",
    "- Recalculate promised dates by region using actual delivery times, adding buffer where dates "
    "are missed and trimming it where orders arrive far too early.\n"
    "- Review the carriers serving those five states and compare alternatives.\n"
    "- Track the late rate for those states monthly to confirm the change works.",
    f"Bringing those five states down to the national late rate would avoid about "
    f"<b>{g['avoided']:,.0f}</b> late deliveries across {g['worst_orders']:,} orders.",
    "card_rec3",
)

section_title("How these estimates were made")
st.markdown(
    "- Every number on this page is calculated live from the same verified tables as the rest of "
    "the app, and updates with the month filter.\n"
    "- **Impact estimates are opportunities, not guarantees.** Each one asks: *what if the problem "
    "group performed like the comparison group?* A real team would test each change on a small "
    "group first.\n"
    "- These results show strong patterns (correlation). Confirming exact causes would need data "
    "Olist did not publish, such as carrier names and warehouse records."
)