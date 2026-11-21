"""
Purpose : Create a SQLAlchemy engine and a cached query helper for the dashboard.
          This file is intentionally SEPARATE from pipeline/db_connection.py
          so the Streamlit app can run on its own without importing any pipeline
          code. The app only needs to query MySQL; it doesn't need to load data.
Reads   : .env file for database credentials
Writes  : nothing
How to run: imported by streamlit_app.py and pages/*.py — not run directly
"""

import os
import pandas as pd
import streamlit as st
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


@st.cache_resource   # cache_resource keeps one engine alive for the whole Streamlit session
def get_engine():
    """
    Build and return a SQLAlchemy engine connected to MySQL.
    @st.cache_resource means this function only runs once per Streamlit session —
    we don't want to open a new database connection on every page refresh.
    """
    load_dotenv()

    host     = os.getenv("DB_HOST", "localhost")
    port     = int(os.getenv("DB_PORT", "3306"))
    user     = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    db_name  = os.getenv("DB_NAME", "ipl_db")

    # URL-encode user and password to safely handle special characters like '@', ':', etc.
    encoded_user = quote_plus(user)
    encoded_password = quote_plus(password)

    # pymysql driver — works on all Python versions including 3.14
    url = f"mysql+pymysql://{encoded_user}:{encoded_password}@{host}:{port}/{db_name}"
    return create_engine(url, pool_pre_ping=True)


@st.cache_data(ttl=600)   # cache query results for 10 minutes (600 seconds)
def run_query(sql: str, params: dict = None) -> pd.DataFrame:
    """
    Run a SQL query and return the results as a Pandas DataFrame.
    Results are cached for 10 minutes so the same query isn't re-run on
    every minor Streamlit interaction (like moving a slider).

    Parameters
    ----------
    sql    : the SQL string, with named placeholders like :season
    params : a dict of values to substitute, e.g. {"season": 2024}
             Using params (not f-strings) is critical: it prevents SQL injection.
             SQL injection is when a user types SQL commands into a text box to
             attack the database. Parameterised queries prevent this.
    """
    engine = get_engine()
    try:
        with engine.connect() as conn:
            # text() wraps the SQL string so SQLAlchemy can parse :placeholders
            df = pd.read_sql(text(sql), conn, params=params)
        return df
    except Exception as e:
        # Show a user-friendly error in the dashboard instead of a stack trace.
        st.error(
            f"**Database connection failed.**\n\n"
            f"Error: `{e}`\n\n"
            f"**What to check:**\n"
            f"- Is MySQL running? (`mysql -u root -p`)\n"
            f"- Is your `.env` file present and correct?\n"
            f"- Did you run the pipeline? (`python -m pipeline.run_full_pipeline`)"
        )
        # Return an empty DataFrame so the page doesn't crash further.
        return pd.DataFrame()

