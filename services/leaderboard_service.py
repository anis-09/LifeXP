"""
services/leaderboard_service.py
-------------------------------
Leaderboard Service

Handles business logic for leaderboards, including date calculations,
tie-breakers, and formatting safe public outputs.
"""

from datetime import date, datetime, timedelta
from models.leaderboard import LeaderboardModel
from models.user import get_user_by_id
from models.user_stats import UserStatsModel


class LeaderboardService:
    """
    Business logic for the leaderboard.
    """

    @staticmethod
    def get_leaderboard_data(user_id, period="global", limit=50):
        """
        Get leaderboard data for a specific period.
        """
        
        today = date.today()
        
        top_players = []
        user_rank_row = None
        
        if period == "weekly":
            # Monday is 0, Sunday is 6
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            
            # Format to SQLite timestamp string format
            start_date_str = f"{start_of_week.isoformat()} 00:00:00"
            end_date_str = f"{end_of_week.isoformat()} 23:59:59"
            
            top_players = LeaderboardModel.get_period_leaderboard(start_date_str, end_date_str, limit)
            user_rank_row = LeaderboardModel.get_user_period_rank(user_id, start_date_str, end_date_str)
            
        elif period == "monthly":
            start_of_month = today.replace(day=1)
            # Find last day of month
            next_month = start_of_month.replace(day=28) + timedelta(days=4)
            end_of_month = next_month - timedelta(days=next_month.day)
            
            start_date_str = f"{start_of_month.isoformat()} 00:00:00"
            end_date_str = f"{end_of_month.isoformat()} 23:59:59"
            
            top_players = LeaderboardModel.get_period_leaderboard(start_date_str, end_date_str, limit)
            user_rank_row = LeaderboardModel.get_user_period_rank(user_id, start_date_str, end_date_str)
            
        elif period == "friends":
            top_players = []
            user_rank_row = None
            
        else:
            # global
            period = "global"
            top_players = LeaderboardModel.get_global_leaderboard(limit)
            user_rank_row = LeaderboardModel.get_user_global_rank(user_id)
            
        # If user is not ranked (e.g. 0 XP in period), provide a default row
        if not user_rank_row and period != "friends":
            user = get_user_by_id(user_id)
            stats = UserStatsModel.get(user_id)
            user_rank_row = {
                "user_id": user_id,
                "full_name": user["full_name"],
                "avatar": user["avatar"],
                "xp": stats["current_xp"] if period == "global" else 0,
                "level": stats["current_level"],
                "streak": stats["current_streak"],
                "rank": "-"
            }
        elif user_rank_row:
            # Convert sqlite3.Row to dict
            user_rank_row = dict(user_rank_row)
            
        # Convert sqlite3.Row list to dict list
        formatted_players = [dict(p) for p in top_players] if top_players else []
        
        # Check if current user is in top N
        user_in_top = False
        if user_rank_row and user_rank_row.get("rank") != "-":
            for p in formatted_players:
                if p["user_id"] == user_id:
                    user_in_top = True
                    break

        return {
            "period": period,
            "top_players": formatted_players,
            "user_rank_row": user_rank_row,
            "user_in_top": user_in_top
        }
