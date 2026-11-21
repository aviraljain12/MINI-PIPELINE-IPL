"""
Purpose : Team Performance page of the IPL dashboard.
          Shows wins by team (all time and by season) and toss statistics.
          The file name "1_Team_Performance.py" becomes "Team Performance"
          in the Streamlit sidebar — that's how Streamlit's multi-page system works.
Reads   : MySQL via app/db.py (queries from app/queries.py)
Writes  : nothing
How to run: automatically loaded by Streamlit from the pages/ folder.
            Run: streamlit run app/streamlit_app.py
"""

import streamlit as st
from app.db      import run_query
from app import queries

st.set_page_config(page_title="Team Performance", page_icon="🏆", layout="wide")

st.title("🏆 Team Performance")
st.markdown("All-time wins, season wins, and toss statistics for every IPL team.")

st.divider()

# ---------------------------------------------------------------------------
# SIDEBAR — Season filter
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")

# Get the list of available seasons to populate the dropdown
df_seasons = run_query(queries.MATCHES_PER_SEASON)
if not df_seasons.empty:
    seasons = df_seasons["season"].tolist()
    # selectbox lets the user pick one value from a list
    chosen_season = st.sidebar.selectbox("Select Season", seasons, index=len(seasons) - 1)
else:
    chosen_season = None

st.divider()

# ---------------------------------------------------------------------------
# SECTION 1: ALL-TIME WINS BY TEAM
# ---------------------------------------------------------------------------
st.subheader("🥇 All-Time Wins by Team")

df_wins = run_query(queries.WINS_BY_TEAM)

if not df_wins.empty:
    df_chart = df_wins.set_index("winner")
    st.bar_chart(df_chart["wins"])

    # Show the full data table below the chart
    st.dataframe(df_wins, use_container_width=True)

    st.caption("**SQL behind this chart:**")
    st.code(queries.WINS_BY_TEAM, language="sql")
    st.caption(
        "Groups all matches by the winning team and counts wins. "
        "WHERE winner IS NOT NULL excludes no-result matches that have no winner."
    )

st.divider()

# ---------------------------------------------------------------------------
# SECTION 2: WINS BY TEAM — CHOSEN SEASON
# ---------------------------------------------------------------------------
if chosen_season is not None:
    st.subheader(f"📅 Wins by Team — Season {chosen_season}")

    # Pass chosen_season as a parameter — NEVER build the SQL string with f-string season values.
    # Parameterised queries prevent SQL injection attacks.
    df_wins_season = run_query(queries.WINS_BY_TEAM_SEASON, params={"season": chosen_season})

    if not df_wins_season.empty:
        df_chart2 = df_wins_season.set_index("winner")
        st.bar_chart(df_chart2["wins"])
        st.dataframe(df_wins_season, use_container_width=True)

        st.caption("**SQL behind this chart:**")
        st.code(queries.WINS_BY_TEAM_SEASON, language="sql")
        st.caption(
            f"Same as above but filtered to season {chosen_season}. "
            "The :season placeholder is replaced safely by the Python parameter."
        )
    else:
        st.info(f"No win data found for season {chosen_season}.")

st.divider()

# ---------------------------------------------------------------------------
# SECTION 3: TOSS STATISTICS
# ---------------------------------------------------------------------------
st.subheader("🪙 Does Winning the Toss Help?")

df_toss_pct = run_query(queries.TOSS_WIN_PCT)
if not df_toss_pct.empty:
    pct = df_toss_pct["toss_winner_won_pct"].iloc[0]
    st.metric(
        label="% of matches won by the toss winner",
        value=f"{pct}%",
        help="If this is close to 50%, the toss doesn't help much."
    )

df_toss_decision = run_query(queries.TOSS_WIN_PCT_BY_DECISION)
if not df_toss_decision.empty:
    st.markdown("**Win % by toss decision:**")
    st.dataframe(df_toss_decision, use_container_width=True)

    st.caption("**SQL behind this table:**")
    st.code(queries.TOSS_WIN_PCT_BY_DECISION, language="sql")
    st.caption(
        "Uses conditional aggregation: SUM(toss_winner = winner) counts rows where "
        "the toss winner also won the match (MySQL evaluates the comparison as 0 or 1)."
    )

