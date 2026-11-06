"""Things every page shares: cached data and the sidebar month filter."""
import streamlit as st

from src import analytics, logistics


@st.cache_data
def order_facts():
    return analytics.load_order_facts()


@st.cache_data
def item_facts():
    return logistics.load_item_facts()


@st.cache_data
def state_centers():
    return logistics.state_centers()


def sidebar_filters():
    """Draw the month filter. Called once in app.py so every page shares it."""
    facts = order_facts()
    st.sidebar.header("Filters")
    exclude_thin = st.sidebar.checkbox(
        "Exclude incomplete months",
        value=True,
        help=f"Drops months with fewer than {analytics.MIN_MONTHLY_ORDERS} orders.",
    )
    if exclude_thin:
        months = analytics.complete_months(facts)
    else:
        months = sorted(facts["purchase_month"].unique())
    start, end = st.sidebar.select_slider(
        "Purchase months", options=months, value=(months[0], months[-1])
    )
    st.session_state["start"] = start
    st.session_state["end"] = end
    selected = facts["purchase_month"].between(start, end).sum()
    st.sidebar.caption(f"{selected:,} orders selected")


def selected_months():
    """The (start, end) months chosen in the sidebar."""
    return st.session_state["start"], st.session_state["end"]