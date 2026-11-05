"""Load the raw Olist CSV files into a single SQLite database."""
import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DB_PATH = PROJECT_ROOT / "data" / "olist.db"

# table name in the database  ->  CSV file it comes from
TABLES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


def load_all():
    conn = sqlite3.connect(DB_PATH)
    for table, filename in TABLES.items():
        df = pd.read_csv(RAW_DIR / filename)
        df.to_sql(table, conn, if_exists="replace", index=False)
        print(f"{table:<22} {len(df):>10,} rows")
    conn.close()
    print(f"\nDatabase saved to {DB_PATH}")


if __name__ == "__main__":
    load_all()
