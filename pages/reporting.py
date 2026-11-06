"""Module 05 - Reporting Center."""
import streamlit as st
import streamlit.components.v1 as components

from src import analytics, insights, operations, reporting, sales, shared
from src.style import chart_title, hero, insight, kpi_card, section_title, show_table


@st.cache_data
def get_ops():
    return operations.load_ops()


@st.cache_data
def get_snapshot():
    return operations.snapshot_date()


@st.cache_data
def get_item_sales():
    return sales.load_item_sales()


facts = shared.order_facts()
items = shared.item_facts()
ops = get_ops()
snapshot = get_snapshot()
item_sales = get_item_sales()
months = analytics.complete_months(facts)

hero(
    "Villegas Analytics · Operations Intelligence",
    "Reporting Center",
    "A one-click monthly operations report: what changed, what went wrong, and what to do first",
)

month = st.selectbox("Report month", options=months[::-1], format_func=insights.fmt_month)
prev = reporting.previous_month(month, months)

current = reporting.month_kpis(month, facts, items, ops, snapshot)
previous = reporting.month_kpis(prev, facts, items, ops, snapshot) if prev else None
table = reporting.kpi_table(current, previous)
indexed = table.set_index("metric")

# ---------- KPI cards ----------
row = st.columns(4)
for col, name in zip(row, ["Revenue (R$)", "Orders", "On-time delivery (%)", "Average review"]):
    r = indexed.loc[name]
    kpi_card(col, name, reporting.fmt_value(name, r["this_month"]),
             reporting.change_text(name, r, prev))

# ---------- Summary and issues ----------
summary = reporting.summary_sentence(month, prev, table)
issues = reporting.top_issues(month, table, facts, items, item_sales)

left, right = st.columns(2)
with left:
    section_title("Summary")
    insight(summary)
with right:
    section_title("Top issues this month")
    issue_list = "".join(f"<li>{i}</li>" for i in issues) or "<li>No major issues found.</li>"
    insight(f"<ol style='margin:0;padding-left:18px'>{issue_list}</ol>")

# ---------- All numbers ----------
section_title("All key numbers")
with st.container(border=True, key="card_report_table"):
    prev_label = insights.fmt_month(prev) if prev else "Previous month"
    display = table.apply(lambda r: {
        "Metric": r["metric"],
        insights.fmt_month(month): reporting.fmt_value(r["metric"], r["this_month"]),
        prev_label: reporting.fmt_value(r["metric"], r["last_month"]),
        "Change": reporting.fmt_change(r["metric"], r),
        "Better or worse": {"good": "Better", "bad": "Worse"}.get(r["direction"], "No change"),
    }, axis=1, result_type="expand")
    show_table(display)

# ---------- Downloads ----------
section_title("Download")
report_html = reporting.build_html_report(month, prev, table, issues, summary)
d1, d2 = st.columns(2)
d1.download_button(
    "Download report (printable page)", data=report_html.encode("utf-8"),
    file_name=f"operations_report_{month}.html", mime="text/html",
    icon=":material/description:", use_container_width=True,
)
d2.download_button(
    "Download numbers (CSV)", data=display.to_csv(index=False).encode("utf-8"),
    file_name=f"operations_report_{month}.csv", mime="text/csv",
    icon=":material/download:", use_container_width=True,
)
st.caption("To get a PDF: open the downloaded report in your browser, then File > Print > Save as PDF.")

with st.expander("Preview the report", expanded=True):
    components.html(report_html, height=900, scrolling=True)