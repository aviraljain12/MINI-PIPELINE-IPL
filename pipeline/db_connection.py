"""
Purpose : Build a SQLAlchemy engine (connection) to MySQL using credentials
          stored in the .env file.
Reads   : .env file (via python-dotenv)
Writes  : nothing
How to run: imported by other pipeline scripts — not run directly
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine


from urllib.parse import quote_plus

def get_engine(include_db: bool = True):
    """
    Return a SQLAlchemy engine connected to MySQL.

    Parameters
    ----------
    include_db : bool
        When True  → connect directly to ipl_db (normal use).
        When False → connect to the server WITHOUT selecting a database.
                     We need this in create_tables.py because the database
                     might not exist yet when we first run it.
    """
    # Load variables from the .env file into os.environ.
    # This must happen before we call os.getenv().
    load_dotenv()

    host     = os.getenv("DB_HOST", "localhost")
    port     = int(os.getenv("DB_PORT", "3306"))   # must be int
    user     = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    db_name  = os.getenv("DB_NAME", "ipl_db")

    # URL-encode user and password to safely handle special characters like '@', ':', etc.
    encoded_user = quote_plus(user)
    encoded_password = quote_plus(password)

    # We use pymysql as the MySQL driver (mysql+pymysql) instead of mysql-connector-python.
    # Reason: mysql-connector-python 8.4 has a port-type bug with SQLAlchemy 2.1 on Python 3.14.
    # pymysql is pure Python, works on all Python versions, and is the most compatible driver.
    if include_db:
        url = f"mysql+pymysql://{encoded_user}:{encoded_password}@{host}:{port}/{db_name}"
    else:
        # No database name → connects to the server root; needed for CREATE DATABASE
        url = f"mysql+pymysql://{encoded_user}:{encoded_password}@{host}:{port}/"

    # pool_pre_ping=True makes SQLAlchemy test the connection before using it.
    engine = create_engine(url, pool_pre_ping=True)
    return engine

