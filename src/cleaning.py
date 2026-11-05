"""Build clean analysis tables from the raw Olist tables.

Creates in data/olist.db:
  orders_clean   - one row per order, real dates + delivery metrics
  products_clean - products with English category names
  order_facts    - one row per order with revenue, freight, review, location
"""
import pandas as pd

from src.database import get_connection

DATE_COLS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]


def days_between(later, earlier):
    """Gap between two date columns, in days (with decimals)."""
    return (later - earlier).dt.total_seconds() / 86400


def build_orders_clean(conn):
    orders = pd.read_sql_query("SELECT * FROM orders", conn, parse_dates=DATE_COLS)

    purchased = orders["order_purchase_timestamp"]
    approved = orders["order_approved_at"]
    carrier = orders["order_delivered_carrier_date"]
    delivered = orders["order_delivered_customer_date"]
    estimated = orders["order_estimated_delivery_date"]

    orders["purchase_month"] = purchased.dt.to_period("M").astype(str)
    orders["is_delivered"] = (orders["order_status"] == "delivered") & delivered.notna()
    orders["is_canceled"] = orders["order_status"].isin(["canceled", "unavailable"])

    orders["delivery_days"] = days_between(delivered, purchased).round(1)
    orders["promised_days"] = days_between(estimated, purchased).round(1)
    orders["handoff_days"] = days_between(carrier, approved).round(1)

    # Late = arrived on a later calendar day than the promised date
    delivered_day = delivered.dt.normalize()
    orders["is_late"] = orders["is_delivered"] & (delivered_day > estimated)
    orders["days_late"] = (delivered_day - estimated).dt.days.where(orders["is_late"], 0)

    # Timestamps in an impossible order
    orders["has_date_issue"] = (
        (delivered < purchased) | (carrier < purchased) | (delivered < carrier)
    )

    orders.to_sql("orders_clean", conn, if_exists="replace", index=False)


PRODUCTS_SQL = """
DROP TABLE IF EXISTS products_clean;
CREATE TABLE products_clean AS
SELECT p.*,
       COALESCE(t.product_category_name_english,
                p.product_category_name,
                'unknown') AS category
FROM products p
LEFT JOIN category_translation t
       ON p.product_category_name = t.product_category_name;
"""

ORDER_FACTS_SQL = """
DROP TABLE IF EXISTS order_facts;
CREATE TABLE order_facts AS
WITH items AS (
    SELECT order_id,
           COUNT(*)                  AS item_count,
           COUNT(DISTINCT seller_id) AS seller_count,
           SUM(price)                AS revenue,
           SUM(freight_value)        AS freight
    FROM order_items
    GROUP BY order_id
),
review AS (
    SELECT order_id, AVG(review_score) AS review_score
    FROM reviews
    GROUP BY order_id
)
SELECT o.order_id,
       c.customer_unique_id,
       c.customer_state,
       o.order_status,
       o.purchase_month,
       o.order_purchase_timestamp,
       o.is_delivered,
       o.is_canceled,
       o.is_late,
       o.days_late,
       o.delivery_days,
       o.promised_days,
       o.handoff_days,
       o.has_date_issue,
       COALESCE(i.item_count, 0)   AS item_count,
       COALESCE(i.seller_count, 0) AS seller_count,
       COALESCE(i.revenue, 0)      AS revenue,
       COALESCE(i.freight, 0)      AS freight,
       r.review_score
FROM orders_clean o
LEFT JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN items i     ON o.order_id = i.order_id
LEFT JOIN review r    ON o.order_id = r.order_id;
"""


def main():
    conn = get_connection()
    try:
        build_orders_clean(conn)
        conn.executescript(PRODUCTS_SQL)
        conn.executescript(ORDER_FACTS_SQL)
        conn.commit()
        for table in ["orders_clean", "products_clean", "order_facts"]:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"{table:<16} {count:>8,} rows")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
