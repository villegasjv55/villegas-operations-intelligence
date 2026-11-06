"""How It Works - plain-English guide to the app, the data and every number."""
import streamlit as st

from src import analytics, explain, insights, shared
from src.style import hero, insight, kpi_card, section_title

hero(
    "Villegas Analytics · Operations Intelligence",
    "How It Works",
    "What this app is, where the numbers come from, and exactly how each one is calculated",
)

facts = shared.order_facts()
k = analytics.kpis_pandas(facts)
complete = analytics.complete_months(facts)

row = st.columns(4)
kpi_card(row[0], "Orders analyzed", f"{k['orders']:,}", "Real, anonymized orders")
kpi_card(row[1], "Time span", "2016 – 2018", f"{len(complete)} complete months for trends")
kpi_card(row[2], "Data tables", "9", "Connected in a SQLite database")
kpi_card(row[3], "Verification", "SQL = Pandas", "Key numbers calculated two ways")

section_title("What this app is")
with st.container(border=True, key="card_what"):
    st.markdown(explain.WHAT_IT_IS)

section_title("The main finding so far")
with st.container(border=True, key="card_finding"):
    insight(insights.delay_insight(analytics.review_by_delay(facts)))

left, right = st.columns(2)
with left:
    section_title("Where the data comes from")
    with st.container(border=True, key="card_data"):
        st.markdown(explain.THE_DATA)
with right:
    section_title("How an order moves")
    with st.container(border=True, key="card_flow"):
        st.markdown(explain.ORDER_FLOW)

section_title("What every number means")
with st.container(border=True, key="card_kpis"):
    st.markdown(explain.kpi_table_markdown())

left, right = st.columns(2)
with left:
    section_title("How the numbers are checked")
    with st.container(border=True, key="card_verify"):
        st.markdown(explain.VERIFY)
with right:
    section_title("Using the filters")
    with st.container(border=True, key="card_filters"):
        st.markdown(explain.FILTERS)

left, right = st.columns(2)
with left:
    section_title("What the data cannot tell us")
    with st.container(border=True, key="card_limits"):
        st.markdown(explain.LIMITS)
with right:
    section_title("About")
    with st.container(border=True, key="card_about"):
        st.markdown(explain.ABOUT)