"""
Purpose : Store every SQL query used by the dashboard as a named constant.
          Keeping queries here (not inside the page files) means:
          - One place to edit when you change a query.
          - Easy to review all queries at once.
          - Every query is shown to the user in the dashboard with st.code().
Reads   : nothing (pure string constants)
Writes  : nothing
How to run: imported by streamlit_app.py and pages/*.py — not run directly

SQL CONCEPTS TAUGHT (see the README for the full list):
  - GROUP BY, COUNT           : MATCHES_PER_SEASON
  - WHERE, ORDER BY DESC      : WINS_BY_TEAM
  - Conditional aggregation   : TOSS_WIN_PCT
  - SUM + JOIN + LIMIT        : TOP_RUN_SCORERS_BY_SEASON
  - NOT IN filter             : TOP_WICKET_TAKERS
  - HAVING clause             : BEST_STRIKE_RATES
  - CTE + JOIN + HAVING       : AVG_FIRST_INNINGS_SCORE_BY_VENUE
  - Window function RANK()    : TOP_SCORER_PER_SEASON
"""


# ---------------------------------------------------------------------------
# OVERVIEW PAGE QUERIES
# ---------------------------------------------------------------------------

# [COUNT *] — total number of matches in the database
TOTAL_MATCHES = """
SELECT COUNT(*) AS total_matches
FROM matches
"""

# [COUNT *, SUM] — total deliveries, total runs scored, total wickets
TOTAL_DELIVERIES_RUNS_WICKETS = """
SELECT
    COUNT(*)        AS total_deliveries,
    SUM(total_runs) AS total_runs,
    SUM(is_wicket)  AS total_wickets
FROM deliveries
"""

# [GROUP BY, COUNT] — number of matches played in each IPL season
# Concept: GROUP BY collapses all rows with the same season into one row,
# and COUNT(*) counts how many rows were in each group.
MATCHES_PER_SEASON = """
SELECT
    season,
    COUNT(*) AS matches
FROM matches
GROUP BY season
ORDER BY season
"""


# ---------------------------------------------------------------------------
# TEAM PERFORMANCE PAGE QUERIES
# ---------------------------------------------------------------------------

# [WHERE, GROUP BY, ORDER BY DESC] — number of wins per team, all time
# WHERE winner IS NOT NULL excludes no-result matches (they have no winner).
WINS_BY_TEAM = """
SELECT
    winner,
    COUNT(*) AS wins
FROM matches
WHERE winner IS NOT NULL
GROUP BY winner
ORDER BY wins DESC
"""

# [WHERE, GROUP BY, ORDER BY DESC] — number of wins per team in a chosen season
# :season is a parameter — the actual value is passed safely by Python.
# This prevents SQL injection: we never paste user input into the SQL string.
WINS_BY_TEAM_SEASON = """
SELECT
    winner,
    COUNT(*) AS wins
FROM matches
WHERE winner IS NOT NULL
  AND season = :season
GROUP BY winner
ORDER BY wins DESC
"""

# [Conditional aggregation] — what percentage of the time does the toss winner also win the match?
# SUM(toss_winner = winner) counts rows where both columns are equal (MySQL returns 1 for TRUE).
TOSS_WIN_PCT = """
SELECT
    ROUND(
        100.0 * SUM(toss_winner = winner) / COUNT(*),
        1
    ) AS toss_winner_won_pct
FROM matches
WHERE winner IS NOT NULL
"""

# [Conditional aggregation, GROUP BY] — toss win % broken down by toss decision (bat/field)
TOSS_WIN_PCT_BY_DECISION = """
SELECT
    toss_decision,
    COUNT(*)                                              AS matches,
    ROUND(100.0 * SUM(toss_winner = winner) / COUNT(*), 1) AS toss_winner_won_pct
FROM matches
WHERE winner IS NOT NULL
  AND toss_decision IS NOT NULL
GROUP BY toss_decision
ORDER BY toss_winner_won_pct DESC
"""


# ---------------------------------------------------------------------------
# PLAYER LEADERBOARDS PAGE QUERIES
# ---------------------------------------------------------------------------

# [SUM, JOIN, GROUP BY, ORDER BY, LIMIT] — top 10 run scorers in a chosen season
# JOIN connects each delivery to its match so we can filter by season.
# :season is a parameterised placeholder — never paste user input directly into SQL.
TOP_RUN_SCORERS_BY_SEASON = """
SELECT
    d.batter,
    SUM(d.batter_runs) AS runs
FROM deliveries d
JOIN matches m ON m.match_id = d.match_id
WHERE m.season = :season
GROUP BY d.batter
ORDER BY runs DESC
LIMIT 10
"""

# [COUNT, NOT IN, GROUP BY, ORDER BY, LIMIT] — all-time top wicket takers
# NOT IN excludes dismissals where the bowler doesn't get credit:
#   run out, retired hurt, obstructing the field.
TOP_WICKET_TAKERS = """
SELECT
    bowler,
    COUNT(*) AS wickets
FROM deliveries
WHERE is_wicket = 1
  AND dismissal_kind NOT IN ('run out', 'retired hurt', 'obstructing the field')
GROUP BY bowler
ORDER BY wickets DESC
LIMIT 10
"""

# [SUM, COUNT, HAVING, ORDER BY] — best batting strike rates (minimum 500 legal balls faced)
# HAVING filters AFTER GROUP BY, unlike WHERE which filters before grouping.
# We only count is_legal_ball = 1 so wides are not counted as balls faced.
BEST_STRIKE_RATES = """
SELECT
    batter,
    SUM(batter_runs)                                             AS runs,
    SUM(is_legal_ball)                                           AS balls_faced,
    ROUND(100.0 * SUM(batter_runs) / NULLIF(SUM(is_legal_ball), 0), 1) AS strike_rate
FROM deliveries
GROUP BY batter
HAVING SUM(is_legal_ball) >= 500
ORDER BY strike_rate DESC
LIMIT 10
"""
# NULLIF(SUM(is_legal_ball), 0) prevents division-by-zero:
# if balls_faced is 0, NULLIF returns NULL, and dividing by NULL gives NULL (not a crash).


# ---------------------------------------------------------------------------
# VENUE INSIGHTS PAGE QUERIES
# ---------------------------------------------------------------------------

# [CTE, SUM, AVG, JOIN, GROUP BY, HAVING, ORDER BY] — average first innings score by venue
# A CTE (Common Table Expression, the WITH clause) first calculates the total score
# for each match's first innings, then we average those scores per venue.
# HAVING COUNT(*) >= 10 filters out venues with fewer than 10 matches (too few to be meaningful).
AVG_FIRST_INNINGS_SCORE_BY_VENUE = """
WITH innings_totals AS (
    SELECT
        match_id,
        SUM(total_runs) AS score
    FROM deliveries
    WHERE innings = 1
    GROUP BY match_id
)
SELECT
    m.venue,
    ROUND(AVG(i.score), 1) AS avg_first_innings_score,
    COUNT(*)               AS matches_played
FROM innings_totals i
JOIN matches m ON m.match_id = i.match_id
GROUP BY m.venue
HAVING COUNT(*) >= 10
ORDER BY avg_first_innings_score DESC
"""

# [Window function RANK() OVER PARTITION BY] — highest run scorer in each IPL season
# Window functions are a MySQL 8+ feature. They let us rank rows within a group
# without collapsing the group into one row (unlike GROUP BY).
# PARTITION BY season means: restart the ranking for each new season.
# ORDER BY runs DESC means: rank 1 goes to the player with the most runs.
TOP_SCORER_PER_SEASON = """
WITH season_totals AS (
    SELECT
        m.season,
        d.batter,
        SUM(d.batter_runs) AS runs
    FROM deliveries d
    JOIN matches m ON m.match_id = d.match_id
    GROUP BY m.season, d.batter
),
ranked AS (
    SELECT
        season,
        batter,
        runs,
        RANK() OVER (PARTITION BY season ORDER BY runs DESC) AS season_rank
    FROM season_totals
)
SELECT
    season,
    batter,
    runs
FROM ranked
WHERE season_rank = 1
ORDER BY season
"""

