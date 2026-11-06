"""Module 04 - Operations Performance."""
import plotly.express as px
import streamlit as st

from src import insights, operations, shared
from src.style import (ACCENT, DANGER, WARN, chart_title, hero, insight, kpi_card,
                       section_title, show_table)


@st.cache_data
def get_ops():
    return operations.load_ops()


@st.cache_data
def get_snapshot():
    return operations.snapshot_date()


start, end = shared.selected_months()
ops_all = get_ops()
snapshot = get_snapshot()
ops = ops_all[ops_all["purchase_month"].between(start, end)]

hero(
    "Villegas Analytics · Operations Intelligence",
    "Operations Performance",
    f"Where orders get stuck and which ones need follow-up · "
    f"{insights.fmt_month(start)} to {insights.fmt_month(end)} · "
    f"data frozen on {snapshot:%b %d, %Y}",
)

k = operations.ops_kpis(ops, snapshot)
row = st.columns(4)
kpi_card(row[0], "Late deliveries", f"{k['late_delivered']:,}", "Arrived after the promised date")
kpi_card(row[1], "Never delivered", f"{k['overdue']:,}", "Past promised date, never arrived")
kpi_card(row[2], "Cancellation rate", f"{k['cancel_rate']:.2f}%", "Canceled or unavailable")
kpi_card(row[3], "Avg carrier transit", f"{k['transit_days']:.1f} days",
         f"Approval {k['approval_hours']:.0f} h · handoff {k['handoff_days']:.1f} d")

# ---------- Where the time goes ----------
section_title("Where the time goes")
stage_col, status_col = st.columns([3, 2])

with stage_col:
    with st.container(border=True, key="card_stages"):
        chart_title("Average days per fulfillment stage: on-time vs. late orders")
        comparison = operations.stage_comparison(ops)
        fig = px.bar(
            comparison, x="days", y="stage", color="delivery", barmode="group",
            orientation="h", text="days",
            color_discrete_map={"On time": ACCENT, "Late": DANGER},
            category_orders={"stage": ["Payment approval", "Seller handoff", "Carrier transit"],
                             "delivery": ["On time", "Late"]},
            labels={"days": "Average days", "stage": "", "delivery": ""},
        )
        fig.update_traces(texttemplate="%{text:.1f} d", textposition="outside")
        fig.update_layout(height=340, barcornerradius=6,
                          legend=dict(orientation="h", y=1.12, x=0))
        st.plotly_chart(fig, theme=None)
        insight(operations.stage_insight(comparison))

with status_col:
    with st.container(border=True, key="card_status"):
        chart_title("Orders that did not complete")
        status = operations.status_breakdown(ops)
        not_done = status[status["status"] != "delivered"]
        fig = px.bar(not_done, x="orders", y="status", orientation="h", text="orders",
                     labels={"orders": "Orders", "status": ""})
        fig.update_traces(marker_color=WARN, texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(height=340, barcornerradius=6,
                          yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig, theme=None)
        insight(operations.status_insight(status, k))

# ---------- Exception list ----------
section_title("Late-order exception list")
with st.container(border=True, key="card_exceptions"):
    exceptions = operations.exception_list(ops, snapshot)
    insight(operations.exceptions_insight(exceptions))

    f1, f2, f3 = st.columns(3)
    issue_choice = f1.multiselect(
        "Issue", options=sorted(exceptions["issue"].unique()),
        placeholder="All issues",
    )
    state_choice = f2.multiselect(
        "Customer state", options=sorted(exceptions["customer_state"].dropna().unique()),
        placeholder="All states",
    )
    max_days = int(exceptions["days_over"].max()) if not exceptions.empty else 1
    min_days = f3.slider("At least this many days over", 1, max(max_days, 2), 1)

    shown = exceptions[exceptions["days_over"] >= min_days]
    if issue_choice:
        shown = shown[shown["issue"].isin(issue_choice)]
    if state_choice:
        shown = shown[shown["customer_state"].isin(state_choice)]

    table = shown.copy()
    table["order_id"] = table["order_id"].str[:8]
    for col in ["purchased_at", "promised_date", "delivered_at"]:
        table[col] = table[col].dt.date
    table = table.rename(columns={
        "order_id": "Order ID", "issue": "Issue", "order_status": "Status",
        "customer_state": "State", "purchased_at": "Purchased", "promised_date": "Promised",
        "delivered_at": "Delivered", "days_over": "Days over", "review_score": "Review",
        "revenue": "Order value (R$)",
    })

    st.caption(f"Showing {len(table):,} of {len(exceptions):,} orders")
    show_table(table, hide_index=True, height=380)
    st.download_button(
        "Download CSV", data=table.to_csv(index=False).encode("utf-8"),
        file_name=f"late_order_exceptions_{start}_to_{end}.csv", mime="text/csv",
        icon=":material/download:",
    )

st.caption("Data: Olist Brazilian E-Commerce Public Dataset (Kaggle), licensed CC BY-NC-SA 4.0.")