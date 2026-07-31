"""
LifeXP Database Initializer
"""

from pathlib import Path

from database.db import initialize_database, get_connection


def seed_database():
    """
    Execute seed.sql only once.
    """

    seed_file = Path("database") / "seed.sql"

    with get_connection() as connection:

        with open(seed_file, "r", encoding="utf-8") as file:

            connection.executescript(file.read())

        connection.commit()


def setup_database():
    """
    Initialize complete database.
    """

    initialize_database()

    seed_database()