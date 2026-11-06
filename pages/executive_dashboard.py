"""Module 01 - Executive Dashboard."""
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src import analytics, insights, shared
from src.style import (ACCENT, DANGER, WARN, chart_title, hero, insight, kpi_card,
                       section_title, show_table)

start, end = shared.selected_months()
all_data = shared.order_facts()
df = all_data[all_data["purchase_month"].between(start, end)]

# ---------- Header ----------
hero(
    "Villegas Analytics · Operations Intelligence",
    "Executive Dashboard",
    f"Olist marketplace · {insights.fmt_month(start)} to {insights.fmt_month(end)} · "
    f"{len(df):,} orders · values in Brazilian reais (R$)",
)

# ---------- KPI cards ----------
k = analytics.kpis_pandas(df)
row1 = st.columns(3)
kpi_card(row1[0], "Revenue", f"R$ {k['revenue']:,.0f}", "Sum of item prices")
kpi_card(row1[1], "Orders", f"{k['orders']:,}", "Distinct orders placed")
kpi_card(row1[2], "Average order value", f"R$ {k['avg_order_value']:,.2f}", "Revenue ÷ orders with items")

row2 = st.columns(3)
kpi_card(row2[0], "Freight cost", f"R$ {k['freight']:,.0f}",
         f"{100 * k['freight'] / k['revenue']:.1f}% of revenue")
kpi_card(row2[1], "On-time delivery", f"{k['on_time_rate']:.1f}%", "Delivered by the promised date")
kpi_card(row2[2], "Average review", f"{k['avg_review']:.2f} / 5", "Mean customer score")

# ---------- Trends ----------
monthly = analytics.monthly_revenue_pandas(df)
on_time = analytics.monthly_on_time(df)

section_title("Sales and delivery trends")
left, right = st.columns(2)

with left:
    with st.container(border=True, key="card_revenue"):
        chart_title("Monthly revenue")
        peak = monthly["revenue"].idxmax()
        colors = [WARN if i == peak else ACCENT for i in monthly.index]
        fig = go.Figure(go.Bar(
            x=monthly["month"], y=monthly["revenue"], marker_color=colors,
            hovertemplate="%{x|%b %Y}<br>R$ %{y:,.0f}<extra></extra>",
        ))
        fig.update_layout(height=330, barcornerradius=6, yaxis_title="Revenue (R$)")
        st.plotly_chart(fig, theme=None)
        insight(insights.revenue_insight(monthly))

with right:
    with st.container(border=True, key="card_on_time"):
        chart_title("On-time delivery rate by month")
        fig = go.Figure(go.Scatter(
            x=on_time["month"], y=on_time["on_time_rate"], mode="lines+markers",
            line=dict(color=ACCENT, width=3, shape="spline"), marker=dict(size=7),
            fill="tozeroy", fillcolor="rgba(34, 211, 238, 0.10)",
            hovertemplate="%{x|%b %Y}<br>%{y:.1f}% on time<extra></extra>",
        ))
        low = max(0, on_time["on_time_rate"].min() - 10) if not on_time.empty else 0
        fig.update_layout(height=330, yaxis=dict(range=[low, 100], title="On-time rate (%)"))
        st.plotly_chart(fig, theme=None)
        insight(insights.on_time_insight(on_time, monthly))

# ---------- Headline finding ----------
section_title("Late deliveries vs. customer satisfaction")
delay = analytics.review_by_delay(df)

chart_col, detail_col = st.columns([3, 2])
with chart_col:
    with st.container(border=True, key="card_delay"):
        chart_title("Average review score by how late the order arrived")
        group_colors = {
            "On time": ACCENT,
            "1-3 days late": WARN,
            "4-7 days late": "#FB923C",
            "8-14 days late": DANGER,
            "15+ days late": "#EF4444",
        }
        fig = px.bar(
            delay, x="delay_group", y="avg_review", text="avg_review",
            color="delay_group", color_discrete_map=group_colors, range_y=[0, 5],
            labels={"delay_group": "", "avg_review": "Average review (1-5)"},
        )
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside",
                          hovertemplate="%{x}<br>%{y:.2f} stars<extra></extra>")
        fig.update_layout(height=380, showlegend=False, barcornerradius=10)
        st.plotly_chart(fig, theme=None)

with detail_col:
    with st.container(border=True, key="card_delay_detail"):
        chart_title("The numbers behind it")
        insight(insights.delay_insight(delay))
        show_table(
            delay.rename(columns={
                "delay_group": "Delivery",
                "orders": "Orders",
                "avg_review": "Avg review",
                "detractor_rate": "% 1-2 stars",
            }),
            hide_index=True,
        )

st.caption("Data: Olist Brazilian E-Commerce Public Dataset (Kaggle), licensed CC BY-NC-SA 4.0.")