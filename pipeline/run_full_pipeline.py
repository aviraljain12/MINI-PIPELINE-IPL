"""
Purpose : ENTRY POINT for the full ETL pipeline.
          Runs every step in order:
            0. Inspect raw data (prints a report; you can read it and check column names)
            1. Extract raw CSVs into DataFrames
            2. Clean matches and deliveries
            3. Create the MySQL database and tables (runs the SQL file)
            4. Load cleaned data into MySQL
            5. Verify row counts (prints PASS/FAIL)
Reads   : data/raw/ipl_matches.csv, data/raw/ipl_ball_by_ball.csv
Writes  : data/processed/matches_clean.csv, data/processed/deliveries_clean.csv
          MySQL tables: ipl_db.matches, ipl_db.deliveries
How to run:
    cd ipl-pipeline
    python -m pipeline.run_full_pipeline

RE-RUNNABLE: running this script twice gives identical MySQL tables, not duplicates.
  This works because create_tables.py runs DROP TABLE + CREATE TABLE before each load.
"""

import sys
from pipeline.extract_raw_csv  import load_raw_matches, load_raw_deliveries
from pipeline.inspect_raw_data  import (inspect_dataframe,
                                        inspect_distinct_teams,
                                        inspect_distinct_venues,
                                        inspect_over_ball_range)
from pipeline.clean_matches    import clean_matches
from pipeline.clean_deliveries import clean_deliveries
from pipeline.create_tables    import create_tables
from pipeline.load_into_mysql  import load_all
from pipeline.check_load_counts import check_counts


def run_pipeline():
    """Run every ETL step in the correct order."""

    print("\n" + "=" * 60)
    print("  IPL DATA PIPELINE — STARTING")
    print("=" * 60)

    # ----------------------------------------------------------------
    # STEP 0 — INSPECT
    # ----------------------------------------------------------------
    # Print a detailed report of raw column names, dtypes, and nulls.
    # Read this output carefully the first time you run the pipeline.
    # If column names differ from what clean_matches.py expects,
    # update the COLUMN_MAP dictionaries in clean_matches.py and
    # clean_deliveries.py before re-running.
    print("\n--- STEP 0: Inspect raw data ---")
    raw_matches    = load_raw_matches()
    raw_deliveries = load_raw_deliveries()
    inspect_dataframe(raw_matches,    "ipl_matches.csv")
    inspect_dataframe(raw_deliveries, "ipl_ball_by_ball.csv")
    inspect_distinct_teams(raw_matches)
    inspect_distinct_venues(raw_matches)
    inspect_over_ball_range(raw_deliveries)

    # ----------------------------------------------------------------
    # STEP 1 — CLEAN
    # ----------------------------------------------------------------
    print("\n--- STEP 1: Clean data ---")
    clean_matches_df    = clean_matches(raw_matches)
    clean_deliveries_df = clean_deliveries(raw_deliveries, clean_matches_df)

    # ----------------------------------------------------------------
    # STEP 2 — CREATE TABLES
    # ----------------------------------------------------------------
    # Runs the SQL file: DROP TABLE + CREATE TABLE + CREATE INDEX.
    # This empties the tables so re-running the pipeline doesn't duplicate rows.
    print("\n--- STEP 2: Create MySQL tables ---")
    create_tables()

    # ----------------------------------------------------------------
    # STEP 3 — LOAD
    # ----------------------------------------------------------------
    print("\n--- STEP 3: Load data into MySQL ---")
    load_all(clean_matches_df, clean_deliveries_df)

    # ----------------------------------------------------------------
    # STEP 4 — VERIFY
    # ----------------------------------------------------------------
    print("\n--- STEP 4: Verify row counts ---")
    check_counts(clean_matches_df, clean_deliveries_df)

    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE — Run the dashboard with:")
    print("  streamlit run app/streamlit_app.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        run_pipeline()
    except FileNotFoundError as e:
        # Give a clear, friendly message when the CSV files are missing.
        print(f"\n[ERROR] {e}")
        print("  Download both CSVs from Kaggle and place them in data/raw/")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}")
        raise

