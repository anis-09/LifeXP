"""
utils/db.py
-----------
SQLite database connection helper.
Provides a get_db() function that returns a thread-safe connection,
and init_db() that creates all required tables on first run.
"""

import sqlite3
import os
from flask import g

DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')


def get_db():
    """Return the database connection for the current application context."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row  # Access columns by name
    return g.db


def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Create database tables if they don't already exist."""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row

    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT    NOT NULL,
            email     TEXT    NOT NULL UNIQUE,
            password  TEXT    NOT NULL,
            level     INTEGER NOT NULL DEFAULT 1,
            xp        INTEGER NOT NULL DEFAULT 0,
            coins     INTEGER NOT NULL DEFAULT 0,
            streak    INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
    db.close()
