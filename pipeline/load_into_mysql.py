"""
Purpose : Load the cleaned DataFrames into MySQL tables.
          This is the Load step of ETL.
          Loads matches first, then deliveries (because of the foreign key:
          deliveries.match_id must reference a row in matches).
Reads   : cleaned DataFrames (passed in from run_full_pipeline.py)
Writes  : rows into MySQL tables `matches` and `deliveries`
How to run: called by run_full_pipeline.py — not run directly

RE-RUNNABLE DESIGN:
  We use if_exists="append" so pandas does NOT recreate the table.
  We use DROP TABLE in the SQL file to empty the tables before each run.
  This means: run the pipeline twice → same result, not duplicate rows.
  DO NOT use if_exists="replace" — that would let pandas auto-create the
  table without our carefully designed indexes and foreign key.
"""

import pandas as pd
from sqlalchemy import text
from pipeline.db_connection import get_engine


def load_matches(df: pd.DataFrame):
    """Load the cleaned matches DataFrame into the MySQL matches table."""
    print(f"\n[load] Loading {len(df):,} rows into `matches` ...")
    engine = get_engine(include_db=True)

    # to_sql with if_exists="append" adds rows to the existing (empty) table.
    # chunksize=10000 sends rows in batches of 10,000 so it doesn't run out of memory.
    # index=False tells pandas NOT to write the DataFrame row number as a column.
    rows_written = df.to_sql(
        name="matches",
        con=engine,
        if_exists="append",   # append to existing table — do NOT recreate it
        index=False,          # the DataFrame index is not a database column
        chunksize=10000,
    )
    print(f"[load] matches: {rows_written:,} rows written.")


def load_deliveries(df: pd.DataFrame):
    """Load the cleaned deliveries DataFrame into the MySQL deliveries table."""
    print(f"\n[load] Loading {len(df):,} rows into `deliveries` ...")
    engine = get_engine(include_db=True)

    # delivery_id is AUTO_INCREMENT in MySQL — we do NOT send it from Python.
    # MySQL will assign it automatically when we insert each row.
    # Make sure the DataFrame does NOT have a delivery_id column before calling this.
    if "delivery_id" in df.columns:
        df = df.drop(columns=["delivery_id"])

    rows_written = df.to_sql(
        name="deliveries",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=10000,
    )
    print(f"[load] deliveries: {rows_written:,} rows written.")


def load_all(matches_df: pd.DataFrame, deliveries_df: pd.DataFrame):
    """Load matches first, then deliveries (foreign key requires this order)."""
    load_matches(matches_df)
    load_deliveries(deliveries_df)
    print("\n[load] All data loaded successfully.\n")

