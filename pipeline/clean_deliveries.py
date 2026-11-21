"""
Purpose : Clean the raw ball-by-ball (deliveries) DataFrame and return
          a cleaned version ready for the MySQL `deliveries` table.
          This is the Transform step of ETL for the deliveries data.
Reads   : raw deliveries DataFrame (passed in from run_full_pipeline.py)
          also uses the cleaned matches DataFrame to validate match_ids
Writes  : data/processed/deliveries_clean.csv
How to run: imported by run_full_pipeline.py — not run directly

CLEANING STEPS APPLIED:
  1. Strip whitespace from all text columns.
  2. Rename raw CSV columns → database column names.
  3. Cast numeric columns (innings, over_no, ball_no, runs, is_wicket) to int.
  4. Standardise team names using TEAM_NAME_MAP (batting_team, bowling_team).
  5. Drop exact duplicate rows.
  6. Remove deliveries whose match_id is NOT in the matches table (FK safety).
  7. Create is_legal_ball flag (1 if not a wide, 0 if wide).
  8. Print a cleaning report and save the cleaned CSV.

IMPORTANT — COLUMN NAMES:
  Run inspect_raw_data.py FIRST and update COLUMN_MAP to match your CSV.
  The names below are common for this Kaggle dataset but are NOT guaranteed.
"""

import pandas as pd
from pathlib import Path
from pipeline.team_and_venue_name_fixes import TEAM_NAME_MAP

PROJECT_ROOT  = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


# Map raw CSV column name → our database column name.
# Left  = exact column name in ipl_ball_by_ball.csv (confirmed by inspect_raw_data.py).
# Right = column name in the MySQL `deliveries` table.
# VERIFIED against the real CSV output from inspect_raw_data.py.
COLUMN_MAP: dict[str, str] = {
    "match_id":      "match_id",       # links to matches.match_id (already correctly named)
    "innings":       "innings",        # 1 or 2 (already correctly named)
    "batting_team":  "batting_team",   # team currently batting (already correctly named)
    "bowling_team":  "bowling_team",   # team currently bowling (already correctly named)
    "over":          "over_no",        # over number 0-indexed (0 = first over, 19 = last)
    "ball_in_over":  "ball_no",        # ball within the over (1–6, up to 11 for no-balls/wides)
    "batter":        "batter",         # batsman facing the ball (already correctly named)
    "bowler":        "bowler",         # bowler delivering the ball (already correctly named)
    "batter_runs":   "batter_runs",    # runs scored by the batter off this ball
    "total_runs":    "total_runs",     # total runs off this delivery (incl. extras)
    "is_wicket":     "is_wicket",      # 1 = wicket fell, 0 = no wicket (already correctly named)
    "wicket_kind":   "dismissal_kind", # e.g. "caught", "bowled", "run out"
    # 'wides' column (integer) is used to build is_legal_ball — see add_legal_ball_flag()
}

KEEP_COLUMNS = [
    "match_id", "innings", "batting_team", "bowling_team",
    "over_no", "ball_no", "batter", "bowler",
    "batter_runs", "total_runs", "is_wicket", "dismissal_kind",
    "is_legal_ball",  # derived column we create
]


def clean_deliveries(df: pd.DataFrame, clean_matches_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the raw deliveries DataFrame and return the cleaned version.
    clean_matches_df is used to filter out orphan deliveries (no matching match_id).
    Also saves deliveries_clean.csv to data/processed/.
    """
    print("\n[clean_deliveries] Starting cleaning ...")
    rows_read = len(df)

    # ---- Step 1: Strip whitespace ----
    df = strip_whitespace(df)

    # ---- Step 2: Build is_legal_ball BEFORE renaming ----
    # We need the raw column name ("extra_type") before it might be dropped.
    # A wide is an extra delivery that does NOT count as a ball faced by the batter.
    # We want to flag legal balls so strike rate can exclude wides.
    df = add_legal_ball_flag(df)

    # ---- Step 3: Rename columns ----
    df = rename_columns(df)

    # ---- Step 4: Cast numeric columns to proper integer types ----
    int_cols = ["match_id", "innings", "over_no", "ball_no",
                "batter_runs", "total_runs", "is_wicket"]
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
            # Int64 (capital I) is pandas nullable integer — allows NaN unlike numpy int64.

    # ---- Step 5: Standardise team names ----
    for col in ["batting_team", "bowling_team"]:
        if col in df.columns:
            df[col] = df[col].map(lambda x: TEAM_NAME_MAP.get(x, x) if pd.notna(x) else x)

    # ---- Step 6: Drop exact duplicate rows ----
    rows_before_dedup = len(df)
    df = df.drop_duplicates()
    duplicates_removed = rows_before_dedup - len(df)

    # ---- Step 7: Remove deliveries with no matching match_id ----
    # This is critical for the FOREIGN KEY constraint in MySQL.
    # If a delivery's match_id doesn't exist in the matches table, MySQL will reject it.
    valid_match_ids = set(clean_matches_df["match_id"].dropna().astype(int).tolist())
    rows_before_fk  = len(df)
    df = df[df["match_id"].isin(valid_match_ids)]
    orphans_removed = rows_before_fk - len(df)
    print(f"  Orphan deliveries removed (no matching match_id): {orphans_removed:,}")

    # ---- Step 8: Keep only the columns the DB table needs ----
    missing_cols = [c for c in KEEP_COLUMNS if c not in df.columns]
    if missing_cols:
        print(f"  [WARNING] Expected columns not found, they will be skipped: {missing_cols}")
    df = df[[c for c in KEEP_COLUMNS if c in df.columns]]

    # ---- Print cleaning report ----
    print_cleaning_report("deliveries", rows_read, duplicates_removed, orphans_removed, df)

    # ---- Save cleaned CSV ----
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "deliveries_clean.csv"
    df.to_csv(out_path, index=False)
    print(f"  Saved cleaned deliveries to {out_path}")

    return df


def add_legal_ball_flag(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add an is_legal_ball column: 1 if the ball is not a wide, 0 if it is.
    This allows strike-rate queries to count only balls the batter actually faced.

    The real CSV (confirmed by inspect_raw_data.py) has a 'wides' integer column:
      wides = 0  → legal ball (counts as a ball faced by the batter)
      wides > 0  → wide (does NOT count as a ball faced)
    """
    if "wides" in df.columns:
        # wides == 0 evaluates to True (1) for legal balls, False (0) for wides
        df["is_legal_ball"] = (df["wides"] == 0).astype(int)
        print(f"  [INFO] is_legal_ball built from 'wides' column.")
        return df

    # Fallback: check other common column names for wides
    for candidate in ["wide_runs", "extras_type", "extra_type"]:
        if candidate in df.columns:
            if candidate == "wide_runs":
                df["is_legal_ball"] = (df[candidate].fillna(0) == 0).astype(int)
            else:
                df["is_legal_ball"] = (~df[candidate].str.lower().str.strip().eq("wides")).astype(int)
            print(f"  [INFO] is_legal_ball built from column '{candidate}'.")
            return df

    # If no wide column found at all, treat everything as legal (safe fallback)
    print(f"  [INFO] No wide column found. Setting is_legal_ball=1 for all rows.")
    df["is_legal_ball"] = 1
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename only the columns that exist; warn about any that are missing."""
    actual_map = {k: v for k, v in COLUMN_MAP.items() if k in df.columns}
    missing    = [k for k in COLUMN_MAP if k not in df.columns]
    if missing:
        print(f"  [WARNING] CSV columns not found (rename skipped): {missing}")
        print(f"  Run inspect_raw_data.py and update COLUMN_MAP in clean_deliveries.py.")
    return df.rename(columns=actual_map)


def strip_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """Strip leading/trailing whitespace from every text column."""
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    return df


def print_cleaning_report(name, rows_read, duplicates_removed, orphans_removed, df):
    """Print a summary of the cleaning process."""
    print(f"\n  ===== CLEANING REPORT: {name} =====")
    print(f"  Rows read              : {rows_read:,}")
    print(f"  Duplicate rows removed : {duplicates_removed:,}")
    print(f"  Orphan rows removed    : {orphans_removed:,}")
    print(f"  Rows kept              : {len(df):,}")
    print(f"  Nulls per column (top columns):")
    for col in df.columns:
        n = df[col].isna().sum()
        if n > 0:  # only print columns that actually have nulls
            print(f"    {col:<25} : {n:,}")
    print(f"  ===================================\n")

