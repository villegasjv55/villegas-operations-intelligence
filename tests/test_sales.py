"""Checks for Module 02: Sales Analytics."""
import pytest

from src import analytics, sales
from src.database import run_query


@pytest.fixture(scope="module")
def items():
    return sales.load_item_sales()


@pytest.fixture(scope="module")
def payments():
    return sales.load_payments()


@pytest.fixture(scope="module")
def facts():
    return analytics.load_order_facts()


def test_category_revenue_adds_up_to_total(items):
    total = run_query("SELECT SUM(price) FROM order_items").iloc[0, 0]
    assert sales.category_performance(items)["revenue"].sum() == pytest.approx(total, abs=1)


def test_state_revenue_adds_up_to_total(facts):
    total = run_query("SELECT SUM(price) FROM order_items").iloc[0, 0]
    assert sales.state_sales(facts)["revenue"].sum() == pytest.approx(total, abs=1)


def test_payment_value_matches_sql(payments):
    total = run_query(
        "SELECT SUM(payment_value) FROM payments WHERE payment_type <> 'not_defined'"
    ).iloc[0, 0]
    assert sales.payment_mix(payments)["value"].sum() == pytest.approx(total, abs=1)


def test_repeat_customer_rate_matches_sql(facts):
    sql_rate = run_query("""
        SELECT 100.0 * SUM(n >= 2) / COUNT(*) FROM (
            SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) AS n
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            GROUP BY c.customer_unique_id
        )
    """).iloc[0, 0]
    assert sales.repeat_customer_rate(facts) == pytest.approx(sql_rate, abs=0.01)
    