"""
services/streak_service.py
-------------------------
Streak Service
"""

from datetime import date, timedelta

from constants import STREAK_MILESTONES
from models.user_stats import UserStatsModel


class StreakService:
    """
    Handles user streak calculations and milestone bonuses.
    """

    @staticmethod
    def update_streak(user_id, activity_date=None):
        """
        Update a user's streak after completing a mission.
        """

        activity_date = activity_date or date.today()
        stats = UserStatsModel.get(user_id)

        if stats is None:
            UserStatsModel.create(user_id)
            stats = UserStatsModel.get(user_id)

        current_streak = StreakService._calculate_current_streak(
            stats=stats,
            activity_date=activity_date
        )
        longest_streak = max(stats["longest_streak"], current_streak)

        UserStatsModel.update_streak(
            user_id=user_id,
            current_streak=current_streak,
            longest_streak=longest_streak,
            last_activity_date=activity_date.isoformat()
        )

        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "last_activity_date": activity_date.isoformat()
        }

    @staticmethod
    def get_streak_bonus(current_streak: int):
        """
        Return (xp_bonus, coin_bonus) if current_streak hits a milestone.
        Returns (0, 0) when the streak count is not a milestone.
        Milestone thresholds and values are defined in constants.STREAK_MILESTONES.
        """
        return STREAK_MILESTONES.get(current_streak, (0, 0))

    @staticmethod
    def _calculate_current_streak(stats, activity_date):
        """
        Return the streak total for the supplied activity date.
        """

        last_activity_date = stats["last_activity_date"]

        if last_activity_date is None:
            return 1

        last_activity_date = date.fromisoformat(last_activity_date)

        if activity_date <= last_activity_date:
            return stats["current_streak"]

        if activity_date == last_activity_date + timedelta(days=1):
            return stats["current_streak"] + 1

        return 1

