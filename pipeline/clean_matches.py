"""
Purpose : Clean the raw matches DataFrame and return a cleaned version
          ready to be loaded into MySQL's `matches` table.
          This is the Transform step of ETL for the matches data.
Reads   : raw matches DataFrame (passed in from run_full_pipeline.py)
Writes  : data/processed/matches_clean.csv
How to run: imported by run_full_pipeline.py — not run directly

CLEANING STEPS APPLIED:
  1. Strip whitespace from all text columns.
  2. Rename raw CSV columns → database column names.
  3. Convert match_date to a proper date type.
  4. Standardise team names using TEAM_NAME_MAP.
  5. Standardise venue names using VENUE_NAME_MAP.
  6. Drop exact duplicate rows.
  7. Keep winner as NULL for no-result matches — do NOT fill it.
  8. Print a cleaning report and save the cleaned CSV.

IMPORTANT — COLUMN NAMES:
  The column names below (in COLUMN_MAP) are based on what the Kaggle
  dataset commonly uses. Run inspect_raw_data.py on your CSV first.
  If the actual column names differ, update COLUMN_MAP to match.
"""

import pandas as pd
from pathlib import Path
from pipeline.team_and_venue_name_fixes import TEAM_NAME_MAP, VENUE_NAME_MAP

PROJECT_ROOT  = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


# Map raw CSV column names → our database column names.
# Left side  = exact column name in ipl_matches.csv (confirmed by inspect_raw_data.py).
# Right side = column name in the MySQL `matches` table.
# VERIFIED against the real CSV: match_id already named correctly; season is a string.
COLUMN_MAP: dict[str, str] = {
    "match_id":      "match_id",       # unique match identifier (already correct name)
    "season":        "season",         # IPL year as string e.g. "2024" → cast to int below
    "date":          "match_date",     # match date string → cast to DATE below
    "venue":         "venue",          # stadium name
    "city":          "city",           # city name
    "team1":         "team1",          # one of the two teams
    "team2":         "team2",          # the other team
    "toss_winner":   "toss_winner",    # which team won the toss
    "toss_decision": "toss_decision",  # "bat" or "field"
    "winner":        "winner",         # winning team (NULL for no-result matches)
}

# Columns we want to keep in the final table (the values in COLUMN_MAP)
KEEP_COLUMNS = list(COLUMN_MAP.values())


def clean_matches(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the raw matches DataFrame and return the cleaned version.
    Also saves matches_clean.csv to data/processed/.
    """
    print("\n[clean_matches] Starting cleaning ...")
    rows_read = len(df)

    # ---- Step 1: Strip whitespace from all text (object) columns ----
    df = strip_whitespace(df)

    # ---- Step 2: Rename columns to our database names ----
    df = rename_columns(df)

    # ---- Step 3: Convert match_date to a date type ----
    df["match_date"] = pd.to_datetime(df["match_date"], errors="coerce")
    # errors="coerce" turns unparseable dates into NaT (Not a Time) instead of crashing.

    # ---- Step 4: Cast match_id and season to integer ----
    # match_id is already int64 in the CSV, but we re-cast to be safe.
    # season comes in as a string — some old seasons use "2007/08" format.
    # We extract just the first 4-digit year (e.g. "2007/08" → 2007, "2024" → 2024).
    df["match_id"] = pd.to_numeric(df["match_id"], errors="coerce").astype("Int64")
    df["season"]   = df["season"].astype(str).str.extract(r"(\d{4})")[0]
    df["season"]   = pd.to_numeric(df["season"], errors="coerce").astype("Int64")

    # ---- Step 5: Standardise team names ----
    team_text_cols = ["team1", "team2", "toss_winner", "winner"]
    for col in team_text_cols:
        if col in df.columns:
            df[col] = df[col].map(lambda x: TEAM_NAME_MAP.get(x, x) if pd.notna(x) else x)
            # map(lambda ...): for each value, look it up in TEAM_NAME_MAP.
            # If not found, keep the original (the .get(x, x) default is x itself).

    # ---- Step 6: Standardise venue names ----
    if "venue" in df.columns:
        df["venue"] = df["venue"].map(lambda x: VENUE_NAME_MAP.get(x, x) if pd.notna(x) else x)

    # ---- Step 7: Drop exact duplicate rows ----
    rows_before_dedup = len(df)
    df = df.drop_duplicates()
    duplicates_removed = rows_before_dedup - len(df)

    # ---- Step 8: Keep only the columns the database table needs ----
    missing_cols = [c for c in KEEP_COLUMNS if c not in df.columns]
    if missing_cols:
        print(f"  [WARNING] These expected columns were NOT found in the CSV: {missing_cols}")
        print(f"  Inspect your CSV with inspect_raw_data.py and update COLUMN_MAP.")
    df = df[[c for c in KEEP_COLUMNS if c in df.columns]]

    # ---- Step 9: Drop rows where match_id is null (can't load without a PK) ----
    null_ids = df["match_id"].isna().sum()
    df = df.dropna(subset=["match_id"])

    # ---- Print cleaning report ----
    print_cleaning_report("matches", rows_read, duplicates_removed, null_ids, df)

    # ---- Save cleaned CSV ----
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "matches_clean.csv"
    df.to_csv(out_path, index=False)
    print(f"  Saved cleaned matches to {out_path}")

    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename only the columns that exist; warn about any that are missing."""
    # Only rename columns that are actually present in the DataFrame.
    # This prevents a crash if the CSV has slightly different column names.
    actual_map = {k: v for k, v in COLUMN_MAP.items() if k in df.columns}
    missing    = [k for k in COLUMN_MAP if k not in df.columns]
    if missing:
        print(f"  [WARNING] CSV columns not found (rename skipped): {missing}")
        print(f"  Run inspect_raw_data.py to see the actual column names, then update COLUMN_MAP.")
    return df.rename(columns=actual_map)


def strip_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """Strip leading/trailing whitespace from every text column."""
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    return df


def print_cleaning_report(name, rows_read, duplicates_removed, null_ids_dropped, df):
    """Print a summary of the cleaning process."""
    print(f"\n  ===== CLEANING REPORT: {name} =====")
    print(f"  Rows read              : {rows_read:,}")
    print(f"  Duplicate rows removed : {duplicates_removed:,}")
    print(f"  Rows dropped (null PK) : {null_ids_dropped:,}")
    print(f"  Rows kept              : {len(df):,}")
    print(f"  Nulls per column:")
    for col in df.columns:
        n = df[col].isna().sum()
        print(f"    {col:<20} : {n:,}")
    print(f"  ===================================\n")

