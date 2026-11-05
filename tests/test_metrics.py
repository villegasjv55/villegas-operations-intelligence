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
