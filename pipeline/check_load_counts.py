"""
Purpose : Verify that the row counts in MySQL match what the cleaned CSVs contain.
          Also prints sample rows and the min/max season from the database.
          Prints PASS or FAIL for each table.
Reads   : cleaned DataFrames (passed in), MySQL tables via SELECT COUNT(*)
Writes  : nothing (output is printed to the terminal)
How to run: called by run_full_pipeline.py, or directly:
    cd ipl-pipeline
    python -m pipeline.check_load_counts
"""

import pandas as pd
from sqlalchemy import text
from pipeline.db_connection import get_engine


def check_counts(matches_df: pd.DataFrame, deliveries_df: pd.DataFrame):
    """Compare cleaned DataFrame row counts with MySQL table row counts."""
    engine = get_engine(include_db=True)

    print("\n[check] Verifying row counts ...")
    print("=" * 55)

    with engine.connect() as conn:
        # --- Check matches ---
        result     = conn.execute(text("SELECT COUNT(*) FROM matches"))
        db_count   = result.scalar()  # .scalar() returns the single value from the result
        csv_count  = len(matches_df)
        status     = "PASS" if db_count == csv_count else "FAIL"
        print(f"  matches   | CSV: {csv_count:>7,} | DB: {db_count:>7,} | {status}")

        # --- Check deliveries ---
        result     = conn.execute(text("SELECT COUNT(*) FROM deliveries"))
        db_count   = result.scalar()
        csv_count  = len(deliveries_df)
        status     = "PASS" if db_count == csv_count else "FAIL"
        print(f"  deliveries| CSV: {csv_count:>7,} | DB: {db_count:>7,} | {status}")

        # --- Print min/max season ---
        result = conn.execute(text("SELECT MIN(season), MAX(season) FROM matches"))
        row    = result.fetchone()
        print(f"\n  Seasons in DB: {row[0]} to {row[1]}")

        # --- Print 3 sample rows from matches ---
        print("\n  Sample rows from matches table:")
        result = conn.execute(text("SELECT match_id, season, match_date, team1, team2, winner FROM matches LIMIT 3"))
        rows   = result.fetchall()
        for r in rows:
            print(f"    {r}")

        # --- Print 3 sample rows from deliveries ---
        print("\n  Sample rows from deliveries table:")
        result = conn.execute(text("SELECT delivery_id, match_id, innings, batter, bowler, batter_runs, total_runs FROM deliveries LIMIT 3"))
        rows   = result.fetchall()
        for r in rows:
            print(f"    {r}")

    print("=" * 55)
    print("[check] Done.\n")


if __name__ == "__main__":
    # When run standalone, load the cleaned CSVs from disk for comparison.
    from pathlib import Path
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    PROCESSED    = PROJECT_ROOT / "data" / "processed"

    matches_df    = pd.read_csv(PROCESSED / "matches_clean.csv")
    deliveries_df = pd.read_csv(PROCESSED / "deliveries_clean.csv")
    check_counts(matches_df, deliveries_df)

