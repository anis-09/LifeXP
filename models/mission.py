"""
models/mission.py
-----------------
Mission Model
"""

from database.db import get_db


class MissionModel:

    @staticmethod
    def create(
        title,
        description,
        category_id,
        difficulty,
        xp_reward,
        coin_reward,
        is_daily=False,
        created_by=None
    ):
        """Create a new mission."""

        db = get_db()

        cursor = db.execute(
            """
            INSERT INTO missions
            (
                title,
                description,
                category_id,
                difficulty,
                xp_reward,
                coin_reward,
                is_daily,
                created_by
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                description,
                category_id,
                difficulty,
                xp_reward,
                coin_reward,
                int(is_daily),
                created_by
            )
        )

        db.commit()

        return cursor.lastrowid

    @staticmethod
    def get_all():
        """Return all missions."""

        db = get_db()

        return db.execute(
            """
            SELECT
                missions.*,
                mission_categories.name AS category_name,
                mission_categories.icon,
                mission_categories.color
            FROM missions

            INNER JOIN mission_categories
                ON mission_categories.id = missions.category_id

            ORDER BY
                missions.created_at DESC,
                missions.id DESC
            """
        ).fetchall()

    @staticmethod
    def get_by_id(mission_id):
        """Return a single mission."""

        db = get_db()

        return db.execute(
            """
            SELECT *
            FROM missions
            WHERE id = ?
            """,
            (mission_id,)
        ).fetchone()

    @staticmethod
    def update(
        mission_id,
        title,
        description,
        category_id,
        difficulty,
        xp_reward,
        coin_reward,
        is_daily
    ):
        """Update an existing mission."""

        db = get_db()

        db.execute(
            """
            UPDATE missions
            SET
                title=?,
                description=?,
                category_id=?,
                difficulty=?,
                xp_reward=?,
                coin_reward=?,
                is_daily=?
            WHERE id=?
            """,
            (
                title,
                description,
                category_id,
                difficulty,
                xp_reward,
                coin_reward,
                int(is_daily),
                mission_id
            )
        )

        db.commit()

    @staticmethod
    def complete(mission_id):
        """
        Mark a mission as completed.
        """

        db = get_db()

        db.execute(
            """
            UPDATE missions
            SET
                is_completed = 1,
                completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (mission_id,)
        )

        db.commit()

    @staticmethod
    def delete(mission_id):
        """Delete a mission."""

        db = get_db()

        db.execute(
            """
            DELETE FROM missions
            WHERE id = ?
            """,
            (mission_id,)
        )

        db.commit()

    @staticmethod
    def count():
        """Return total mission count."""

        db = get_db()

        result = db.execute(
            """
            SELECT COUNT(*) AS total
            FROM missions
            """
        ).fetchone()

        return result["total"]