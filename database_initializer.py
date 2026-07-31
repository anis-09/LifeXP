"""
database_initializer.py
"""

from pathlib import Path

from database.db import (
    get_connection,
    initialize_database,
)


def seed_database():

    seed_path = Path("database") / "seed.sql"

    with get_connection() as connection:

        with open(seed_path, "r", encoding="utf-8") as file:

            connection.executescript(file.read())

        connection.commit()


def setup_database():

    initialize_database()

    seed_database()