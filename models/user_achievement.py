"""
models/user_achievement.py
--------------------------
User Achievement Association Model
"""

from __future__ import annotations

from typing import List, Dict

from database.db import get_db


class UserAchievementModel:
    """
    Handles operations for user-unlocked achievements.
    """

    @staticmethod
    def unlock(user_id: int, achievement_id: int) -> None:
        """Record that a user has unlocked an achievement."""
        db = get_db()
        db.execute(
            """
            INSERT OR IGNORE INTO user_achievements (user_id, achievement_id)
            VALUES (?, ?)
            """,
            (user_id, achievement_id)
        )
        # Note: Transaction is managed by the service layer

    @staticmethod
    def get_unlocked_for_user(user_id: int) -> List[Dict]:
        """Return a list of achievements unlocked by the user as dictionaries."""
        db = get_db()
        rows = db.execute(
            """
            SELECT
                a.*,
                ua.unlocked_at
            FROM user_achievements ua
            JOIN achievements a ON a.id = ua.achievement_id
            WHERE ua.user_id = ?
            ORDER BY ua.unlocked_at DESC
            """,
            (user_id,)
        ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def get_locked_for_user(user_id: int) -> List[Dict]:
        """Return a list of achievements NOT YET unlocked by the user as dictionaries."""
        db = get_db()
        rows = db.execute(
            """
            SELECT a.*
            FROM achievements a
            LEFT JOIN user_achievements ua
                ON a.id = ua.achievement_id AND ua.user_id = ?
            WHERE ua.achievement_id IS NULL
            ORDER BY a.display_order, a.id ASC
            """,
            (user_id,)
        ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def has_unlocked(user_id: int, achievement_id: int) -> bool:
        """Check if a user has already unlocked a specific achievement."""
        db = get_db()
        result = db.execute(
            """
            SELECT 1 FROM user_achievements
            WHERE user_id = ? AND achievement_id = ?
            """,
            (user_id, achievement_id)
        ).fetchone()
        return result is not None

    @staticmethod
    def count_unlocked(user_id: int) -> int:
        """Return the number of achievements a user has unlocked."""
        db = get_db()
        result = db.execute(
            """
            SELECT COUNT(*) FROM user_achievements WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()
        # result is a Row with the count at index 0
        return result[0] if result else 0

    @staticmethod
    def latest_unlocked(user_id: int, limit: int = 5) -> List[Dict]:
        """Return the most recently unlocked achievements for a user (default 5)."""
        db = get_db()
        rows = db.execute(
            """
            SELECT a.*, ua.unlocked_at
            FROM user_achievements ua
            JOIN achievements a ON a.id = ua.achievement_id
            WHERE ua.user_id = ?
            ORDER BY ua.unlocked_at DESC
            LIMIT ?
            """,
            (user_id, limit)
        ).fetchall()
        return [dict(row) for row in rows]

    # TODO: Implement create(achievement_data: Dict) -> int
    # TODO: Implement update(achievement_id: int, data: Dict) -> None
    # TODO: Implement delete(achievement_id: int) -> None
