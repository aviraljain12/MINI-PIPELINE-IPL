"""
Purpose : Read both raw CSVs and return them as Pandas DataFrames.
          This is the Extract step of ETL — we pull data out of flat files
          and hand it to the cleaning step.
Reads   : data/raw/ipl_matches.csv
          data/raw/ipl_ball_by_ball.csv
Writes  : nothing (returns DataFrames to the caller)
How to run: imported by run_full_pipeline.py — not run directly
"""

import pandas as pd
from pathlib import Path


# Build the path relative to this file so the script works from any directory.
# Path(__file__).resolve() is the absolute path of this script file.
# .parent.parent is the project root (two levels up from pipeline/).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR      = PROJECT_ROOT / "data" / "raw"

MATCHES_FILE   = RAW_DIR / "ipl_matches.csv"
DELIVERIES_FILE = RAW_DIR / "ipl_ball_by_ball.csv"


def load_raw_matches() -> pd.DataFrame:
    """Read the raw matches CSV and return a DataFrame."""
    _check_file_exists(MATCHES_FILE)
    print(f"[extract] Reading matches from {MATCHES_FILE} ...")
    df = pd.read_csv(MATCHES_FILE)
    print(f"[extract] Matches loaded: {len(df):,} rows × {len(df.columns)} columns")
    return df


def load_raw_deliveries() -> pd.DataFrame:
    """Read the raw ball-by-ball CSV and return a DataFrame."""
    _check_file_exists(DELIVERIES_FILE)
    print(f"[extract] Reading deliveries from {DELIVERIES_FILE} ...")
    # low_memory=False tells pandas to read the full column before deciding its type,
    # avoiding "DtypeWarning: mixed types" on large files.
    df = pd.read_csv(DELIVERIES_FILE, low_memory=False)
    print(f"[extract] Deliveries loaded: {len(df):,} rows × {len(df.columns)} columns")
    return df


def _check_file_exists(path: Path):
    """Raise a clear error if the CSV file is missing."""
    if not path.exists():
        raise FileNotFoundError(
            f"\n\n  File not found: {path}\n"
            f"  Please download it from Kaggle and place it in data/raw/\n"
            f"  Dataset: https://www.kaggle.com/datasets/vedantbhavsar43/"
            f"ipl-2007-to-2026-complete-ball-by-ball-dataset\n"
        )

