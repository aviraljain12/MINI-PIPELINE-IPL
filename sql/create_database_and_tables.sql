-- =============================================================================
-- File    : sql/create_database_and_tables.sql
-- Purpose : Create the ipl_db database and its two tables from scratch.
--           This file is designed to be RE-RUNNABLE: running it twice gives
--           the same result, not an error. The DROP TABLE / DROP DATABASE
--           statements ensure a clean slate every time.
-- How to run: executed automatically by pipeline/create_tables.py
--             You can also run it manually in MySQL Workbench or the CLI.
-- =============================================================================

-- Create the database if it doesn't already exist.
-- CHARACTER SET utf8mb4 supports all Unicode characters (including emoji, etc.)
CREATE DATABASE IF NOT EXISTS ipl_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Switch to the ipl_db database for all following statements.
USE ipl_db;

-- Drop deliveries FIRST because it has a FOREIGN KEY pointing to matches.
-- MySQL will refuse to drop matches while deliveries still references it.
DROP TABLE IF EXISTS deliveries;
DROP TABLE IF EXISTS matches;

-- =============================================================================
-- TABLE: matches
-- One row per IPL match.
-- match_id is the PRIMARY KEY — it uniquely identifies each match.
-- =============================================================================
CREATE TABLE matches (
  match_id      BIGINT       PRIMARY KEY,   -- unique match number from the dataset
  season        INT,                        -- IPL season year (e.g. 2008, 2024)
  match_date    DATE,                       -- date the match was played
  venue         VARCHAR(120),               -- stadium name
  city          VARCHAR(60),                -- city where match was played
  team1         VARCHAR(60),                -- one of the two competing teams
  team2         VARCHAR(60),                -- the other competing team
  toss_winner   VARCHAR(60),                -- team that won the toss
  toss_decision VARCHAR(10),                -- "bat" or "field"
  winner        VARCHAR(60)                 -- winning team (NULL for no-result matches)
);

-- Index on season makes GROUP BY season and WHERE season = X much faster.
-- Without an index, MySQL must scan every row to find matches for a season.
CREATE INDEX idx_matches_season ON matches(season);


-- =============================================================================
-- TABLE: deliveries
-- One row per ball bowled (a "delivery").
-- A PRIMARY KEY (delivery_id) is auto-assigned because the raw data has no
-- natural unique key for each individual ball.
-- The FOREIGN KEY on match_id ensures every delivery belongs to a real match —
-- MySQL will reject any delivery row whose match_id is not in the matches table.
-- =============================================================================
CREATE TABLE deliveries (
  delivery_id    BIGINT       AUTO_INCREMENT PRIMARY KEY,  -- surrogate PK, auto-assigned
  match_id       BIGINT       NOT NULL,                    -- links to matches.match_id
  innings        INT,                                      -- 1 (first innings) or 2 (second)
  batting_team   VARCHAR(60),                              -- team batting this over
  bowling_team   VARCHAR(60),                              -- team bowling this over
  over_no        INT,                                      -- over number (0 = first over, 19 = last)
  ball_no        INT,                                      -- ball within the over (1–6+)
  batter         VARCHAR(80),                              -- name of the batsman on strike
  bowler         VARCHAR(80),                              -- name of the bowler
  batter_runs    INT,                                      -- runs scored by the batter off this ball
  total_runs     INT,                                      -- total runs (batter + extras) this delivery
  is_wicket      TINYINT,                                  -- 1 = a wicket fell, 0 = no wicket
  dismissal_kind VARCHAR(30),                              -- e.g. "caught", "bowled", "run out"
  is_legal_ball  TINYINT,                                  -- 1 = not a wide (counts as ball faced), 0 = wide

  -- FOREIGN KEY constraint: match_id must exist in matches.match_id.
  -- This prevents "orphan" deliveries (data for a match we know nothing about).
  FOREIGN KEY (match_id) REFERENCES matches(match_id)
);

-- Index on match_id speeds up JOIN queries between deliveries and matches.
CREATE INDEX idx_deliveries_match_id ON deliveries(match_id);

-- Index on batter speeds up "top scorers" and "strike rate" queries.
CREATE INDEX idx_deliveries_batter ON deliveries(batter);

-- Index on bowler speeds up "top wicket-takers" queries.
CREATE INDEX idx_deliveries_bowler ON deliveries(bowler);

-- =============================================================================
-- END OF FILE
-- =============================================================================

