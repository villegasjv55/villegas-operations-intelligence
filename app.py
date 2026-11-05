"""Villegas Operations Intelligence - Executive Dashboard."""
import plotly.express as px
import streamlit as st

from src import analytics

st.set_page_config(page_title="Villegas Operations Intelligence", layout="wide")


@st.cache_data
def get_data():
    return analytics.load_order_facts()


all_data = get_data()

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
exclude_thin = st.sidebar.checkbox(
    "Exclude incomplete months",
    value=True,
    help=f"Drops months with fewer than {analytics.MIN_MONTHLY_ORDERS} orders.",
)
if exclude_thin:
    months = analytics.complete_months(all_data)
else:
    months = sorted(all_data["purchase_month"].unique())

start, end = st.sidebar.select_slider(
    "Purchase months", options=months, value=(months[0], months[-1])
)
df = all_data[all_data["purchase_month"].between(start, end)]
st.sidebar.caption(f"{len(df):,} orders selected")

# ---------- Header and KPIs ----------
st.title("Villegas Operations Intelligence")
st.caption(f"Executive Dashboard · Olist orders {start} to {end} · Values in Brazilian reais (R$)")

k = analytics.kpis_pandas(df)
c1, c2, c3 = st.columns(3)
c1.metric("Revenue", f"R$ {k['revenue']:,.0f}")
c2.metric("Orders", f"{k['orders']:,}")
c3.metric("Average order value", f"R$ {k['avg_order_value']:,.2f}")

c4, c5, c6 = st.columns(3)
c4.metric("Freight cost", f"R$ {k['freight']:,.0f}",
          f"{100 * k['freight'] / k['revenue']:.1f}% of revenue", delta_color="off")
c5.metric("On-time delivery rate", f"{k['on_time_rate']:.1f}%")
c6.metric("Average review score", f"{k['avg_review']:.2f} / 5")

# ---------- Trends ----------
left, right = st.columns(2)
with left:
    st.subheader("Monthly revenue")
    fig = px.bar(analytics.monthly_revenue_pandas(df), x="month", y="revenue",
                 labels={"month": "", "revenue": "Revenue (R$)"})
    st.plotly_chart(fig)
with right:
    st.subheader("On-time delivery rate by month")
    fig = px.line(analytics.monthly_on_time(df), x="month", y="on_time_rate",
                  markers=True, labels={"month": "", "on_time_rate": "On-time rate (%)"})
    st.plotly_chart(fig)

# ---------- Headline finding ----------
st.divider()
st.subheader("Late deliveries vs. customer satisfaction")

delay = analytics.review_by_delay(df)
on_time_score = delay.loc[delay["delay_group"] == "On time", "avg_review"].iloc[0]
worst = delay.iloc[-1]
st.markdown(
    f"On-time orders average **{on_time_score:.2f} stars**. "
    f"Orders {str(worst['delay_group']).lower()} average **{worst['avg_review']:.2f} stars**."
)

fig = px.bar(delay, x="delay_group", y="avg_review", text="avg_review",
             range_y=[0, 5],
             labels={"delay_group": "", "avg_review": "Average review score (1-5)"})
st.plotly_chart(fig)

st.dataframe(
    delay.rename(columns={
        "delay_group": "Delivery",
        "orders": "Orders",
        "avg_review": "Avg review",
        "detractor_rate": "% 1-2 star reviews",
    }),
    hide_index=True,
)

st.caption("Data: Olist Brazilian E-Commerce Public Dataset (Kaggle), licensed CC BY-NC-SA 4.0.")