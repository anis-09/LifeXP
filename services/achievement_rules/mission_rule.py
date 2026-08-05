"""
services/achievement_rules/mission_rule.py
------------------------------------------
"""

from .base_rule import AchievementRule
from models.user_stats import UserStatsModel


class MissionRule(AchievementRule):
    """
    Checks total completed missions.
    """

    def get_current_value(self, user_id: int) -> int:
        stats = UserStatsModel.get(user_id)
        if not stats:
            return 0
        return stats["missions_completed"]
