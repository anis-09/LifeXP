"""
models/leaderboard.py
---------------------
Leaderboard Model

Handles queries for global, weekly, and monthly rankings.
"""

from database.db import get_db
from config import FIRESTORE_USER_STATS_ENABLED

def get_fs():
    from services.firebase_service import get_firestore_client
    return get_firestore_client()


class LeaderboardModel:
    """
    Leaderboard data access.
    """

    @staticmethod
    def get_global_leaderboard(limit=50):
        """
        Get global leaderboard top N.
        """
        if FIRESTORE_USER_STATS_ENABLED:
            from firebase_admin import firestore
            
            # Fetch a bounded candidate pool to handle ties without composite indexes
            candidate_limit = max(limit * 3, 200)
            docs = get_fs().collection("user_stats")\
                .order_by("current_xp", direction=firestore.Query.DESCENDING)\
                .limit(candidate_limit).get()
            
            candidates = []
            for doc in docs:
                data = doc.to_dict()
                user_id = int(doc.id.replace("sqlite_", "")) if doc.id.startswith("sqlite_") else doc.id
                candidates.append({
                    "user_id": user_id,
                    "full_name": data.get("full_name", ""),
                    "avatar": data.get("avatar", ""),
                    "xp": data.get("current_xp", 0),
                    "level": data.get("current_level", 0),
                    "streak": data.get("current_streak", 0)
                })
            
            # Tie-breakers: XP DESC, level DESC, streak DESC, user_id ASC
            candidates.sort(key=lambda x: (-x["xp"], -x["level"], -x["streak"], x["user_id"]))
            
            results = []
            for i, p in enumerate(candidates[:limit]):
                p["rank"] = i + 1
                results.append(p)
            return results

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
                ROW_NUMBER() OVER (ORDER BY us.current_xp DESC, us.current_level DESC, us.current_streak DESC, u.id ASC) as rank
            FROM user_stats us
            JOIN users u ON u.id = us.user_id
            WHERE u.is_active = 1
            ORDER BY us.current_xp DESC, us.current_level DESC, us.current_streak DESC, u.id ASC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

    @staticmethod
    def get_user_global_rank(user_id):
        """
        Get the global rank for a specific user.
        """
        if FIRESTORE_USER_STATS_ENABLED:
            from firebase_admin import firestore
            
            candidate_limit = 200
            docs = get_fs().collection("user_stats")\
                .order_by("current_xp", direction=firestore.Query.DESCENDING)\
                .limit(candidate_limit).get()
            
            candidates = []
            for doc in docs:
                data = doc.to_dict()
                uid = int(doc.id.replace("sqlite_", "")) if doc.id.startswith("sqlite_") else doc.id
                candidates.append({
                    "user_id": uid,
                    "full_name": data.get("full_name", ""),
                    "avatar": data.get("avatar", ""),
                    "xp": data.get("current_xp", 0),
                    "level": data.get("current_level", 0),
                    "streak": data.get("current_streak", 0)
                })
                
            candidates.sort(key=lambda x: (-x["xp"], -x["level"], -x["streak"], x["user_id"]))
            
            for i, p in enumerate(candidates):
                if p["user_id"] == user_id:
                    p["rank"] = i + 1
                    return p
            return None

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
                    ROW_NUMBER() OVER (ORDER BY us.current_xp DESC, us.current_level DESC, us.current_streak DESC, u.id ASC) as rank
                FROM user_stats us
                JOIN users u ON u.id = us.user_id
                WHERE u.is_active = 1
            )
            SELECT * FROM RankedUsers WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()

    @staticmethod
    def get_period_leaderboard(start_date_str, end_date_str, limit=50, period_key=None):
        """
        Get leaderboard for a specific period (weekly/monthly).
        start_date_str and end_date_str should be 'YYYY-MM-DD HH:MM:SS'.
        """
        if FIRESTORE_USER_STATS_ENABLED and period_key:
            from firebase_admin import firestore
            candidate_limit = max(limit * 3, 200)
            docs = get_fs().collection("user_stats")\
                .order_by(period_key, direction=firestore.Query.DESCENDING)\
                .limit(candidate_limit).get()
            
            candidates = []
            for doc in docs:
                data = doc.to_dict()
                if data.get(period_key, 0) == 0:
                    continue # Ignore players with 0 XP in this period
                
                user_id = int(doc.id.replace("sqlite_", "")) if doc.id.startswith("sqlite_") else doc.id
                candidates.append({
                    "user_id": user_id,
                    "full_name": data.get("full_name", ""),
                    "avatar": data.get("avatar", ""),
                    "xp": data.get(period_key, 0),
                    "level": data.get("current_level", 0),
                    "streak": data.get("current_streak", 0)
                })
                
            candidates.sort(key=lambda x: (-x["xp"], -x["level"], -x["streak"], x["user_id"]))
            
            results = []
            for i, p in enumerate(candidates[:limit]):
                p["rank"] = i + 1
                results.append(p)
            return results

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
                ROW_NUMBER() OVER (ORDER BY COALESCE(px.period_xp, 0) DESC, us.current_level DESC, us.current_streak DESC, u.id ASC) as rank
            FROM user_stats us
            JOIN users u ON u.id = us.user_id
            JOIN PeriodXP px ON px.user_id = u.id
            WHERE u.is_active = 1 AND COALESCE(px.period_xp, 0) > 0
            ORDER BY COALESCE(px.period_xp, 0) DESC, us.current_level DESC, us.current_streak DESC, u.id ASC
            LIMIT ?
            """,
            (start_date_str, end_date_str, limit)
        ).fetchall()

    @staticmethod
    def get_user_period_rank(user_id, start_date_str, end_date_str, period_key=None):
        """
        Get the period rank for a specific user.
        """
        if FIRESTORE_USER_STATS_ENABLED and period_key:
            from firebase_admin import firestore
            candidate_limit = 200
            docs = get_fs().collection("user_stats")\
                .order_by(period_key, direction=firestore.Query.DESCENDING)\
                .limit(candidate_limit).get()
            
            candidates = []
            for doc in docs:
                data = doc.to_dict()
                if data.get(period_key, 0) == 0:
                    continue
                
                uid = int(doc.id.replace("sqlite_", "")) if doc.id.startswith("sqlite_") else doc.id
                candidates.append({
                    "user_id": uid,
                    "full_name": data.get("full_name", ""),
                    "avatar": data.get("avatar", ""),
                    "xp": data.get(period_key, 0),
                    "level": data.get("current_level", 0),
                    "streak": data.get("current_streak", 0)
                })
                
            candidates.sort(key=lambda x: (-x["xp"], -x["level"], -x["streak"], x["user_id"]))
            
            for i, p in enumerate(candidates):
                if p["user_id"] == user_id:
                    p["rank"] = i + 1
                    return p
            return None

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
                    ROW_NUMBER() OVER (ORDER BY COALESCE(px.period_xp, 0) DESC, us.current_level DESC, us.current_streak DESC, u.id ASC) as rank
                FROM user_stats us
                JOIN users u ON u.id = us.user_id
                JOIN PeriodXP px ON px.user_id = u.id
                WHERE u.is_active = 1 AND COALESCE(px.period_xp, 0) > 0
            )
            SELECT * FROM RankedUsers WHERE user_id = ?
            """,
            (start_date_str, end_date_str, user_id)
        ).fetchone()
