"""
models/user_stats.py
--------------------
User Stats Model
"""

from database.db import get_db
from config import FIRESTORE_USER_STATS_ENABLED
import datetime

def get_fs():
    from services.firebase_service import get_firestore_client
    return get_firestore_client()


class UserStatsModel:
    """
    User statistics model.
    """

    @staticmethod
    def get(user_id):
        """
        Return user stats.
        """
        if FIRESTORE_USER_STATS_ENABLED:
            doc = get_fs().collection("user_stats").document(f"sqlite_{user_id}").get()
            if doc.exists:
                data = doc.to_dict()
                data["user_id"] = user_id
                return data
            return None

        db = get_db()
        return db.execute(
            """
            SELECT *
            FROM user_stats
            WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()

    @staticmethod
    def create(user_id):
        """
        Create default stats for a user.
        """
        if FIRESTORE_USER_STATS_ENABLED:
            from models.user import get_user_by_id
            user = get_user_by_id(user_id)
            get_fs().collection("user_stats").document(f"sqlite_{user_id}").set({
                "current_level": 1,
                "current_xp": 0,
                "current_coins": 0,
                "current_streak": 0,
                "longest_streak": 0,
                "last_activity_date": None,
                "missions_completed": 0,
                "missions_failed": 0,
                "total_daily_claims": 0,
                "full_name": user["full_name"] if user else "",
                "avatar": user["avatar"] if user else "default.png",
                "last_updated": datetime.datetime.utcnow()
            })
            return

        db = get_db()
        db.execute(
            """
            INSERT INTO user_stats
            (
                user_id
            )
            VALUES
            (
                ?
            )
            """,
            (user_id,)
        )
        db.commit()

    @staticmethod
    def add_xp(user_id, xp):
        """
        Add XP to user.
        """
        if FIRESTORE_USER_STATS_ENABLED:
            from firebase_admin import firestore
            now = datetime.datetime.utcnow()
            year, week, _ = now.isocalendar()
            weekly_key = f"weekly_xp_{year}_{week}"
            monthly_key = f"monthly_xp_{now.year}_{now.month:02d}"
            
            get_fs().collection("user_stats").document(f"sqlite_{user_id}").update({
                "current_xp": firestore.Increment(xp),
                weekly_key: firestore.Increment(xp),
                monthly_key: firestore.Increment(xp),
                "last_updated": firestore.SERVER_TIMESTAMP
            })
            return

        db = get_db()
        db.execute(
            """
            UPDATE user_stats
            SET
                current_xp = current_xp + ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ?
            """,
            (
                xp,
                user_id
            )
        )
        db.commit()

    @staticmethod
    def add_coins(user_id, coins):
        """
        Add coins to user.
        """
        if FIRESTORE_USER_STATS_ENABLED:
            from firebase_admin import firestore
            get_fs().collection("user_stats").document(f"sqlite_{user_id}").update({
                "current_coins": firestore.Increment(coins),
                "last_updated": firestore.SERVER_TIMESTAMP
            })
            return

        db = get_db()
        db.execute(
            """
            UPDATE user_stats
            SET
                current_coins = current_coins + ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ?
            """,
            (
                coins,
                user_id
            )
        )
        db.commit()

    @staticmethod
    def increment_completed_missions(user_id):
        """
        Increase completed mission count.
        """
        if FIRESTORE_USER_STATS_ENABLED:
            from firebase_admin import firestore
            get_fs().collection("user_stats").document(f"sqlite_{user_id}").update({
                "missions_completed": firestore.Increment(1),
                "last_updated": firestore.SERVER_TIMESTAMP
            })
            return

        db = get_db()
        db.execute(
            """
            UPDATE user_stats
            SET
                missions_completed = missions_completed + 1,
                last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ?
            """,
            (user_id,)
        )
        db.commit()

    @staticmethod
    def update_streak(
        user_id,
        current_streak,
        longest_streak,
        last_activity_date
    ):
        """
        Update a user's streak information.
        """
        if FIRESTORE_USER_STATS_ENABLED:
            from firebase_admin import firestore
            get_fs().collection("user_stats").document(f"sqlite_{user_id}").update({
                "current_streak": current_streak,
                "longest_streak": longest_streak,
                "last_activity_date": last_activity_date,
                "last_updated": firestore.SERVER_TIMESTAMP
            })
            return

        db = get_db()
        db.execute(
            """
            UPDATE user_stats
            SET
                current_streak = ?,
                longest_streak = ?,
                last_activity_date = ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ?
            """,
            (
                current_streak,
                longest_streak,
                last_activity_date,
                user_id
            )
        )
        db.commit()

    @staticmethod
    def update_level(user_id, level):
        """
        Update user level.
        """
        if FIRESTORE_USER_STATS_ENABLED:
            from firebase_admin import firestore
            get_fs().collection("user_stats").document(f"sqlite_{user_id}").update({
                "current_level": level,
                "last_updated": firestore.SERVER_TIMESTAMP
            })
            return

        db = get_db()
        db.execute(
            """
            UPDATE user_stats
            SET
                current_level = ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ?
            """,
            (
                level,
                user_id
            )
        )
        db.commit()
