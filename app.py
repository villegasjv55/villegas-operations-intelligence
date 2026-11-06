"""Villegas Operations Intelligence - entry point: branding, page menu, shared style, shared filter."""
import streamlit as st

from src import explain, shared
from src.style import apply_style, page_footer, sidebar_brand

st.set_page_config(page_title="Villegas Operations Intelligence", page_icon="assets/logo_icon.svg",
                   layout="wide")
apply_style()
st.logo("assets/logo.svg", size="large", icon_image="assets/logo_icon.svg")

pages = st.navigation({
    "Overview": [
        st.Page("pages/executive_dashboard.py", title="Executive Dashboard",
                icon=":material/dashboard:", default=True),
        st.Page("pages/findings.py", title="Findings & Recommendations",
                icon=":material/lightbulb:"),
        st.Page("pages/guide.py", title="How It Works", icon=":material/menu_book:"),
    ],
    "Modules": [
        st.Page("pages/sales.py", title="Sales Analytics", icon=":material/storefront:"),
        st.Page("pages/seller_logistics.py", title="Seller & Logistics",
                icon=":material/local_shipping:"),
        st.Page("pages/operations.py", title="Operations Performance",
                icon=":material/pending_actions:"),
        st.Page("pages/reporting.py", title="Reporting Center",
                icon=":material/summarize:"),
    ],
})

shared.sidebar_filters()
sidebar_brand()
explain.how_to_read(pages.title)
pages.run()
page_footer()