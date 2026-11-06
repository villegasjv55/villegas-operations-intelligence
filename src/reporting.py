"""Module 05: Reporting Center - a one-click monthly operations report."""
from datetime import datetime

import pandas as pd

from src import analytics, operations, sales
from src.insights import fmt_month
from src.logistics import STATE_NAMES

# For these metrics, going up is good. For the rest, going down is good.
HIGHER_IS_BETTER = {"Orders", "Revenue (R$)", "Average order value (R$)",
                    "On-time delivery (%)", "Average review"}


def previous_month(month, months):
    i = months.index(month)
    return months[i - 1] if i > 0 else None


def month_kpis(month, facts, items, ops, snapshot):
    """The report's key numbers for one month."""
    f = facts[facts["purchase_month"] == month]
    it = items[items["purchase_month"] == month]
    o = ops[ops["purchase_month"] == month]
    k = analytics.kpis_pandas(f)
    reviews = f["review_score"].dropna()
    detractors = round(100 * (reviews <= 2).mean(), 2) if len(reviews) else 0.0
    return {
        "Orders": k["orders"],
        "Revenue (R$)": k["revenue"],
        "Average order value (R$)": k["avg_order_value"],
        "On-time delivery (%)": k["on_time_rate"],
        "Average review": k["avg_review"],
        "1-2 star reviews (%)": detractors,
        "Late deliveries": int(f["is_late"].sum()),
        "Cancellation rate (%)": round(operations.ops_kpis(o, snapshot)["cancel_rate"], 2),
        "Missed handoff rate (%)": round(100 * it["missed_handoff"].mean(), 2),
    }


def kpi_table(current, previous=None):
    """This month vs. last month, with the change and whether it is good or bad."""
    rows = []
    for name, value in current.items():
        prev = previous.get(name) if previous else None
        change = value - prev if prev is not None else None
        change_pct = 100 * change / prev if prev not in (None, 0) else None
        if change is None or change == 0:
            direction = "flat"
        elif (change > 0) == (name in HIGHER_IS_BETTER):
            direction = "good"
        else:
            direction = "bad"
        rows.append({"metric": name, "this_month": value, "last_month": prev,
                     "change": change, "change_pct": change_pct, "direction": direction})
    return pd.DataFrame(rows)


def fmt_value(name, value):
    if value is None or pd.isna(value):
        return "–"
    if "(R$)" in name:
        return f"R$ {value:,.2f}"
    if "(%)" in name:
        return f"{value:.1f}%"
    if name == "Average review":
        return f"{value:.2f} ★"
    return f"{value:,.0f}"


def fmt_change(name, row):
    if row["change"] is None or pd.isna(row["change"]):
        return "–"
    if "(%)" in name:
        return f"{row['change']:+.1f} pts"
    if name == "Average review":
        return f"{row['change']:+.2f}"
    if row["change_pct"] is not None and pd.notna(row["change_pct"]):
        return f"{row['change_pct']:+.1f}%"
    return f"{row['change']:+,.0f}"


def change_text(name, row, prev_month):
    """Colored up/down line for a KPI card."""
    if prev_month is None or row["change"] is None or pd.isna(row["change"]):
        return "No earlier month to compare"
    arrow = "▲" if row["change"] > 0 else ("▼" if row["change"] < 0 else "■")
    color = {"good": "#34D399", "bad": "#F87171"}.get(row["direction"], "#8FA3BF")
    label = fmt_change(name, row)
    return f'<span style="color:{color}">{arrow} {label} vs {fmt_month(prev_month)}</span>'


def summary_sentence(month, prev_month, table):
    t = table.set_index("metric")
    orders = t.loc["Orders", "this_month"]
    revenue = t.loc["Revenue (R$)", "this_month"]
    on_time = t.loc["On-time delivery (%)", "this_month"]
    review = t.loc["Average review", "this_month"]
    text = (f"In <b>{fmt_month(month)}</b>, the marketplace processed <b>{orders:,.0f}</b> "
            f"orders worth <b>R$ {revenue:,.0f}</b>. On-time delivery was <b>{on_time:.1f}%</b> "
            f"and the average review was <b>{review:.2f}★</b>.")
    if prev_month is not None:
        rev = t.loc["Revenue (R$)", "change_pct"]
        ot = t.loc["On-time delivery (%)", "change"]
        rev_word = "rose" if rev >= 0 else "fell"
        ot_word = "improved" if ot >= 0 else "dropped"
        text += (f" Compared with {fmt_month(prev_month)}, revenue {rev_word} "
                 f"<b>{abs(rev):.1f}%</b> and on-time delivery {ot_word} by "
                 f"<b>{abs(ot):.1f} points</b>.")
    return text


def top_issues(month, table, facts, items, item_sales, limit=3):
    """The most important problems this month, found automatically."""
    issues = []
    t = table.set_index("metric")
    ot_change = t.loc["On-time delivery (%)", "change"]
    ot_now = t.loc["On-time delivery (%)", "this_month"]
    if ot_change is not None and pd.notna(ot_change) and ot_change < -0.5:
        issues.append(f"On-time delivery <b>dropped {abs(ot_change):.1f} points</b> "
                      f"to {ot_now:.1f}%.")

    f = facts[(facts["purchase_month"] == month) & (facts["is_delivered"] == 1)]
    by_state = f.groupby("customer_state").agg(orders=("order_id", "count"), late=("is_late", "sum"))
    by_state = by_state[by_state["orders"] >= 50]
    if not by_state.empty and by_state["late"].max() > 0:
        code = by_state["late"].idxmax()
        late = int(by_state.loc[code, "late"])
        orders = int(by_state.loc[code, "orders"])
        issues.append(f"<b>{STATE_NAMES.get(code, code)}</b> had the most late deliveries: "
                      f"<b>{late}</b> of {orders} orders ({100 * late / orders:.1f}% late).")

    it = items[(items["purchase_month"] == month) & (items["is_delivered"] == 1)]
    it = it.drop_duplicates(["seller_id", "order_id"])
    by_seller = it.groupby(["seller_id", "seller_state"]).agg(orders=("order_id", "nunique"), late=("is_late", "sum"))
    by_seller = by_seller.reset_index()
    by_seller = by_seller[by_seller["orders"] >= 10]
    if not by_seller.empty and by_seller["late"].max() > 0:
        w = by_seller.sort_values("late", ascending=False).iloc[0]
        late, orders = int(w["late"]), int(w["orders"])
        issues.append(f"Seller <b>{w['seller_id'][:8]}</b> ({w['seller_state']}) delivered "
                      f"<b>{late}</b> of {orders} orders late ({100 * late / orders:.0f}%).")

    cs = item_sales[item_sales["purchase_month"] == month]
    cs = cs.drop_duplicates(["category", "order_id"])
    by_cat = cs.groupby("category").agg(orders=("order_id", "nunique"), review=("review_score", "mean"))
    by_cat = by_cat[by_cat["orders"] >= 50]
    if not by_cat.empty:
        name = by_cat["review"].idxmin()
        review = by_cat.loc[name, "review"]
        orders = int(by_cat.loc[name, "orders"])
        issues.append(f"<b>{sales.pretty_category(name)}</b> had the lowest reviews among big "
                      f"categories: <b>{review:.2f}★</b> across {orders} orders.")
    return issues[:limit]


REPORT_CSS = """
body{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#0F172A;max-width:820px;
margin:32px auto;padding:0 24px;line-height:1.5}
.brand{color:#0891B2;font-size:12px;font-weight:700;letter-spacing:.14em;text-transform:uppercase}
h1{margin:4px 0 2px;font-size:28px}.sub{color:#64748B;margin-bottom:24px}
h2{font-size:17px;margin:28px 0 8px;border-bottom:2px solid #22D3EE;padding-bottom:4px}
table{width:100%;border-collapse:collapse;font-size:14px}
th{background:#0B1220;color:#fff;text-align:left;padding:8px}
td{padding:8px;border-bottom:1px solid #E2E8F0}
.good{color:#059669;font-weight:600}.bad{color:#DC2626;font-weight:600}
.box{background:#ECFEFF;border-left:4px solid #0891B2;padding:12px 16px;border-radius:6px}
.foot{margin-top:32px;color:#64748B;font-size:12px}
"""


def build_html_report(month, prev_month, table, issues, summary):
    """A complete, printable report page (open it, then Print -> Save as PDF)."""
    rows = ""
    for _, r in table.iterrows():
        name = r["metric"]
        rows += (f"<tr><td>{name}</td><td>{fmt_value(name, r['this_month'])}</td>"
                 f"<td>{fmt_value(name, r['last_month'])}</td>"
                 f"<td class='{r['direction']}'>{fmt_change(name, r)}</td></tr>")
    issue_items = "".join(f"<li>{i}</li>" for i in issues) or "<li>No major issues found.</li>"
    prev_label = fmt_month(prev_month) if prev_month else "previous month"
    month_label = fmt_month(month)
    created = datetime.now().strftime("%b %d, %Y")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Operations Report - {month_label}</title><style>{REPORT_CSS}</style></head><body>
<div class="brand">Villegas Analytics · Operations Intelligence</div>
<h1>Monthly Operations Report: {month_label}</h1>
<div class="sub">Olist marketplace · compared with {prev_label} · created {created}</div>
<h2>Summary</h2><div class="box">{summary}</div>
<h2>Key numbers</h2>
<table><tr><th>Metric</th><th>{month_label}</th><th>{prev_label}</th><th>Change</th></tr>
{rows}</table>
<h2>Top issues this month</h2><ol>{issue_items}</ol>
<h2>Recommended focus</h2><ol>
<li>Contact customers whose orders are at risk of arriving late, before the promised date.</li>
<li>Follow up with the sellers who missed shipping deadlines or delivered late most often.</li>
<li>Review promised delivery dates for the states with the highest late rates.</li></ol>
<div class="foot">Built by Juan Villegas · Villegas Operations Intelligence.
Data: Olist Brazilian E-Commerce Public Dataset (Kaggle), CC BY-NC-SA 4.0.
Values in Brazilian reais (R$).</div></body></html>"""
