"""Checks for the Findings & Recommendations numbers."""
import pytest

from src import analytics, findings, logistics, operations


@pytest.fixture(scope="module")
def data():
    return {
        "facts": analytics.load_order_facts(),
        "items": logistics.load_item_facts(),
        "ops": operations.load_ops(),
    }


def test_review_impact_is_sensible(data):
    r = findings.review_impact(data["facts"], data["ops"])
    assert r["avoidable"] >= 0
    assert 0 <= r["late_detractor_share"] <= 100
    assert r["on_time_review"] > r["late_review"]


def test_seller_impact_is_sensible(data):
    s = findings.seller_impact(data["items"])
    assert 0 < s["flagged"] < s["ranked"]
    assert s["avoided"] >= 0


def test_state_impact_is_sensible(data):
    st = findings.state_impact(data["facts"], data["ops"])
    assert len(st["worst_names"]) == 5
    assert all(rate >= st["national"] for rate in st["worst_rates"])