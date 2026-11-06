"""Checks for Module 04: Operations Performance."""
import pytest

from src import operations
from src.database import run_query


@pytest.fixture(scope="module")
def ops():
    return operations.load_ops()


@pytest.fixture(scope="module")
def snapshot():
    return operations.snapshot_date()


def test_one_row_per_order(ops):
    assert len(ops) == run_query("SELECT COUNT(*) FROM orders").iloc[0, 0]
    assert ops["order_id"].is_unique


def test_cancellation_rate_matches_sql(ops, snapshot):
    sql_rate = run_query("""
        SELECT 100.0 * SUM(order_status IN ('canceled', 'unavailable')) / COUNT(*)
        FROM orders
    """).iloc[0, 0]
    assert operations.ops_kpis(ops, snapshot)["cancel_rate"] == pytest.approx(sql_rate, abs=0.01)


def test_exception_list_is_only_late_or_overdue(ops, snapshot):
    exceptions = operations.exception_list(ops, snapshot)
    assert (exceptions["days_over"] > 0).all()
    expected = int(ops["is_late"].sum()) + len(operations.overdue_orders(ops, snapshot))
    assert len(exceptions) == expected


def test_stage_times_are_never_negative(ops):
    assert (operations.stage_comparison(ops)["days"] >= 0).all()