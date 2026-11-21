"""
Purpose : ENTRY POINT for the Streamlit dashboard.
          This is the Overview page — the first thing the user sees.
          It shows metric cards (total matches, deliveries, runs, wickets)
          and a bar chart of matches played per season.
          The sidebar lets users navigate to the other pages.
Reads   : MySQL via app/db.py (queries from app/queries.py)
Writes  : nothing (Streamlit renders in the browser)
How to run:
    cd ipl-pipeline
    streamlit run app/streamlit_app.py
    Then open http://localhost:8501 in your browser.
"""

import streamlit as st
from app.db      import run_query
from app import queries

# --- Page config must be the FIRST Streamlit call in the script ---
st.set_page_config(
    page_title="IPL Analytics",
    page_icon="🏏",
    layout="wide",   # use the full width of the browser window
)

# ---------------------------------------------------------------------------
# PAGE HEADER
# ---------------------------------------------------------------------------
st.title("🏏 IPL Cricket Analytics Dashboard")
st.markdown("""
This dashboard is the final step of a mini data-engineering pipeline:

> **Raw CSV → Pandas (clean) → MySQL (store) → SQL (query) → Streamlit (visualise)**

The dataset covers **IPL seasons 2007 – 2026** (ball-by-ball detail).
Every chart on this site shows the SQL query that generated it, so you can
learn what each query does and copy it into MySQL Workbench to experiment.

**Data source:** [Kaggle — IPL 2007 to 2026 Complete Ball-by-Ball Dataset]
(https://www.kaggle.com/datasets/vedantbhavsar43/ipl-2007-to-2026-complete-ball-by-ball-dataset)
""")

st.divider()

# ---------------------------------------------------------------------------
# METRIC CARDS
# ---------------------------------------------------------------------------
st.subheader("📊 Database Summary")

# Run the two summary queries
df_matches  = run_query(queries.TOTAL_MATCHES)
df_rest     = run_query(queries.TOTAL_DELIVERIES_RUNS_WICKETS)

# Only display if we got data back (run_query returns empty df on error)
if not df_matches.empty and not df_rest.empty:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🏟️ Total Matches", f"{df_matches['total_matches'].iloc[0]:,}")
    with col2:
        st.metric("⚾ Total Deliveries", f"{df_rest['total_deliveries'].iloc[0]:,}")
    with col3:
        st.metric("🏃 Total Runs", f"{df_rest['total_runs'].iloc[0]:,}")
    with col4:
        st.metric("🎯 Total Wickets", f"{df_rest['total_wickets'].iloc[0]:,}")

st.divider()

# ---------------------------------------------------------------------------
# MATCHES PER SEASON CHART
# ---------------------------------------------------------------------------
st.subheader("📅 Matches Played Per Season")

df_seasons = run_query(queries.MATCHES_PER_SEASON)

if not df_seasons.empty:
    # Set season as the index so Streamlit uses it as the x-axis label
    df_chart = df_seasons.set_index("season")
    st.bar_chart(df_chart["matches"])

    # Show the SQL and explain what it does — educational feature
    st.caption("**SQL behind this chart:**")
    st.code(queries.MATCHES_PER_SEASON, language="sql")
    st.caption(
        "This query groups every match by its season year and counts how many "
        "matches were played in each season."
    )

st.divider()
st.caption("Use the sidebar ← to navigate to Team Performance, Player Leaderboards, or Venue Insights.")

