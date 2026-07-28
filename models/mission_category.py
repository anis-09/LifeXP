"""
models/mission_category.py
--------------------------
Mission Category Model
"""

from database.db import get_db


class MissionCategoryModel:
    """
    Handles mission category database operations.
    """

    @staticmethod
    def get_all():
        """
        Return all mission categories ordered by name.
        """

        db = get_db()

        return db.execute(
            """
            SELECT
                id,
                name,
                icon,
                color
            FROM mission_categories
            ORDER BY name ASC
            """
        ).fetchall()

    @staticmethod
    def get_by_id(category_id):
        """
        Return a single category.
        """

        db = get_db()

        return db.execute(
            """
            SELECT *
            FROM mission_categories
            WHERE id = ?
            """,
            (category_id,)
        ).fetchone()