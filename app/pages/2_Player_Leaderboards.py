"""
Purpose : Player Leaderboards page of the IPL dashboard.
          Shows top run scorers, top wicket-takers, and best strike rates.
          A season selector in the sidebar filters the run scorer leaderboard.
          The file name "2_Player_Leaderboards.py" becomes "Player Leaderboards"
          in the Streamlit sidebar.
Reads   : MySQL via app/db.py (queries from app/queries.py)
Writes  : nothing
How to run: automatically loaded by Streamlit from the pages/ folder.
            Run: streamlit run app/streamlit_app.py
"""

import streamlit as st
from app.db      import run_query
from app import queries

st.set_page_config(page_title="Player Leaderboards", page_icon="🏅", layout="wide")

st.title("🏅 Player Leaderboards")
st.markdown("Top batters, bowlers, and strike rates across all IPL seasons.")

st.divider()

# ---------------------------------------------------------------------------
# SIDEBAR — Season filter for run scorers
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")

df_seasons = run_query(queries.MATCHES_PER_SEASON)
if not df_seasons.empty:
    seasons       = df_seasons["season"].tolist()
    chosen_season = st.sidebar.selectbox("Season (for run scorers)", seasons, index=len(seasons) - 1)
else:
    chosen_season = None

# ---------------------------------------------------------------------------
# SECTION 1: TOP RUN SCORERS — CHOSEN SEASON
# ---------------------------------------------------------------------------
if chosen_season is not None:
    st.subheader(f"🏏 Top 10 Run Scorers — Season {chosen_season}")

    df_runs = run_query(queries.TOP_RUN_SCORERS_BY_SEASON, params={"season": chosen_season})

    if not df_runs.empty:
        df_chart = df_runs.set_index("batter")
        st.bar_chart(df_chart["runs"])
        st.dataframe(df_runs, use_container_width=True)

        st.caption("**SQL behind this chart:**")
        st.code(queries.TOP_RUN_SCORERS_BY_SEASON, language="sql")
        st.caption(
            f"JOINs deliveries with matches to filter by season {chosen_season}, "
            "then sums batter_runs per player and takes the top 10."
        )
    else:
        st.info(f"No run scorer data for season {chosen_season}.")

st.divider()

# ---------------------------------------------------------------------------
# SECTION 2: ALL-TIME TOP WICKET TAKERS
# ---------------------------------------------------------------------------
st.subheader("🎯 All-Time Top 10 Wicket Takers")

df_wkt = run_query(queries.TOP_WICKET_TAKERS)

if not df_wkt.empty:
    df_chart2 = df_wkt.set_index("bowler")
    st.bar_chart(df_chart2["wickets"])
    st.dataframe(df_wkt, use_container_width=True)

    st.caption("**SQL behind this chart:**")
    st.code(queries.TOP_WICKET_TAKERS, language="sql")
    st.caption(
        "Counts only rows where is_wicket=1 and the dismissal_kind is NOT one of the "
        "types where the bowler doesn't get credit (run out, retired hurt, etc.)."
    )

st.divider()

# ---------------------------------------------------------------------------
# SECTION 3: BEST STRIKE RATES
# ---------------------------------------------------------------------------
st.subheader("⚡ Best Career Strike Rates (min. 500 legal balls faced)")

df_sr = run_query(queries.BEST_STRIKE_RATES)

if not df_sr.empty:
    df_chart3 = df_sr.set_index("batter")
    st.bar_chart(df_chart3["strike_rate"])
    st.dataframe(df_sr, use_container_width=True)

    st.caption("**SQL behind this chart:**")
    st.code(queries.BEST_STRIKE_RATES, language="sql")
    st.caption(
        "HAVING SUM(is_legal_ball) >= 500 filters out players with too few balls "
        "(a player who faced 10 balls and hit 2 sixes would have SR 200, which is misleading). "
        "Only legal balls (not wides) are counted in balls_faced."
    )

