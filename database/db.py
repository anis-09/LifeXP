"""
database/db.py
--------------
LifeXP Database Manager
"""

import sqlite3
from pathlib import Path
from flask import g

from config import DATABASE_PATH


def get_connection():
    """
    Create and return a SQLite connection.
    """

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def get_db():
    """
    Return request-level database connection.
    """

    if "db" not in g:
        g.db = get_connection()

    return g.db


def close_db(e=None):
    """
    Close request database connection.
    """

    db = g.pop("db", None)

    if db is not None:
        db.close()


def initialize_database():
    """
    Create database schema, insert default seed data, and apply any
    migration scripts found in the migrations/ directory.

    All SQL files are run with executescript which is idempotent for
    CREATE … IF NOT EXISTS / CREATE INDEX IF NOT EXISTS statements.
    """

    connection = get_connection()

    database_dir = Path(__file__).parent

    schema_file = database_dir / "schema.sql"
    seed_file = database_dir / "seed.sql"

    # Create tables
    with open(schema_file, "r", encoding="utf-8") as file:
        connection.executescript(file.read())

    # Insert default data
    with open(seed_file, "r", encoding="utf-8") as file:
        connection.executescript(file.read())

    # Apply migration scripts (alphabetical order, idempotent)
    migrations_dir = database_dir.parent / "migrations"
    if migrations_dir.is_dir():
        for migration_file in sorted(migrations_dir.glob("*.sql")):
            with open(migration_file, "r", encoding="utf-8") as file:
                connection.executescript(file.read())

    # ---------------------------------------------------------------
    # Idempotent column-level migrations
    # These use Python guards (PRAGMA table_info) to safely ADD COLUMN
    # without failing on repeated runs.  SQLite does not support
    # ALTER TABLE ADD COLUMN IF NOT EXISTS, so this pattern is required.
    # ---------------------------------------------------------------

    _apply_column_migrations(connection)

    connection.commit()
    connection.close()


def _apply_column_migrations(connection: sqlite3.Connection) -> None:
    """
    Apply idempotent ALTER TABLE ADD COLUMN migrations.

    Each entry is a (table, column, column_definition) tuple.
    The column is added only if it does not already exist.
    """

    column_migrations = [
        # Added in migrate_last_activity_date.py (standalone script).
        # Required by DashboardService._build_streak_days() and
        # UserStatsModel.update_streak().
        ("user_stats", "last_activity_date", "DATE"),
    ]

    for table, column, definition in column_migrations:
        existing = [
            row[1]
            for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
        ]
        if column not in existing:
            connection.execute(
                f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
            )
            connection.commit()