"""Plain-English summaries of each chart, written from the data so they update with the filters."""
import pandas as pd


def fmt_month(month):
    """'2017-11' -> 'Nov 2017'"""
    return pd.to_datetime(month).strftime("%b %Y")


def revenue_insight(monthly):
    if monthly.empty:
        return "No orders in the selected months."
    peak = monthly.loc[monthly["revenue"].idxmax()]
    text = (f"Revenue peaked in <b>{fmt_month(peak['month'])}</b> at "
            f"<b>R$ {peak['revenue']:,.0f}</b> (the amber bar).")
    first, last = monthly.iloc[0], monthly.iloc[-1]
    if len(monthly) >= 2 and first["revenue"] > 0:
        change = 100 * (last["revenue"] - first["revenue"]) / first["revenue"]
        direction = "grew" if change >= 0 else "fell"
        text += (f" Monthly revenue {direction} <b>{abs(change):.0f}%</b> from "
                 f"{fmt_month(first['month'])} to {fmt_month(last['month'])}.")
    return text


def on_time_insight(on_time, monthly):
    if on_time.empty:
        return "No delivered orders in the selected months."
    avg = on_time["on_time_rate"].mean()
    worst = on_time.loc[on_time["on_time_rate"].idxmin()]
    best = on_time.loc[on_time["on_time_rate"].idxmax()]
    text = (f"On-time delivery ranged from <b>{worst['on_time_rate']:.1f}%</b> in "
            f"{fmt_month(worst['month'])} to <b>{best['on_time_rate']:.1f}%</b> in "
            f"{fmt_month(best['month'])}, averaging {avg:.1f}% per month.")
    if not monthly.empty:
        peak_month = monthly.loc[monthly["revenue"].idxmax(), "month"]
        peak_rate = on_time.loc[on_time["month"] == peak_month, "on_time_rate"]
        if not peak_rate.empty:
            gap = peak_rate.iloc[0] - avg
            if gap < -1:
                text += (f" In the busiest sales month ({fmt_month(peak_month)}), on-time "
                         f"delivery ran <b>{abs(gap):.1f} points below average</b>, a sign "
                         f"the demand spike strained carriers.")
            else:
                text += (f" Even in the busiest sales month ({fmt_month(peak_month)}), "
                         f"on-time delivery held near average.")
    return text


def delay_insight(delay):
    on_time = delay[delay["delay_group"] == "On time"]
    late = delay[delay["delay_group"] != "On time"]
    if on_time.empty or late.empty:
        return "Not enough late and on-time orders in this selection to compare."
    ot = on_time.iloc[0]
    detractors = delay["orders"] * delay["detractor_rate"] / 100
    late_detractor_share = 100 * detractors[late.index].sum() / detractors.sum()
    late_order_share = 100 * late["orders"].sum() / delay["orders"].sum()

    text = (f"On-time orders average <b>{ot['avg_review']:.2f} stars</b>, and only "
            f"{ot['detractor_rate']:.0f}% leave a 1-2 star review. ")
    below_three = late[late["avg_review"] < 3]
    if not below_three.empty:
        g = below_three.iloc[0]
        text += (f"Once an order is <b>{str(g['delay_group']).lower()}</b>, the average "
                 f"falls to <b>{g['avg_review']:.2f}</b> and <b>{g['detractor_rate']:.0f}%</b> "
                 f"of customers leave a 1-2 star review. ")
    text += (f"Late orders are only <b>{late_order_share:.0f}%</b> of deliveries but cause "
             f"<b>{late_detractor_share:.0f}%</b> of all 1-2 star reviews.")
    return text