"""
services/achievement_rules/xp_rule.py
-------------------------------------
"""

from .base_rule import AchievementRule
from models.user_stats import UserStatsModel


class XPRule(AchievementRule):
    """
    Checks total XP earned.
    """

    def evaluate(self, user_id: int, target_value: int) -> bool:
        stats = UserStatsModel.get(user_id)
        if not stats:
            return False
        return stats["current_xp"] >= target_value
