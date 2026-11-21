"""
Purpose : Venue Insights page of the IPL dashboard.
          Shows average first-innings score per venue and the top run scorer
          in each IPL season (uses a window function query).
          The file name "3_Venue_Insights.py" becomes "Venue Insights"
          in the Streamlit sidebar.
Reads   : MySQL via app/db.py (queries from app/queries.py)
Writes  : nothing
How to run: automatically loaded by Streamlit from the pages/ folder.
            Run: streamlit run app/streamlit_app.py
"""

import streamlit as st
from app.db      import run_query
from app import queries

st.set_page_config(page_title="Venue Insights", page_icon="🏟️", layout="wide")

st.title("🏟️ Venue Insights")
st.markdown(
    "Average first-innings scores by venue and the leading run scorer "
    "in every IPL season."
)

st.divider()

# ---------------------------------------------------------------------------
# SECTION 1: AVERAGE FIRST INNINGS SCORE BY VENUE
# ---------------------------------------------------------------------------
st.subheader("🏏 Average First-Innings Score by Venue")
st.caption("Only venues with 10 or more matches are shown.")

df_venue = run_query(queries.AVG_FIRST_INNINGS_SCORE_BY_VENUE)

if not df_venue.empty:
    # Truncate long venue names for readability on the chart
    df_chart = df_venue.copy()
    df_chart["venue"] = df_chart["venue"].str.slice(0, 35)   # keep first 35 characters
    df_chart = df_chart.set_index("venue")

    st.bar_chart(df_chart["avg_first_innings_score"])
    st.dataframe(df_venue, use_container_width=True)

    st.caption("**SQL behind this chart:**")
    st.code(queries.AVG_FIRST_INNINGS_SCORE_BY_VENUE, language="sql")
    st.caption(
        "Uses a CTE (WITH clause) to first calculate each match's first-innings total, "
        "then JOINs with matches to get the venue name, and averages the totals per venue. "
        "HAVING COUNT(*) >= 10 removes venues with too few matches for a reliable average."
    )

st.divider()

# ---------------------------------------------------------------------------
# SECTION 2: TOP SCORER PER SEASON (window function)
# ---------------------------------------------------------------------------
st.subheader("🏆 Orange Cap — Top Run Scorer Per Season")
st.markdown(
    "Uses a **window function** (`RANK() OVER PARTITION BY season`) — "
    "a MySQL 8+ feature that ranks batters within each season without collapsing the rows."
)

df_top = run_query(queries.TOP_SCORER_PER_SEASON)

if not df_top.empty:
    st.dataframe(df_top, use_container_width=True)

    st.caption("**SQL behind this table:**")
    st.code(queries.TOP_SCORER_PER_SEASON, language="sql")
    st.caption(
        "Two CTEs are used: the first sums runs per (season, batter) pair; "
        "the second uses RANK() OVER (PARTITION BY season ORDER BY runs DESC) to assign "
        "rank 1 to the top scorer in each season. The outer query keeps only rank = 1."
    )

