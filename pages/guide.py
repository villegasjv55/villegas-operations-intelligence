"""How It Works - plain-English guide to the app, the data and every number."""
import pandas as pd
import streamlit as st

from src import analytics, explain, insights, shared
from src.database import run_query
from src.style import hero, insight, kpi_card, section_title


@st.cache_data
def data_at_a_glance():
    return run_query("""
        SELECT
            (SELECT COUNT(DISTINCT customer_unique_id) FROM customers) AS customers,
            (SELECT COUNT(*) FROM sellers)                              AS sellers,
            (SELECT COUNT(*) FROM products)                             AS products,
            (SELECT COUNT(DISTINCT category) FROM products_clean)       AS categories,
            (SELECT COUNT(DISTINCT customer_state) FROM customers)      AS states,
            (SELECT COUNT(*) FROM order_items)                          AS items,
            (SELECT MIN(order_purchase_timestamp) FROM orders)          AS first_order,
            (SELECT MAX(order_purchase_timestamp) FROM orders)          AS last_order
    """).iloc[0]


hero(
    "Villegas Analytics · Operations Intelligence",
    "How It Works",
    "What this app is, what the data contains, and exactly how each number is calculated",
)

facts = shared.order_facts()
k = analytics.kpis_pandas(facts)
glance = data_at_a_glance()
first = pd.to_datetime(glance["first_order"]).strftime("%b %Y")
last = pd.to_datetime(glance["last_order"]).strftime("%b %Y")

section_title("What this app is")
with st.container(border=True, key="card_what"):
    st.markdown(explain.WHAT_IT_IS)

section_title("The data at a glance")
row1 = st.columns(4)
kpi_card(row1[0], "Orders", f"{k['orders']:,}", "Real, anonymized purchases")
kpi_card(row1[1], "Products sold", f"{glance['items']:,}", "Individual items across all orders")
kpi_card(row1[2], "Customers", f"{glance['customers']:,}", "Unique people who bought")
kpi_card(row1[3], "Sellers", f"{glance['sellers']:,}", "Small businesses selling on Olist")
row2 = st.columns(4)
kpi_card(row2[0], "Products", f"{glance['products']:,}", "Different products listed")
kpi_card(row2[1], "Categories", f"{glance['categories']:,}", "Translated to English")
kpi_card(row2[2], "States covered", f"{glance['states']}", "Every state in Brazil")
kpi_card(row2[3], "Time span", f"{first} – {last}", "A fixed historical snapshot")

section_title("Where the data comes from")
with st.container(border=True, key="card_data"):
    st.markdown(explain.THE_DATA)

section_title("The 9 data files and what is in them")
with st.container(border=True, key="card_tables"):
    st.markdown(explain.tables_markdown())

left, right = st.columns(2)
with left:
    section_title("How an order moves")
    with st.container(border=True, key="card_flow"):
        st.markdown(explain.ORDER_FLOW)
with right:
    section_title("The clean tables we built")
    with st.container(border=True, key="card_built"):
        st.markdown(explain.BUILT_TABLES)

section_title("One order, start to finish")
with st.container(border=True, key="card_example"):
    st.markdown(explain.EXAMPLE_ORDER)

section_title("What every number means")
with st.container(border=True, key="card_kpis"):
    st.markdown(explain.kpi_table_markdown())

section_title("The main finding so far")
with st.container(border=True, key="card_finding"):
    insight(insights.delay_insight(analytics.review_by_delay(facts)))

left, right = st.columns(2)
with left:
    section_title("How the numbers are checked")
    with st.container(border=True, key="card_verify"):
        st.markdown(explain.VERIFY)
with right:
    section_title("Using the filters")
    with st.container(border=True, key="card_filters"):
        st.markdown(explain.FILTERS)

section_title("Words used in this app")
with st.container(border=True, key="card_glossary"):
    st.markdown(explain.GLOSSARY)

left, right = st.columns(2)
with left:
    section_title("What the data cannot tell us")
    with st.container(border=True, key="card_limits"):
        st.markdown(explain.LIMITS)
with right:
    section_title("About")
    with st.container(border=True, key="card_about"):
        st.markdown(explain.ABOUT)