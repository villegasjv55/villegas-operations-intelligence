"""Module 03 - Seller & Logistics Performance."""
import plotly.express as px
import pydeck as pdk
import streamlit as st

from src import insights, logistics, shared
from src.style import (ACCENT, DANGER, WARN, chart_title, hero, insight, kpi_card,
                       section_title, show_table)

start, end = shared.selected_months()
facts_all = shared.order_facts()
items_all = shared.item_facts()
facts = facts_all[facts_all["purchase_month"].between(start, end)]
items = items_all[items_all["purchase_month"].between(start, end)]

# ---------- Header ----------
hero(
    "Villegas Analytics · Operations Intelligence",
    "Seller & Logistics Performance",
    f"Which sellers and regions cause late deliveries · "
    f"{insights.fmt_month(start)} to {insights.fmt_month(end)}",
)

card = logistics.seller_scorecard(items)
states = logistics.state_performance(facts)
delivered = facts[facts["is_delivered"] == 1]

# ---------- KPI cards ----------
row = st.columns(4)
kpi_card(row[0], "Active sellers", f"{items['seller_id'].nunique():,}",
         f"{len(card):,} with {logistics.MIN_SELLER_ORDERS}+ orders")
kpi_card(row[1], "Missed handoff rate", f"{100 * items['missed_handoff'].mean():.1f}%",
         "Items given to carrier after deadline")
kpi_card(row[2], "Avg seller handoff", f"{facts['handoff_days'].mean():.1f} days",
         "Payment approved to carrier")
kpi_card(row[3], "Avg delivery time", f"{delivered['delivery_days'].mean():.1f} days",
         "Purchase to customer")

# ---------- 3D map ----------
section_title("Where customers wait longest")
map_col, info_col = st.columns([3, 2])

with map_col:
    with st.container(border=True, key="card_map"):
        chart_title("Average delivery time by customer state")
        geo = states.merge(shared.state_centers(), on="customer_state")
        geo["color"] = logistics.late_rate_colors(geo["late_rate"])
        layer = pdk.Layer(
            "ColumnLayer",
            data=geo,
            get_position=["lng", "lat"],
            get_elevation="avg_delivery_days",
            elevation_scale=22000,
            radius=55000,
            get_fill_color="color",
            extruded=True,
            pickable=True,
            auto_highlight=True,
        )
        view = pdk.ViewState(latitude=-15, longitude=-52, zoom=3.1, pitch=50, bearing=-12)
        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view,
            map_provider="carto",
            map_style="dark",
            tooltip={
                "html": "<b>{state_name}</b><br/>{avg_delivery_days} days on average"
                        "<br/>{late_rate}% late<br/>{orders} delivered orders",
                "style": {"backgroundColor": "#111A2E", "color": "#F1F5F9"},
            },
        ))
        st.caption("Column height = average delivery days. Color = late rate "
                   "(cyan = low, red = high). Hold Ctrl and drag to rotate, scroll to zoom, "
                   "hover a column for details.")

with info_col:
    with st.container(border=True, key="card_states"):
        chart_title("Delivery by state")
        insight(logistics.state_insight(states))
        show_table(
            states[["state_name", "orders", "avg_delivery_days", "late_rate", "avg_review"]]
            .rename(columns={
                "state_name": "State", "orders": "Orders",
                "avg_delivery_days": "Avg days", "late_rate": "% late",
                "avg_review": "Avg review",
            }),
            hide_index=True, height=300,
        )

# ---------- Seller scorecard ----------
section_title("Seller scorecard")
scatter_col, seller_info_col = st.columns([3, 2])

with scatter_col:
    with st.container(border=True, key="card_scatter"):
        chart_title("Do slow handoffs cause late deliveries?")
        fig = px.scatter(
            card, x="missed_handoff_rate", y="late_rate", size="orders",
            color="avg_review", color_continuous_scale=[DANGER, WARN, ACCENT],
            range_color=[1, 5], hover_data={"seller_state": True, "orders": True},
            labels={
                "missed_handoff_rate": "Missed handoff rate (%)",
                "late_rate": "Late delivery rate (%)",
                "avg_review": "Avg review",
                "seller_state": "Seller state",
                "orders": "Orders",
            },
        )
        fig.update_traces(marker=dict(opacity=0.75, line=dict(width=0)))
        fig.update_layout(height=400)
        st.plotly_chart(fig, theme=None)
        st.caption("Each bubble is one seller. Bigger = more orders. "
                   "Red = low reviews, cyan = high reviews.")

with seller_info_col:
    with st.container(border=True, key="card_seller_info"):
        chart_title("What the scorecard says")
        insight(logistics.seller_insight(card))

with st.container(border=True, key="card_bottom10"):
    chart_title("Bottom 10 sellers by late-delivery rate (follow-up list)")
    bottom = card.head(10).copy()
    bottom["seller"] = bottom["seller_id"].str[:8]
    columns = {
        "seller": "Seller ID", "seller_state": "State", "orders": "Orders",
        "late_rate": "% late", "missed_handoff_rate": "% missed handoff",
        "avg_handoff_days": "Avg handoff days", "avg_review": "Avg review",
        "revenue": "Revenue (R$)",
    }
    show_table(bottom[list(columns)].rename(columns=columns), hide_index=True)
    with st.expander("See the full seller scorecard"):
        full = card.copy()
        full["seller"] = full["seller_id"].str[:8]
        show_table(full[list(columns)].rename(columns=columns), hide_index=True)

st.caption("Data: Olist Brazilian E-Commerce Public Dataset (Kaggle), licensed CC BY-NC-SA 4.0.")