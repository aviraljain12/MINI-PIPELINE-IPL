"""
Purpose : Venue Insights page of the IPL dashboard.
          Shows average first-innings score per venue and the leading run scorer
          in each IPL season.
Reads   : MySQL via app/db.py (queries from app/queries.py)
Writes  : nothing
"""

import streamlit as st
from app.db import run_query
from app import queries

st.set_page_config(page_title="Venue Insights", layout="wide")

st.title("Venue Insights")
st.markdown("First-innings stadium scoring distributions and seasonal leading run scorers.")

st.divider()

# ---------------------------------------------------------------------------
# SECTION 1: AVERAGE FIRST INNINGS SCORE BY VENUE
# ---------------------------------------------------------------------------
st.subheader("Average First-Innings Score by Venue")
st.caption("Venues hosting a minimum of 10 matches are displayed.")

df_venue = run_query(queries.AVG_FIRST_INNINGS_SCORE_BY_VENUE)

if not df_venue.empty:
    df_chart = df_venue.copy()
    df_chart["venue"] = df_chart["venue"].str.slice(0, 35)
    df_chart = df_chart.set_index("venue")

    st.bar_chart(df_chart["avg_first_innings_score"])
    st.dataframe(df_venue, use_container_width=True)

    st.caption("SQL query executed:")
    st.code(queries.AVG_FIRST_INNINGS_SCORE_BY_VENUE, language="sql")
    st.caption(
        "Utilizes a Common Table Expression (CTE) to calculate match first-innings sums before venue averaging."
    )

st.divider()

# ---------------------------------------------------------------------------
# SECTION 2: TOP SCORER PER SEASON (window function)
# ---------------------------------------------------------------------------
st.subheader("Leading Run Scorer Per Season (Orange Cap)")
st.markdown(
    "Computed using a MySQL 8 window ranking function: `RANK() OVER (PARTITION BY season ORDER BY runs DESC)`."
)

df_top = run_query(queries.TOP_SCORER_PER_SEASON)

if not df_top.empty:
    st.dataframe(df_top, use_container_width=True)

    st.caption("SQL query executed:")
    st.code(queries.TOP_SCORER_PER_SEASON, language="sql")
    st.caption(
        "Applies a window function over seasonal partitions to identify the rank-1 run scorer for each edition."
    )
