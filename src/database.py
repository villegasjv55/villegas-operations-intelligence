"""Database connection helpers. Every part of the app reads data through here."""
import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "olist.db"


def get_connection():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}. Run: python src/data_loader.py"
        )
    return sqlite3.connect(DB_PATH)


def run_query(sql, params=None):
    """Run a SQL query and return the result as a pandas DataFrame."""
    conn = get_connection()
    try:
        return pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()
