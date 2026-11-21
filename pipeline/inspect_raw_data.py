"""
Purpose : Inspect the raw CSVs and print a detailed report:
          column names, data types, null counts, sample values,
          distinct team names, distinct venue names.
          Run this BEFORE writing any cleaning code, so you know
          the exact column names in YOUR version of the dataset.
Reads   : data/raw/ipl_matches.csv
          data/raw/ipl_ball_by_ball.csv
Writes  : nothing (output is printed to the terminal)
How to run:
    cd ipl-pipeline
    python -m pipeline.inspect_raw_data
"""

import pandas as pd
from pipeline.extract_raw_csv import load_raw_matches, load_raw_deliveries


def inspect_dataframe(df: pd.DataFrame, name: str):
    """Print shape, dtypes, null counts, and sample values for a DataFrame."""
    print("\n" + "=" * 70)
    print(f"  INSPECTING: {name}")
    print("=" * 70)
    print(f"  Shape: {df.shape[0]:,} rows × {df.shape[1]} columns\n")

    print("  --- Column names, dtypes, null count, sample value ---")
    # Iterate over each column to show its profile
    for col in df.columns:
        null_count = df[col].isna().sum()
        # Get the first non-null value as a sample
        sample = df[col].dropna().iloc[0] if null_count < len(df) else "ALL NULL"
        print(f"  {col:<35} dtype={str(df[col].dtype):<10} "
              f"nulls={null_count:<7} sample={repr(sample)}")


def inspect_distinct_teams(matches_df: pd.DataFrame):
    """Print every distinct team name found in the matches file."""
    print("\n" + "=" * 70)
    print("  DISTINCT TEAM NAMES (from matches file)")
    print("=" * 70)

    # team1, team2, toss_winner, winner are the text columns that hold team names.
    # toss_decision holds "bat"/"field" — not a team name, so we filter by dtype=object
    # AND only pick columns that actually contain team names (not "bat"/"field").
    team_cols = ["team1", "team2", "toss_winner", "winner"]
    team_cols = [c for c in team_cols if c in matches_df.columns]
    print(f"  Columns searched: {team_cols}")

    all_teams = set()
    for col in team_cols:
        if matches_df[col].dtype == object:
            all_teams.update(matches_df[col].dropna().unique().tolist())

    for t in sorted(all_teams):
        print(f"    {t}")


def inspect_distinct_venues(matches_df: pd.DataFrame):
    """Print every distinct venue name found in the matches file."""
    print("\n" + "=" * 70)
    print("  DISTINCT VENUE / CITY NAMES (from matches file)")
    print("=" * 70)

    venue_cols = [c for c in matches_df.columns
                  if any(word in c.lower() for word in ['venue', 'city', 'ground', 'stadium'])]
    print(f"  Columns searched: {venue_cols}")

    for col in venue_cols:
        if matches_df[col].dtype == object:
            venues = sorted(matches_df[col].dropna().unique().tolist())
            print(f"\n  [{col}] — {len(venues)} distinct values:")
            for v in venues:
                print(f"    {v}")


def inspect_over_ball_range(deliveries_df: pd.DataFrame):
    """Print the min/max values for over and ball columns in deliveries."""
    print("\n" + "=" * 70)
    print("  OVER / BALL RANGE CHECK (deliveries file)")
    print("=" * 70)

    # Look for columns that likely represent over number and ball number
    over_cols = [c for c in deliveries_df.columns if 'over' in c.lower()]
    ball_cols = [c for c in deliveries_df.columns if 'ball' in c.lower()]

    for col in over_cols + ball_cols:
        try:
            print(f"  {col:<30} min={deliveries_df[col].min()}  "
                  f"max={deliveries_df[col].max()}")
        except TypeError:
            print(f"  {col:<30} (non-numeric, skipped)")


if __name__ == "__main__":
    matches_df    = load_raw_matches()
    deliveries_df = load_raw_deliveries()

    inspect_dataframe(matches_df,    "ipl_matches.csv")
    inspect_dataframe(deliveries_df, "ipl_ball_by_ball.csv")
    inspect_distinct_teams(matches_df)
    inspect_distinct_venues(matches_df)
    inspect_over_ball_range(deliveries_df)

    print("\n" + "=" * 70)
    print("  INSPECTION COMPLETE")
    print("  Copy the column names above into clean_matches.py and")
    print("  clean_deliveries.py and update COLUMN_MAP dictionaries.")
    print("=" * 70 + "\n")

