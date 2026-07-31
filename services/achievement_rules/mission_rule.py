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

    def evaluate(self, user_id: int, target_value: int) -> bool:
        stats = UserStatsModel.get(user_id)
        if not stats:
            return False
        return stats["missions_completed"] >= target_value
