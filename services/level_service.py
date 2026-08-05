"""
services/level_service.py
-------------------------
Level Calculation Service
"""

from constants import XP_PER_LEVEL


class LevelService:
    """
    Provides business logic for user level calculations.
    """

    @staticmethod
    def calculate_level(total_xp):
        """
        Return the level associated with a user's total XP.
        Uses XP_PER_LEVEL from constants as the single source of truth.
        """

        return (total_xp // XP_PER_LEVEL) + 1
