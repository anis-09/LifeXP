"""
services/dashboard_service.py
-----------------------------
Dashboard Service
"""

from datetime import date, datetime, timedelta

from constants import XP_PER_LEVEL
from models.user import get_user_by_id
from models.user_stats import UserStatsModel
from services.daily_mission_service import DailyMissionService
from models.user_achievement import UserAchievementModel


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
        streak_days = DashboardService._build_streak_days(stats)
        unlocked_achievements = UserAchievementModel.get_unlocked_for_user(user_id)

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

            # Streak data for the weekly visualiser
            "streak_days": streak_days,
            "longest_streak": stats["longest_streak"],

            "unlocked_achievements": unlocked_achievements,
        }

    @staticmethod
    def _build_streak_days(stats):
        """
        Build a list of 7 dicts representing the last 7 calendar days.

        Each dict has:
            label    – single-letter day abbreviation (M, T, W …)
            active   – True if this day was part of the current streak
            is_today – True for today's entry

        We derive active days from current_streak and last_activity_date.
        A streak is a consecutive block of days ending on last_activity_date
        (or today if last_activity_date is today).
        """

        today = date.today()
        day_labels = ["M", "T", "W", "T", "F", "S", "S"]

        current_streak = stats["current_streak"] or 0
        last_activity_raw = stats["last_activity_date"]

        # Determine the most recent active date.
        if last_activity_raw:
            last_active = date.fromisoformat(last_activity_raw)
        else:
            last_active = None

        # If the streak is alive (last_active is today or yesterday at most),
        # build the active window; otherwise streak is broken — no active days.
        streak_end = None
        if last_active and current_streak > 0:
            days_since_last = (today - last_active).days
            if days_since_last <= 1:
                # Streak is live — end of the active window is last_active
                streak_end = last_active
            # else streak broken; streak_end stays None

        result = []
        for offset in range(6, -1, -1):
            day_date = today - timedelta(days=offset)
            weekday_index = day_date.weekday()  # 0=Monday … 6=Sunday

            active = False
            if streak_end is not None and current_streak > 0:
                streak_start = streak_end - timedelta(days=current_streak - 1)
                active = streak_start <= day_date <= streak_end

            result.append({
                "label": day_labels[weekday_index],
                "active": active,
                "is_today": day_date == today,
            })

        return result