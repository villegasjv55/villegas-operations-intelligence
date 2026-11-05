"""Data quality checks on the raw Olist tables. Results go in docs/data_quality_log.md."""
from src.database import run_query

CHECKS = {
    "Total orders": "SELECT COUNT(*) FROM orders",
    "Duplicate order_ids in orders":
        "SELECT COUNT(*) - COUNT(DISTINCT order_id) FROM orders",
    "Non-delivered orders (canceled, shipped, etc.)":
        "SELECT COUNT(*) FROM orders WHERE order_status <> 'delivered'",
    "Delivered orders missing delivered date": """
        SELECT COUNT(*) FROM orders
        WHERE order_status = 'delivered' AND order_delivered_customer_date IS NULL""",
    "Orders missing approval date":
        "SELECT COUNT(*) FROM orders WHERE order_approved_at IS NULL",
    "Delivered to customer before purchase": """
        SELECT COUNT(*) FROM orders
        WHERE order_delivered_customer_date < order_purchase_timestamp""",
    "Handed to carrier before purchase": """
        SELECT COUNT(*) FROM orders
        WHERE order_delivered_carrier_date < order_purchase_timestamp""",
    "Delivered to customer before carrier handoff": """
        SELECT COUNT(*) FROM orders
        WHERE order_delivered_customer_date < order_delivered_carrier_date""",
    "Orders with no items": """
        SELECT COUNT(*) FROM orders
        WHERE order_id NOT IN (SELECT order_id FROM order_items)""",
    "Orders with no review": """
        SELECT COUNT(*) FROM orders
        WHERE order_id NOT IN (SELECT order_id FROM reviews)""",
    "Orders with more than one review": """
        SELECT COUNT(*) FROM (
            SELECT order_id FROM reviews GROUP BY order_id HAVING COUNT(*) > 1)""",
    "Orders with more than one payment row": """
        SELECT COUNT(*) FROM (
            SELECT order_id FROM payments GROUP BY order_id HAVING COUNT(*) > 1)""",
    "Payments with value 0":
        "SELECT COUNT(*) FROM payments WHERE payment_value = 0",
    "Products with no category":
        "SELECT COUNT(*) FROM products WHERE product_category_name IS NULL",
    "Categories missing an English name": """
        SELECT COUNT(DISTINCT p.product_category_name)
        FROM products p
        LEFT JOIN category_translation t
               ON p.product_category_name = t.product_category_name
        WHERE p.product_category_name IS NOT NULL
          AND t.product_category_name IS NULL""",
    "Geolocation rows per zip prefix (average)": """
        SELECT ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT geolocation_zip_code_prefix), 1)
        FROM geolocation""",
}


def main():
    print(f"{'CHECK':<50} RESULT")
    print("-" * 62)
    for name, sql in CHECKS.items():
        value = run_query(sql).iloc[0, 0]
        print(f"{name:<50} {value}")


if __name__ == "__main__":
    main()
