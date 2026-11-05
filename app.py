"""Villegas Operations Intelligence - Executive Dashboard."""
import plotly.express as px
import streamlit as st

from src import analytics

st.set_page_config(page_title="Villegas Operations Intelligence", layout="wide")


@st.cache_data
def get_data():
    return analytics.load_order_facts()


df = get_data()
k = analytics.kpis_pandas(df)

st.title("Villegas Operations Intelligence")
st.caption("Executive Dashboard · Olist Brazilian E-Commerce, 2016–2018 · Values in Brazilian reais (R$)")

c1, c2, c3 = st.columns(3)
c1.metric("Revenue", f"R$ {k['revenue']:,.0f}")
c2.metric("Orders", f"{k['orders']:,}")
c3.metric("Average order value", f"R$ {k['avg_order_value']:,.2f}")

c4, c5, c6 = st.columns(3)
c4.metric("Freight cost", f"R$ {k['freight']:,.0f}",
          f"{100 * k['freight'] / k['revenue']:.1f}% of revenue", delta_color="off")
c5.metric("On-time delivery rate", f"{k['on_time_rate']:.1f}%")
c6.metric("Average review score", f"{k['avg_review']:.2f} / 5")

st.subheader("Monthly revenue")
monthly = analytics.monthly_revenue_pandas(df)
fig = px.bar(monthly, x="month", y="revenue",
             labels={"month": "", "revenue": "Revenue (R$)"})
st.plotly_chart(fig)

st.caption("Data: Olist Brazilian E-Commerce Public Dataset (Kaggle), licensed CC BY-NC-SA 4.0.")
