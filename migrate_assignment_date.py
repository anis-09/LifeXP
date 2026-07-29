"""
migrate_assignment_date.py
--------------------------
One-time migration: adds the assignment_date column and index to
user_missions if they don't already exist. Safe to run multiple times.
"""

import sqlite3
import sys
import os

# Locate the database the same way the app does
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
conn.execute("PRAGMA foreign_keys = ON")

cols = [row[1] for row in conn.execute("PRAGMA table_info(user_missions)").fetchall()]

if "assignment_date" not in cols:
    conn.execute(
        "ALTER TABLE user_missions "
        "ADD COLUMN assignment_date DATE NOT NULL DEFAULT (DATE('now'))"
    )
    print("Added assignment_date column to user_missions.")
else:
    print("assignment_date already present — skipping ALTER TABLE.")

idx_names = [
    row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index'"
    ).fetchall()
]
if "idx_daily_assignment" not in idx_names:
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_daily_assignment "
        "ON user_missions(user_id, mission_id, assignment_date)"
    )
    print("Created idx_daily_assignment unique index.")
else:
    print("idx_daily_assignment already present — skipping CREATE INDEX.")

conn.commit()
conn.close()
print("Migration complete.")
