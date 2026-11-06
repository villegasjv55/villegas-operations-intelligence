"""Checks for Module 05: Reporting Center."""
import pytest

from src import analytics, logistics, operations, reporting, sales


@pytest.fixture(scope="module")
def data():
    facts = analytics.load_order_facts()
    return {
        "facts": facts,
        "items": logistics.load_item_facts(),
        "ops": operations.load_ops(),
        "item_sales": sales.load_item_sales(),
        "snapshot": operations.snapshot_date(),
        "months": analytics.complete_months(facts),
    }


def kpis(d, month):
    return reporting.month_kpis(month, d["facts"], d["items"], d["ops"], d["snapshot"])


def test_monthly_orders_add_up(data):
    total = sum(kpis(data, m)["Orders"] for m in data["months"])
    in_months = data["facts"][data["facts"]["purchase_month"].isin(data["months"])]
    assert total == in_months["order_id"].nunique()


def test_first_month_has_nothing_to_compare(data):
    first = data["months"][0]
    assert reporting.previous_month(first, data["months"]) is None
    table = reporting.kpi_table(kpis(data, first))
    assert table["change"].isna().all()


def test_report_is_complete(data):
    month = data["months"][-1]
    prev = reporting.previous_month(month, data["months"])
    table = reporting.kpi_table(kpis(data, month), kpis(data, prev))
    issues = reporting.top_issues(month, table, data["facts"], data["items"], data["item_sales"])
    html = reporting.build_html_report(month, prev, table, issues,
                                       reporting.summary_sentence(month, prev, table))
    assert len(issues) <= 3
    assert "Villegas Analytics" in html
    assert "Monthly Operations Report" in html