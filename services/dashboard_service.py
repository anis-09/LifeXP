"""
services/dashboard_service.py
-----------------------------
Dashboard Service
"""

from datetime import datetime

from constants import XP_PER_LEVEL
from models.user import get_user_by_id
from models.user_stats import UserStatsModel
from services.daily_mission_service import DailyMissionService



class DashboardService:
    """
    Business logic for the authenticated dashboard.
    """

    @staticmethod
    def get_dashboard_data(user_id):
        """
        Build all data required to render the dashboard.
        """

        user = get_user_by_id(user_id)

        if not user:
            return None

        stats = UserStatsModel.get(user_id)

        if not stats:
            UserStatsModel.create(user_id)
            stats = UserStatsModel.get(user_id)

        current_level = stats["current_level"]
        current_xp = stats["current_xp"]

        level_start_xp = (current_level - 1) * XP_PER_LEVEL
        level_end_xp = current_level * XP_PER_LEVEL

        xp_into_level = current_xp - level_start_xp
        xp_required_this_level = level_end_xp - level_start_xp
        xp_remaining = max(level_end_xp - current_xp, 0)

        xp_progress = (
            int((xp_into_level / xp_required_this_level) * 100)
            if xp_required_this_level
            else 0
        )

        today_missions = DailyMissionService.ensure_daily_missions(user_id)

        return {
            "user": user,
            "stats": stats,
            "today": datetime.now().strftime("%A, %B %d, %Y"),

            "xp_progress": xp_progress,
            "xp_into_level": xp_into_level,
            "xp_required_this_level": xp_required_this_level,
            "xp_remaining": xp_remaining,
            "level_start_xp": level_start_xp,
            "level_end_xp": level_end_xp,

            "daily_missions": today_missions,
        }