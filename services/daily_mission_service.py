"""
services/daily_mission_service.py
---------------------------------
Daily Mission Service

Responsible for:
- Assigning daily missions
- Preventing duplicate assignments
- Returning today's missions
"""

from database.db import get_db
from models.user_mission import UserMissionModel


class DailyMissionService:
    """
    Handles the daily mission workflow.
    """

    @staticmethod
    def ensure_daily_missions(user_id):
        """
        Ensure the user has today's daily missions.

        If today's missions have not yet been assigned,
        assign them first.

        Returns:
            list: Today's assigned missions.
        """
        
        db = get_db()
        
        try:
            # A single, atomic operation to assign any missing daily missions for today.
            UserMissionModel.assign_all_daily_missions(user_id)
            db.commit()
        except Exception:
            db.rollback()
            raise

        return UserMissionModel.get_today_missions(user_id)

    @staticmethod
    def get_today_missions(user_id):
        """
        Return today's assigned missions.

        Ensures assignments exist before returning them.
        """

        return DailyMissionService.ensure_daily_missions(user_id)