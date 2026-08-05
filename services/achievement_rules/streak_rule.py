"""
services/achievement_rules/streak_rule.py
-----------------------------------------
"""

from .base_rule import AchievementRule
from models.user_stats import UserStatsModel


class StreakRule(AchievementRule):
    """
    Checks highest streak length.
    """

    def get_current_value(self, user_id: int) -> int:
        stats = UserStatsModel.get(user_id)
        if not stats:
            return 0
        return stats["longest_streak"]
