"""
services/level_service.py
-------------------------
Level Calculation Service
"""


class LevelService:
    """
    Provides business logic for user level calculations.
    """

    XP_PER_LEVEL = 500

    @staticmethod
    def calculate_level(total_xp):
        """
        Return the level associated with a user's total XP.
        """

        return (total_xp // LevelService.XP_PER_LEVEL) + 1
