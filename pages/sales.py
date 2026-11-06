"""Module 02 - Sales Analytics."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src import insights, sales, shared
from src.style import (ACCENT, ACCENT_2, WARN, chart_title, hero, insight, kpi_card,
                       section_title, show_table)


@st.cache_data
def get_item_sales():
    return sales.load_item_sales()


@st.cache_data
def get_payments():
    return sales.load_payments()


start, end = shared.selected_months()
facts_all = shared.order_facts()
items_all = get_item_sales()
payments_all = get_payments()
facts = facts_all[facts_all["purchase_month"].between(start, end)]
items = items_all[items_all["purchase_month"].between(start, end)]
payments = payments_all[payments_all["purchase_month"].between(start, end)]

hero(
    "Villegas Analytics · Operations Intelligence",
    "Sales Analytics",
    f"What sells, where, how customers pay, and whether busy months hurt delivery · "
    f"{insights.fmt_month(start)} to {insights.fmt_month(end)}",
)

cats = sales.category_performance(items)
states = sales.state_sales(facts)
mix = sales.payment_mix(payments)
plans = sales.installment_plans(payments)

# ---------- KPI cards ----------
row = st.columns(4)
if not cats.empty:
    kpi_card(row[0], "Top category", cats.iloc[0]["category"],
             f"{cats.iloc[0]['revenue_share']:.1f}% of revenue")
    kpi_card(row[1], "Top 10 categories", f"{cats.head(10)['revenue_share'].sum():.0f}%",
             f"of revenue, out of {len(cats)} categories")
if not mix.empty:
    kpi_card(row[2], mix.iloc[0]["payment"], f"{mix.iloc[0]['value_share']:.0f}%",
             "of all money paid")
kpi_card(row[3], "Repeat customers", f"{sales.repeat_customer_rate(facts):.1f}%",
         "Customers who ordered 2+ times")

# ---------- What sells ----------
section_title("What sells")
with st.container(border=True, key="card_categories"):
    chart_title("Top 10 categories by revenue")
    top10 = cats.head(10).sort_values("revenue")
    fig = px.bar(top10, x="revenue", y="category", orientation="h", text="revenue_share",
                 labels={"revenue": "Revenue (R$)", "category": ""})
    fig.update_traces(marker_color=ACCENT, texttemplate="%{text:.1f}%", textposition="outside",
                      hovertemplate="%{y}<br>R$ %{x:,.0f}<extra></extra>")
    fig.update_layout(height=420, barcornerradius=6)
    st.plotly_chart(fig, theme=None)
    insight(sales.category_insight(cats))
    with st.expander("See every category"):
        show_table(cats[["category", "orders", "items_sold", "revenue", "revenue_share",
                         "avg_price", "freight_pct", "avg_review", "late_rate"]].rename(columns={
            "category": "Category", "orders": "Orders", "items_sold": "Items sold",
            "revenue": "Revenue (R$)", "revenue_share": "% of revenue",
            "avg_price": "Avg price (R$)", "freight_pct": "% shipping cost",
            "avg_review": "Avg review", "late_rate": "% late",
        }), height=400)

# ---------- Where customers are ----------
section_title("Where customers are")
state_col, state_table_col = st.columns([3, 2])
with state_col:
    with st.container(border=True, key="card_state_sales"):
        chart_title("Top 10 states by revenue")
        top_states = states.head(10).sort_values("revenue")
        fig = px.bar(top_states, x="revenue", y="state_name", orientation="h",
                     text="revenue_share", labels={"revenue": "Revenue (R$)", "state_name": ""})
        fig.update_traces(marker_color=ACCENT_2, texttemplate="%{text:.1f}%",
                          textposition="outside",
                          hovertemplate="%{y}<br>R$ %{x:,.0f}<extra></extra>")
        fig.update_layout(height=400, barcornerradius=6)
        st.plotly_chart(fig, theme=None)
with state_table_col:
    with st.container(border=True, key="card_state_table"):
        chart_title("Sales by state")
        insight(sales.state_insight(states))
        show_table(states[["state_name", "orders", "revenue", "revenue_share",
                           "avg_order_value"]].rename(columns={
            "state_name": "State", "orders": "Orders", "revenue": "Revenue (R$)",
            "revenue_share": "% of revenue", "avg_order_value": "Avg order (R$)",
        }), height=260)

# ---------- How customers pay ----------
section_title("How customers pay")
pay_col, plan_col = st.columns(2)
with pay_col:
    with st.container(border=True, key="card_payments"):
        chart_title("Share of money paid, by payment method")
        fig = px.bar(mix.sort_values("value_share"), x="value_share", y="payment",
                     orientation="h", text="value_share",
                     labels={"value_share": "% of money paid", "payment": ""})
        fig.update_traces(marker_color=ACCENT, texttemplate="%{text:.1f}%",
                          textposition="outside")
        fig.update_layout(height=300, barcornerradius=6, xaxis=dict(range=[0, 100]))
        st.plotly_chart(fig, theme=None)
with plan_col:
    with st.container(border=True, key="card_installments"):
        chart_title("Credit card payments by number of installments")
        fig = px.bar(plans, x="plan", y="share", text="avg_value",
                     labels={"plan": "Installments", "share": "% of credit card payments"})
        fig.update_traces(marker_color=ACCENT_2, texttemplate="avg R$ %{text:,.0f}",
                          textposition="outside")
        fig.update_layout(height=300, barcornerradius=6)
        st.plotly_chart(fig, theme=None)
insight(sales.payment_insight(mix, plans))

# ---------- Peaks vs delays ----------
section_title("Do sales peaks cause delays?")
with st.container(border=True, key="card_peaks"):
    chart_title("Each dot is one month: order volume vs. on-time delivery")
    peaks = sales.peak_vs_delay(facts)
    labels = [pd.to_datetime(m).strftime("%b %y") for m in peaks["month"]]
    fig = go.Figure(go.Scatter(
        x=peaks["orders"], y=peaks["on_time_rate"], mode="markers+text", text=labels,
        textposition="top center", textfont=dict(size=10, color="#8FA3BF"),
        marker=dict(size=12, color=ACCENT, line=dict(width=0)),
        hovertemplate="%{text}<br>%{x:,} orders<br>%{y:.1f}% on time<extra></extra>",
    ))
    if len(peaks) >= 3:
        slope, intercept = np.polyfit(peaks["orders"], peaks["on_time_rate"], 1)
        xs = np.array([peaks["orders"].min(), peaks["orders"].max()])
        fig.add_trace(go.Scatter(x=xs, y=slope * xs + intercept, mode="lines",
                                 line=dict(color=WARN, width=2, dash="dash"),
                                 hoverinfo="skip"))
    fig.update_layout(height=420, showlegend=False,
                      xaxis_title="Orders placed that month",
                      yaxis_title="On-time delivery rate (%)")
    st.plotly_chart(fig, theme=None)
    st.caption("Dashed amber line = overall trend.")
    insight(sales.peak_insight(peaks))

st.caption("Data: Olist Brazilian E-Commerce Public Dataset (Kaggle), licensed CC BY-NC-SA 4.0.")