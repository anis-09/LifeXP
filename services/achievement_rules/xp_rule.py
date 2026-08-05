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

    def get_current_value(self, user_id: int) -> int:
        stats = UserStatsModel.get(user_id)
        if not stats:
            return 0
        return stats["current_xp"]
