"""
models/user_stats.py
--------------------
User Stats Model
"""

from database.db import get_db


class UserStatsModel:
    """
    User statistics model.
    """

    @staticmethod
    def get(user_id):
        """
        Return user stats.
        """

        db = get_db()

        return db.execute(
            """
            SELECT *
            FROM user_stats
            WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()

    @staticmethod
    def create(user_id):
        """
        Create default stats for a user.
        """

        db = get_db()

        db.execute(
            """
            INSERT INTO user_stats
            (
                user_id
            )
            VALUES
            (
                ?
            )
            """,
            (user_id,)
        )

        db.commit()

    @staticmethod
    def add_xp(user_id, xp):
        """
        Add XP to user.
        """

        db = get_db()

        db.execute(
            """
            UPDATE user_stats
            SET
                current_xp = current_xp + ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ?
            """,
            (
                xp,
                user_id
            )
        )

        db.commit()

    @staticmethod
    def add_coins(user_id, coins):
        """
        Add coins to user.
        """

        db = get_db()

        db.execute(
            """
            UPDATE user_stats
            SET
                current_coins = current_coins + ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ?
            """,
            (
                coins,
                user_id
            )
        )

        db.commit()

    @staticmethod
    def increment_completed_missions(user_id):
        """
        Increase completed mission count.
        """

        db = get_db()

        db.execute(
            """
            UPDATE user_stats
            SET
                missions_completed = missions_completed + 1,
                last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ?
            """,
            (user_id,)
        )

        db.commit()

    @staticmethod
    def update_level(user_id, level):
        """
        Update user level.
        """

        db = get_db()

        db.execute(
            """
            UPDATE user_stats
            SET
                current_level = ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ?
            """,
            (
                level,
                user_id
            )
        )

        db.commit()