import logging
from database.db import get_db

class NotificationService:

    @staticmethod
    def create(user_id, title, message, notif_type="Info"):
        """
        Creates a new persistent notification in the database.
        """
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
            logging.error(f"Error creating notification: {e}")
            return False

    @staticmethod
    def get_unread_for_user(user_id):
        """
        Retrieves all unread notifications for a user, ordered by newest first.
        """
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
            logging.error(f"Error fetching notifications: {e}")
            return []

    @staticmethod
    def mark_as_read(user_id, notification_id=None):
        """
        Marks a specific notification as read, or all if notification_id is None.
        """
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
            logging.error(f"Error marking notification(s) as read: {e}")
            return False

    @staticmethod
    def create_mission_reminder_if_needed(user_id):
        """
        Creates a 'Mission Reminder' notification if the user has incomplete
        daily missions and hasn't received a reminder today.
        """
        try:
            db = get_db()
            # Check if there are incomplete daily missions for today
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

            # Check if a reminder was already created today
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
