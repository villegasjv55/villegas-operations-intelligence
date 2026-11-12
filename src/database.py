"""Database connection helpers. Every part of the app reads data through here."""
import gzip
import shutil
import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "olist.db"
GZ_PATH = DB_PATH.with_name("olist.db.gz")


def ensure_database():
    """On the live site only the zipped copy is on GitHub, so unzip it the first time."""
    if not DB_PATH.exists() and GZ_PATH.exists():
        tmp = DB_PATH.with_name("olist.db.tmp")
        with gzip.open(GZ_PATH, "rb") as src, open(tmp, "wb") as dst:
            shutil.copyfileobj(src, dst)
        tmp.replace(DB_PATH)


def get_connection():
    ensure_database()
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
