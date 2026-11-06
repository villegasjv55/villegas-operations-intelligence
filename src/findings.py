"""Findings & Recommendations: the three actions the data supports, with live numbers."""
from src import analytics, logistics, operations


def _weighted(values, weights):
    """Average of values, giving bigger groups more weight."""
    mask = values.notna() & weights.notna()
    if weights[mask].sum() == 0:
        return 0.0
    return (values[mask] * weights[mask]).sum() / weights[mask].sum()


def review_impact(facts, ops):
    """Recommendation 1: how many bad reviews come from late orders, and where time is lost."""
    delay = analytics.review_by_delay(facts)
    on_time = delay[delay["delay_group"] == "On time"]
    late = delay[delay["delay_group"] != "On time"]
    if on_time.empty or late.empty:
        return None
    ot = on_time.iloc[0]
    late_orders = late["orders"].sum()
    late_detractors = (late["orders"] * late["detractor_rate"] / 100).sum()
    on_time_detractors = ot["orders"] * ot["detractor_rate"] / 100
    all_detractors = late_detractors + on_time_detractors
    # If late orders were as satisfied as on-time orders, these bad reviews would not exist
    avoidable = late_detractors - late_orders * ot["detractor_rate"] / 100

    result = {
        "on_time_review": ot["avg_review"],
        "late_review": _weighted(late["avg_review"], late["orders"]),
        "late_share": 100 * late_orders / delay["orders"].sum(),
        "late_detractor_share": 100 * late_detractors / all_detractors,
        "avoidable": avoidable,
        "avoidable_share": 100 * avoidable / all_detractors,
        "stage": None,
    }
    comparison = operations.stage_comparison(ops)
    pivot = comparison.pivot(index="stage", columns="delivery", values="days")
    if {"On time", "Late"}.issubset(pivot.columns):
        extra = pivot["Late"] - pivot["On time"]
        stage = extra.idxmax()
        result.update(stage=stage, stage_late=pivot.loc[stage, "Late"],
                      stage_on_time=pivot.loc[stage, "On time"],
                      stage_share=100 * extra[stage] / extra.sum() if extra.sum() > 0 else 0)
    return result


def seller_impact(items, threshold=10):
    """Recommendation 2: sellers who miss their shipping deadline often."""
    card = logistics.seller_scorecard(items).dropna(subset=["late_rate"])
    flagged = card[card["missed_handoff_rate"] > threshold]
    rest = card[card["missed_handoff_rate"] <= threshold]
    if flagged.empty or rest.empty:
        return None
    rest_late = _weighted(rest["late_rate"], rest["orders"])
    flagged_late = _weighted(flagged["late_rate"], flagged["orders"])
    extra_late = (flagged["late_rate"] - rest_late).clip(lower=0)
    return {
        "threshold": threshold,
        "ranked": len(card),
        "flagged": len(flagged),
        "flagged_order_share": 100 * flagged["orders"].sum() / card["orders"].sum(),
        "flagged_late": flagged_late,
        "rest_late": rest_late,
        "avoided": (flagged["orders"] * extra_late / 100).sum(),
    }


def state_impact(facts, ops, top_n=5, min_orders=300):
    """Recommendation 3: states where promised dates are missed most."""
    states = logistics.state_performance(facts)
    delivered = facts[facts["is_delivered"] == 1]
    if states.empty or delivered.empty:
        return None
    national = 100 * delivered["is_late"].mean()
    big = states[states["orders"] >= min_orders]
    worst = big.sort_values("late_rate", ascending=False).head(top_n)
    extra_late = (worst["late_rate"] - national).clip(lower=0)

    arrived = ops[ops["is_delivered"] == 1].dropna(subset=["delivered_at", "promised_date"])
    days_early = (arrived["promised_date"] - arrived["delivered_at"].dt.normalize()).dt.days
    on_time_only = days_early[days_early >= 0]
    return {
        "national": national,
        "worst_names": list(worst["state_name"]),
        "worst_rates": list(worst["late_rate"]),
        "worst_orders": int(worst["orders"].sum()),
        "avoided": (worst["orders"] * extra_late / 100).sum(),
        "avg_days_early": on_time_only.mean() if not on_time_only.empty else 0,
    }