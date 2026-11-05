"""Verify every KPI gives the same answer in Pandas and SQL."""
import pytest

from src import analytics


@pytest.fixture(scope="module")
def facts():
    return analytics.load_order_facts()


def test_kpis_match_between_pandas_and_sql(facts):
    pandas_kpis = analytics.kpis_pandas(facts)
    sql_kpis = analytics.kpis_sql()
    for key in pandas_kpis:
        assert pandas_kpis[key] == pytest.approx(sql_kpis[key], abs=0.01), key


def test_monthly_revenue_matches(facts):
    p = analytics.monthly_revenue_pandas(facts)
    s = analytics.monthly_revenue_sql()
    merged = s.merge(p, on="month", suffixes=("_sql", "_pandas"))
    assert len(merged) == len(s)
    assert (merged["revenue_sql"] - merged["revenue_pandas"]).abs().max() < 0.01


def test_one_row_per_order(facts):
    assert facts["order_id"].is_unique


def test_on_time_rate_is_a_percentage(facts):
    rate = analytics.kpis_pandas(facts)["on_time_rate"]
    assert 0 <= rate <= 100


def test_late_vs_on_time_matches_sql(facts):
    p = analytics.late_vs_on_time_pandas(facts).set_index("status")["avg_review"]
    s = analytics.late_vs_on_time_sql().set_index("status")["avg_review"]
    for status in ["late", "on_time"]:
        assert p[status] == pytest.approx(s[status], abs=0.01), status


def test_delay_groups_cover_every_reviewed_delivery(facts):
    groups = analytics.review_by_delay(facts)
    reviewed = facts[(facts["is_delivered"] == 1) & facts["review_score"].notna()]
    assert groups["orders"].sum() == len(reviewed)


def test_complete_months_drops_thin_months(facts):
    months = analytics.complete_months(facts)
    counts = facts.groupby("purchase_month")["order_id"].nunique()
    assert all(counts[m] >= analytics.MIN_MONTHLY_ORDERS for m in months)
    assert len(months) < len(counts)