import logging
import datetime
from database.db import get_db
from config import FIRESTORE_NOTIFICATIONS_ENABLED
from firebase_admin import firestore
from services.firebase_service import get_firestore_client, format_firestore_timestamp, FirebaseConfigurationError

class NotificationService:

    @staticmethod
    def _get_fs():
        try:
            return get_firestore_client()
        except FirebaseConfigurationError as e:
            logging.error(f"Firestore disabled due to config error: {e}")
            return None

    @staticmethod
    def create(user_id, title, message, notif_type="Info"):
        """
        Creates a new persistent notification in the database (SQLite or Firestore).
        """
        if FIRESTORE_NOTIFICATIONS_ENABLED:
            fs = NotificationService._get_fs()
            if fs:
                try:
                    uid = f"sqlite_{user_id}"
                    ref = fs.collection("users").document(uid).collection("notifications").document()
                    data = {
                        "title": title,
                        "message": message,
                        "type": notif_type,
                        "is_read": False,
                        "created_at": firestore.SERVER_TIMESTAMP
                    }
                    ref.set(data)
                    return True
                except Exception as e:
                    logging.error(f"Error creating notification in Firestore: {e}")
                    # Fallback to SQLite is not implemented for individual writes to avoid split-brain
                    return False
        
        # SQLite fallback/default
        try:
            db = get_db()
            db.execute(
                '''
                INSERT INTO notifications (user_id, title, message, type)
                VALUES (?, ?, ?, ?)
                ''',
                (user_id, title, message, notif_type)
            )
            db.commit()
            return True
        except Exception as e:
            logging.error(f"Error creating notification in SQLite: {e}")
            return False

    @staticmethod
    def get_unread_for_user(user_id):
        """
        Retrieves all unread notifications for a user, ordered by newest first.
        """
        if FIRESTORE_NOTIFICATIONS_ENABLED:
            fs = NotificationService._get_fs()
            if fs:
                try:
                    uid = f"sqlite_{user_id}"
                    docs = fs.collection("users").document(uid).collection("notifications") \
                             .where(filter=firestore.FieldFilter("is_read", "==", False)) \
                             .order_by("created_at", direction=firestore.Query.DESCENDING) \
                             .stream()
                    
                    results = []
                    for doc in docs:
                        data = doc.to_dict()
                        results.append({
                            "id": doc.id,
                            "title": data.get("title", ""),
                            "message": data.get("message", ""),
                            "type": data.get("type", "Info"),
                            "created_at": format_firestore_timestamp(data.get("created_at"))
                        })
                    return results
                except Exception as e:
                    logging.error(f"Error fetching notifications from Firestore: {e}")
                    return []

        # SQLite fallback/default
        try:
            db = get_db()
            return db.execute(
                '''
                SELECT id, title, message, type, created_at
                FROM notifications
                WHERE user_id = ? AND is_read = 0
                ORDER BY created_at DESC
                ''',
                (user_id,)
            ).fetchall()
        except Exception as e:
            logging.error(f"Error fetching notifications from SQLite: {e}")
            return []

    @staticmethod
    def mark_as_read(user_id, notification_id=None):
        """
        Marks a specific notification as read, or all if notification_id is None.
        """
        if FIRESTORE_NOTIFICATIONS_ENABLED:
            fs = NotificationService._get_fs()
            if fs:
                try:
                    uid = f"sqlite_{user_id}"
                    coll_ref = fs.collection("users").document(uid).collection("notifications")
                    
                    if notification_id:
                        # Depending on migration format, old notifications might have string IDs like "sqlite_notif_1"
                        coll_ref.document(str(notification_id)).update({"is_read": True})
                    else:
                        # Mark all unread as read (batched)
                        docs = coll_ref.where(filter=firestore.FieldFilter("is_read", "==", False)).stream()
                        batch = fs.batch()
                        count = 0
                        for doc in docs:
                            batch.update(doc.reference, {"is_read": True})
                            count += 1
                            if count >= 500:
                                batch.commit()
                                batch = fs.batch()
                                count = 0
                        if count > 0:
                            batch.commit()
                    return True
                except Exception as e:
                    logging.error(f"Error marking notification(s) as read in Firestore: {e}")
                    return False

        # SQLite fallback/default
        try:
            db = get_db()
            if notification_id:
                db.execute(
                    'UPDATE notifications SET is_read = 1 WHERE user_id = ? AND id = ?',
                    (user_id, notification_id)
                )
            else:
                db.execute(
                    'UPDATE notifications SET is_read = 1 WHERE user_id = ?',
                    (user_id,)
                )
            db.commit()
            return True
        except Exception as e:
            logging.error(f"Error marking notification(s) as read in SQLite: {e}")
            return False

    @staticmethod
    def create_mission_reminder_if_needed(user_id):
        """
        Creates a 'Mission Reminder' notification if the user has incomplete
        daily missions and hasn't received a reminder today.
        """
        try:
            db = get_db()
            # 1. ALWAYS query user_missions from SQLite (not migrated to Firestore reads yet)
            incomplete_dailies = db.execute(
                '''
                SELECT um.id 
                FROM user_missions um
                JOIN missions m ON um.mission_id = m.id
                WHERE um.user_id = ? 
                  AND m.is_daily = 1 
                  AND um.status = 'Pending'
                  AND um.assignment_date = DATE('now', 'localtime')
                LIMIT 1
                ''',
                (user_id,)
            ).fetchone()
            
            if not incomplete_dailies:
                return False

            # 2. Check existence of today's reminder
            if FIRESTORE_NOTIFICATIONS_ENABLED:
                fs = NotificationService._get_fs()
                if fs:
                    uid = f"sqlite_{user_id}"
                    
                    # Compute start of today in UTC for comparison if needed, 
                    # but since server timestamp is UTC, let's just do a basic check
                    # To avoid complex timezone queries on Firestore, we can query last 10 and filter,
                    # or strictly use a where clause if indexed.
                    # Since it's a simple app, let's query the latest reminder notification.
                    docs = fs.collection("users").document(uid).collection("notifications") \
                             .where(filter=firestore.FieldFilter("title", "==", "Daily Mission Reminder")) \
                             .order_by("created_at", direction=firestore.Query.DESCENDING) \
                             .limit(1) \
                             .stream()
                    
                    has_recent = False
                    for doc in docs:
                        dt = doc.to_dict().get("created_at")
                        # Check if dt is today
                        if dt and dt.date() == datetime.datetime.now(datetime.timezone.utc).date():
                            has_recent = True
                    
                    if has_recent:
                        return False
                    
                    # Create the reminder in Firestore
                    return NotificationService.create(
                        user_id=user_id,
                        title="Daily Mission Reminder",
                        message="You have incomplete daily missions. Don't break your streak!",
                        notif_type="Warning"
                    )

            # 2.b SQLite fallback existence check
            existing_reminder = db.execute(
                '''
                SELECT id 
                FROM notifications 
                WHERE user_id = ? 
                  AND title = 'Daily Mission Reminder' 
                  AND DATE(created_at, 'localtime') = DATE('now', 'localtime')
                LIMIT 1
                ''',
                (user_id,)
            ).fetchone()
            
            if existing_reminder:
                return False

            # Create the reminder
            return NotificationService.create(
                user_id=user_id,
                title="Daily Mission Reminder",
                message="You have incomplete daily missions. Don't break your streak!",
                notif_type="Warning"
            )

        except Exception as e:
            logging.error(f"Error checking mission reminders: {e}")
            return False
