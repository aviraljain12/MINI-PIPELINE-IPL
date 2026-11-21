"""
Purpose : Team Performance page of the IPL dashboard.
          Shows wins by team (all time and by season) and toss statistics.
Reads   : MySQL via app/db.py (queries from app/queries.py)
Writes  : nothing
"""

import streamlit as st
from app.db import run_query
from app import queries

st.set_page_config(page_title="Team Performance", layout="wide")

st.title("Team Performance")
st.markdown("All-time franchise wins, season-specific performance, and toss outcome statistics.")

st.divider()

# ---------------------------------------------------------------------------
# SIDEBAR — Season filter
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")

df_seasons = run_query(queries.MATCHES_PER_SEASON)
if not df_seasons.empty:
    seasons = df_seasons["season"].tolist()
    chosen_season = st.sidebar.selectbox("Select Season", seasons, index=len(seasons) - 1)
else:
    chosen_season = None

st.divider()

# ---------------------------------------------------------------------------
# SECTION 1: ALL-TIME WINS BY TEAM
# ---------------------------------------------------------------------------
st.subheader("All-Time Wins by Team")

df_wins = run_query(queries.WINS_BY_TEAM)

if not df_wins.empty:
    df_chart = df_wins.set_index("winner")
    st.bar_chart(df_chart["wins"])
    st.dataframe(df_wins, use_container_width=True)

    st.caption("SQL query executed:")
    st.code(queries.WINS_BY_TEAM, language="sql")
    st.caption(
        "Aggregates match victories per franchise. Excludes no-result encounters where winner is NULL."
    )

st.divider()

# ---------------------------------------------------------------------------
# SECTION 2: WINS BY TEAM — CHOSEN SEASON
# ---------------------------------------------------------------------------
if chosen_season is not None:
    st.subheader(f"Wins by Team - Season {chosen_season}")

    df_wins_season = run_query(queries.WINS_BY_TEAM_SEASON, params={"season": chosen_season})

    if not df_wins_season.empty:
        df_chart2 = df_wins_season.set_index("winner")
        st.bar_chart(df_chart2["wins"])
        st.dataframe(df_wins_season, use_container_width=True)

        st.caption("SQL query executed:")
        st.code(queries.WINS_BY_TEAM_SEASON, language="sql")
        st.caption(
            f"Evaluates team victories restricted to the {chosen_season} season using parameter binding."
        )
    else:
        st.info(f"No win data available for season {chosen_season}.")

st.divider()

# ---------------------------------------------------------------------------
# SECTION 3: TOSS STATISTICS
# ---------------------------------------------------------------------------
st.subheader("Toss Impact Analysis")

df_toss_pct = run_query(queries.TOSS_WIN_PCT)
if not df_toss_pct.empty:
    pct = df_toss_pct["toss_winner_won_pct"].iloc[0]
    st.metric(
        label="Percentage of matches won by toss winner",
        value=f"{pct}%"
    )

df_toss_decision = run_query(queries.TOSS_WIN_PCT_BY_DECISION)
if not df_toss_decision.empty:
    st.markdown("**Win rate segregated by toss decision (batting vs. fielding first):**")
    st.dataframe(df_toss_decision, use_container_width=True)

    st.caption("SQL query executed:")
    st.code(queries.TOSS_WIN_PCT_BY_DECISION, language="sql")
    st.caption(
        "Employs conditional aggregation (SUM(toss_winner = winner)) grouped by the strategic decision."
    )
