# MINI PIPELINE IPL: End-to-End Cricket Analytics Data Pipeline

## Overview

MINI PIPELINE IPL is an end-to-end data engineering pipeline and analytics system designed to extract, transform, normalize, and serve Indian Premier League (IPL) match and ball-by-ball delivery datasets spanning from 2007 through 2026.

The architecture ingests high-volume semi-structured CSV datasets, applies validation and entity standardization rules via Pandas, loads normalized records into a MySQL 8 relational schema with foreign key constraints and targeted indexing, and exposes analytical data through parameterized SQL queries within a multi-page Streamlit interface.

---

## Architectural Design

The data platform follows a decoupled, three-tier architecture:

1. **Ingestion & Processing Layer (ETL Engine)**:
   Extracts raw delivery and match records, enforces schema definitions, rectifies data anomalies (multi-year season notations, historical franchise rebrands, stadium naming discrepancies), derives domain-specific metrics, and performs idempotent batch loading.
2. **Persistence Layer (Relational Data Warehouse)**:
   A normalized MySQL 8 database enforcing Third Normal Form (3NF) between match summaries and individual delivery events. Referential integrity is strictly maintained via foreign keys, with composite indexing implemented to optimize analytical aggregations.
3. **Serving & Analytics Layer (Streamlit & SQLAlchemy)**:
   A web-based analytical application executing pre-compiled SQL queries with connection pooling, caching strategies, and interactive data visualization.

---

## Data Ingestion & Transformation Engineering

The raw dataset comprises two primary sources:
* Match summary records (1,212 matches across 18 tournament editions).
* Granular delivery events (288,226 recorded deliveries across 34 raw attributes).

### Transformation Rules Applied

* **Entity Resolution and Normalization**:
  Franchises subject to historical rebranding (e.g., Delhi Daredevils to Delhi Capitals, Kings XI Punjab to Punjab Kings, Royal Challengers Bangalore to Royal Challengers Bengaluru) are standardized to unified entities without conflating distinct franchises (such as Deccan Chargers and Sunrisers Hyderabad). Venue nomenclature is mapped across historical naming conventions to canonical stadium identifiers.
* **Temporal Discrepancy Rectification**:
  Multi-year seasonal representations (e.g., `2007/08`, `2009/10`, `2020/21`) are parsed via regular expression pattern extraction to isolate canonical calendar years as strict integer types.
* **Domain Feature Derivation (`is_legal_ball`)**:
  Cricket batting metrics require discriminating balls faced from illegal deliveries. The transformation engine computes a binary indicator (`is_legal_ball`) based on wide-ball classifications, ensuring strike rates accurately reflect deliveries where the batter was legitimately on strike.
* **Integrity Validation & Orphan Prevention**:
  Before database ingestion, foreign key integrity is verified by performing set-membership validation between delivery `match_id` references and verified match identifiers, preventing insertion violations.
* **Null Handling Standards**:
  No-result encounters retain an explicit `NULL` state for match winners rather than fabricated imputation. Similarly, deliveries without dismissals retain `NULL` for dismissal categorization.

---

## Relational Schema & Optimization Strategy

The relational schema splits flat ball-by-ball delivery records into two interconnected tables to eliminate 34-column data duplication across 288,000+ records.

### Schema Definitions

```sql
CREATE TABLE matches (
    match_id BIGINT PRIMARY KEY,
    season INT,
    match_date DATE,
    venue VARCHAR(120),
    city VARCHAR(60),
    team1 VARCHAR(60),
    team2 VARCHAR(60),
    toss_winner VARCHAR(60),
    toss_decision VARCHAR(10),
    winner VARCHAR(60)
);

CREATE TABLE deliveries (
    delivery_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    match_id BIGINT NOT NULL,
    innings INT,
    batting_team VARCHAR(60),
    bowling_team VARCHAR(60),
    over_no INT,
    ball_no INT,
    batter VARCHAR(80),
    bowler VARCHAR(80),
    batter_runs INT,
    total_runs INT,
    is_wicket TINYINT,
    dismissal_kind VARCHAR(30),
    is_legal_ball TINYINT,
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
);
```

### Indexing Strategy

To maintain sub-second query performance over high-cardinality tables:
* `idx_matches_season`: Eliminates full-table scans for seasonal partitioning and filtering.
* `idx_deliveries_match_id`: Accelerates join operations between delivery events and match dimensions.
* `idx_deliveries_batter`: Optimizes high-frequency grouping operations for player-level batting performance and cumulative run totals.
* `idx_deliveries_bowler`: Accelerates aggregation filters for bowling strike rates and wicket-taker rankings.

---

## Analytical SQL Query Layer

The analytical interface relies on strict parameterized SQL queries to safeguard against SQL injection and optimize execution plan reuse in MySQL. Core analytical constructs include:

1. **Window Ranking Functions**:
   Utilizes `RANK() OVER (PARTITION BY season ORDER BY runs DESC)` within Common Table Expressions (CTEs) to extract leading run scorers (Orange Cap holders) across all tournament editions in a single scan.
2. **Common Table Expressions (CTEs)**:
   Aggregates first-innings totals per match before computing stadium-level scoring averages, coupled with `HAVING COUNT(*) >= 10` filters to eliminate low-sample statistical noise.
3. **Conditional Aggregation**:
   Evaluates toss efficacy and match outcomes utilizing boolean evaluation inside aggregate expressions (`SUM(toss_winner = winner) / COUNT(*)`), segregated by strategic decision (batting first versus fielding first).
4. **Targeted Exclusions**:
   Wicket-taker aggregations filter dismissal classifications using `NOT IN ('run out', 'retired hurt', 'obstructing the field')`, strictly isolating dismissals attributable to the bowler.
5. **Division-by-Zero Protection**:
   Batting strike rates employ `NULLIF(SUM(is_legal_ball), 0)` to guarantee numeric safety during calculation.

---

## Analytics Interface Architecture

The reporting layer is constructed with Streamlit, configured with distinct decoupled analytical views:
* **Overview**: Aggregated metrics across tournament history and seasonal match frequency distributions.
* **Team Performance**: All-time and season-filtered franchise win distributions alongside toss impact analytics.
* **Player Leaderboards**: Season-scoped run leaderboards, career wicket tallies, and career strike rates among qualified batters (minimum 500 legal balls faced).
* **Venue Insights**: Venue-specific first-innings scoring distributions and historical Orange Cap recipient tracking.

Database interactions are mediated via SQLAlchemy connection pooling with a 10-minute cache invalidation cycle (`@st.cache_data(ttl=600)`), minimizing database overhead during interactive dashboard usage.

---

## Technology Stack

* **Language**: Python 3.10+
* **Data Processing**: Pandas
* **Database Driver & Connection Layer**: SQLAlchemy 2.x, PyMySQL
* **Database Engine**: MySQL 8.x
* **Analytical Presentation**: Streamlit
* **Configuration Management**: python-dotenv
