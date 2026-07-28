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
    Create database schema and insert default seed data.
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

    connection.commit()
    connection.close()