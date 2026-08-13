"""
models/leaderboard.py
---------------------
Leaderboard Model

Handles queries for global, weekly, and monthly rankings.
"""

from database.db import get_db


class LeaderboardModel:
    """
    Leaderboard data access.
    """

    @staticmethod
    def get_global_leaderboard(limit=50):
        """
        Get global leaderboard top N.
        """
        db = get_db()
        return db.execute(
            """
            SELECT 
                u.id as user_id,
                u.full_name, 
                u.avatar, 
                us.current_xp as xp, 
                us.current_level as level, 
                us.current_streak as streak,
                ROW_NUMBER() OVER (ORDER BY us.current_xp DESC, us.current_level DESC, us.current_streak DESC) as rank
            FROM user_stats us
            JOIN users u ON u.id = us.user_id
            WHERE u.is_active = 1
            ORDER BY us.current_xp DESC, us.current_level DESC, us.current_streak DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

    @staticmethod
    def get_user_global_rank(user_id):
        """
        Get the global rank for a specific user.
        """
        db = get_db()
        return db.execute(
            """
            WITH RankedUsers AS (
                SELECT 
                    u.id as user_id,
                    u.full_name, 
                    u.avatar, 
                    us.current_xp as xp, 
                    us.current_level as level, 
                    us.current_streak as streak,
                    ROW_NUMBER() OVER (ORDER BY us.current_xp DESC, us.current_level DESC, us.current_streak DESC) as rank
                FROM user_stats us
                JOIN users u ON u.id = us.user_id
                WHERE u.is_active = 1
            )
            SELECT * FROM RankedUsers WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()

    @staticmethod
    def get_period_leaderboard(start_date_str, end_date_str, limit=50):
        """
        Get leaderboard for a specific period (weekly/monthly).
        start_date_str and end_date_str should be 'YYYY-MM-DD HH:MM:SS'.
        """
        db = get_db()
        return db.execute(
            """
            WITH PeriodXP AS (
                SELECT user_id, SUM(amount) as period_xp
                FROM xp_transactions
                WHERE created_at >= ? AND created_at <= ?
                GROUP BY user_id
            )
            SELECT 
                u.id as user_id,
                u.full_name, 
                u.avatar, 
                COALESCE(px.period_xp, 0) as xp,
                us.current_level as level, 
                us.current_streak as streak,
                ROW_NUMBER() OVER (ORDER BY COALESCE(px.period_xp, 0) DESC, us.current_level DESC, us.current_streak DESC) as rank
            FROM user_stats us
            JOIN users u ON u.id = us.user_id
            JOIN PeriodXP px ON px.user_id = u.id
            WHERE u.is_active = 1 AND COALESCE(px.period_xp, 0) > 0
            ORDER BY COALESCE(px.period_xp, 0) DESC, us.current_level DESC, us.current_streak DESC
            LIMIT ?
            """,
            (start_date_str, end_date_str, limit)
        ).fetchall()

    @staticmethod
    def get_user_period_rank(user_id, start_date_str, end_date_str):
        """
        Get the period rank for a specific user.
        """
        db = get_db()
        return db.execute(
            """
            WITH PeriodXP AS (
                SELECT user_id, SUM(amount) as period_xp
                FROM xp_transactions
                WHERE created_at >= ? AND created_at <= ?
                GROUP BY user_id
            ),
            RankedUsers AS (
                SELECT 
                    u.id as user_id,
                    u.full_name, 
                    u.avatar, 
                    COALESCE(px.period_xp, 0) as xp, 
                    us.current_level as level, 
                    us.current_streak as streak,
                    ROW_NUMBER() OVER (ORDER BY COALESCE(px.period_xp, 0) DESC, us.current_level DESC, us.current_streak DESC) as rank
                FROM user_stats us
                JOIN users u ON u.id = us.user_id
                JOIN PeriodXP px ON px.user_id = u.id
                WHERE u.is_active = 1 AND COALESCE(px.period_xp, 0) > 0
            )
            SELECT * FROM RankedUsers WHERE user_id = ?
            """,
            (start_date_str, end_date_str, user_id)
        ).fetchone()
