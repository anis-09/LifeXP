"""
services/achievement_rules/level_rule.py
----------------------------------------
"""

from .base_rule import AchievementRule
from models.user_stats import UserStatsModel


class LevelRule(AchievementRule):
    """
    Checks user's current level.
    """

    def evaluate(self, user_id: int, target_value: int) -> bool:
        stats = UserStatsModel.get(user_id)
        if not stats:
            return False
        return stats["current_level"] >= target_value
