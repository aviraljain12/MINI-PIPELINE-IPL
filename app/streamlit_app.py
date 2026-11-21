"""
Purpose : ENTRY POINT for the Streamlit dashboard.
          This is the Overview page — the first thing the user sees.
          It shows metric cards (total matches, deliveries, runs, wickets)
          and a bar chart of matches played per season.
          The sidebar lets users navigate to the other pages.
Reads   : MySQL via app/db.py (queries from app/queries.py)
Writes  : nothing (Streamlit renders in the browser)
"""

import streamlit as st
from app.db import run_query
from app import queries

# Page config must be the FIRST Streamlit call in the script
st.set_page_config(
    page_title="IPL Analytics",
    layout="wide",
)

# ---------------------------------------------------------------------------
# PAGE HEADER
# ---------------------------------------------------------------------------
st.title("IPL Cricket Analytics Dashboard")
st.markdown("""
This dashboard is the final serving layer of the IPL data engineering pipeline:

> **Raw CSV -> Pandas (clean) -> MySQL (store) -> SQL (query) -> Streamlit (visualise)**

The underlying dataset covers IPL seasons 2007 to 2026 with ball-by-ball granularity.
Every visualization presents the exact SQL query executed against the database.
""")

st.divider()

# ---------------------------------------------------------------------------
# METRIC CARDS
# ---------------------------------------------------------------------------
st.subheader("Database Summary")

# Run the summary queries
df_matches = run_query(queries.TOTAL_MATCHES)
df_rest = run_query(queries.TOTAL_DELIVERIES_RUNS_WICKETS)

if not df_matches.empty and not df_rest.empty:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Matches", f"{df_matches['total_matches'].iloc[0]:,}")
    with col2:
        st.metric("Total Deliveries", f"{df_rest['total_deliveries'].iloc[0]:,}")
    with col3:
        st.metric("Total Runs", f"{df_rest['total_runs'].iloc[0]:,}")
    with col4:
        st.metric("Total Wickets", f"{df_rest['total_wickets'].iloc[0]:,}")

st.divider()

# ---------------------------------------------------------------------------
# MATCHES PER SEASON CHART
# ---------------------------------------------------------------------------
st.subheader("Matches Played Per Season")

df_seasons = run_query(queries.MATCHES_PER_SEASON)

if not df_seasons.empty:
    df_chart = df_seasons.set_index("season")
    st.bar_chart(df_chart["matches"])

    st.caption("SQL query executed:")
    st.code(queries.MATCHES_PER_SEASON, language="sql")
    st.caption(
        "Groups matches by tournament edition (season year) and aggregates total matches played."
    )

st.divider()
st.caption("Use the sidebar navigation to access Team Performance, Player Leaderboards, and Venue Insights.")
