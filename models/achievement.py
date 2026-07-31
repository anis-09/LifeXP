"""
models/achievement.py
---------------------
Achievement Model
"""

from __future__ import annotations

from typing import List, Dict, Optional

from database.db import get_db


class AchievementModel:
    """
    Handles operations for the achievements table.
    """

    @staticmethod
    def get_all() -> List[Dict]:
        """Return all available achievements ordered by display_order and id as a list of dicts."""
        db = get_db()
        rows = db.execute(
            """
            SELECT * FROM achievements ORDER BY display_order, id ASC
            """
        ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def get_by_id(achievement_id: int) -> Optional[Dict]:
        """Return a single achievement by ID as a dict, or None if not found."""
        db = get_db()
        achievement = db.execute(
            """
            SELECT * FROM achievements WHERE id = ?
            """,
            (achievement_id,)
        ).fetchone()
        return dict(achievement) if achievement else None

    @staticmethod
    def get_by_category(category: str) -> List[Dict]:
        """Return achievements filtered by category, ordered by display_order and id."""
        db = get_db()
        rows = db.execute(
            """
            SELECT * FROM achievements WHERE category = ? ORDER BY display_order, id ASC
            """,
            (category,)
        ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def get_visible() -> List[Dict]:
        """Return achievements that are not hidden (is_hidden = 0)."""
        db = get_db()
        rows = db.execute(
            """
            SELECT * FROM achievements WHERE is_hidden = 0 ORDER BY display_order, id ASC
            """
        ).fetchall()
        return [dict(row) for row in rows]

    # TODO: Implement create(achievement_data: Dict) -> int
    # TODO: Implement update(achievement_id: int, data: Dict) -> None
    # TODO: Implement delete(achievement_id: int) -> None
