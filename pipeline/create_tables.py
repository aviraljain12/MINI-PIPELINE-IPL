"""
Purpose : Read the SQL file and execute each statement against MySQL.
          This creates the ipl_db database and both tables.
          It MUST connect WITHOUT specifying the database first (include_db=False)
          because the database might not exist yet.
Reads   : sql/create_database_and_tables.sql
Writes  : creates ipl_db, tables matches and deliveries in MySQL
How to run: called by run_full_pipeline.py, or directly:
    cd ipl-pipeline
    python -m pipeline.create_tables
"""

import re
from pathlib import Path
from sqlalchemy import text
from pipeline.db_connection import get_engine

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_FILE     = PROJECT_ROOT / "sql" / "create_database_and_tables.sql"


def create_tables():
    """Read the SQL file and run each statement against the MySQL server."""
    print("\n[create_tables] Reading SQL file ...")
    sql_text = SQL_FILE.read_text(encoding="utf-8")

    # Strip all comments (-- ...) including inline comments so semicolons inside comments
    # do not break statement splitting.
    cleaned_lines = [re.sub(r"--.*$", "", line) for line in sql_text.splitlines()]
    cleaned_sql = "\n".join(cleaned_lines)

    # Split the file into individual statements on the semicolons.
    statements = [s.strip() for s in cleaned_sql.split(";") if s.strip()]

    # Connect WITHOUT a database name because "USE ipl_db" in the SQL file
    # will switch to ipl_db after the CREATE DATABASE statement runs.
    engine = get_engine(include_db=False)

    print(f"[create_tables] Executing {len(statements)} SQL statements ...")
    with engine.connect() as conn:
        for i, stmt in enumerate(statements, start=1):
            if stmt.strip():  # skip blank statements
                print(f"  Statement {i}: {stmt[:60].replace(chr(10), ' ')} ...")
                conn.execute(text(stmt))
        # Commit all the DDL statements (CREATE TABLE, etc.)
        conn.commit()

    print("[create_tables] Database and tables created successfully.\n")


if __name__ == "__main__":
    create_tables()

