"""Checks for Module 03: Seller & Logistics."""
import pytest

from src import analytics, logistics
from src.database import run_query


@pytest.fixture(scope="module")
def items():
    return logistics.load_item_facts()


@pytest.fixture(scope="module")
def facts():
    return analytics.load_order_facts()


def test_one_row_per_item_sold(items):
    total_items = run_query("SELECT COUNT(*) FROM order_items").iloc[0, 0]
    assert len(items) == total_items


def test_missed_handoff_rate_matches_sql(items):
    sql_rate = run_query("""
        SELECT 100.0 * AVG(CASE WHEN o.order_delivered_carrier_date > i.shipping_limit_date
                                THEN 1.0 ELSE 0.0 END)
        FROM order_items i
        JOIN orders o ON i.order_id = o.order_id
        WHERE o.order_delivered_carrier_date IS NOT NULL
    """).iloc[0, 0]
    pandas_rate = 100 * items["missed_handoff"].mean()
    assert pandas_rate == pytest.approx(sql_rate, abs=0.01)


def test_scorecard_has_one_row_per_seller(items):
    card = logistics.seller_scorecard(items)
    assert card["seller_id"].is_unique
    assert (card["orders"] >= logistics.MIN_SELLER_ORDERS).all()


def test_state_orders_add_up_to_all_delivered(facts):
    states = logistics.state_performance(facts)
    assert states["orders"].sum() == (facts["is_delivered"] == 1).sum()