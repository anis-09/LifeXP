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

    def evaluate(self, user_id: int, target_value: int) -> bool:
        stats = UserStatsModel.get(user_id)
        if not stats:
            return False
        return stats["longest_streak"] >= target_value
