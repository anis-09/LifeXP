"""
One-time migration that adds last_activity_date to user_stats.
Safe to run multiple times.
"""

import sqlite3

from config import DATABASE_PATH


def migrate_last_activity_date():
    """
    Add the user_stats activity date column when it is missing.
    """

    connection = sqlite3.connect(DATABASE_PATH)
    columns = [
        row[1]
        for row in connection.execute("PRAGMA table_info(user_stats)").fetchall()
    ]

    if "last_activity_date" not in columns:
        connection.execute(
            "ALTER TABLE user_stats ADD COLUMN last_activity_date DATE"
        )
        connection.commit()
        print("Added last_activity_date column to user_stats.")
    else:
        print("last_activity_date already present; skipping migration.")

    connection.close()


if __name__ == "__main__":
    migrate_last_activity_date()
