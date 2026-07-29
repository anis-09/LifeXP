"""
models/user_mission.py
----------------------
User Mission Assignment Model
"""

from database.db import get_db


class UserMissionModel:
    """
    Handles user-specific mission assignments.
    """

    @staticmethod
    def assign_mission(user_id, mission_id):
        """
        Assign a mission to a user for today.
        """

        db = get_db()

        cursor = db.execute(
            """
            INSERT INTO user_missions
            (
                user_id,
                mission_id
            )
            VALUES (?, ?)
            """,
            (
                user_id,
                mission_id
            )
        )

        db.commit()

        return cursor.lastrowid

    @staticmethod
    def has_assignment_today(user_id, mission_id):
        """
        Check whether today's assignment already exists.
        """

        db = get_db()

        assignment = db.execute(
            """
            SELECT id
            FROM user_missions
            WHERE
                user_id = ?
                AND mission_id = ?
                AND assignment_date = DATE('now')
            """,
            (
                user_id,
                mission_id
            )
        ).fetchone()

        return assignment is not None

    @staticmethod
    def get_today_missions(user_id):
        """
        Return today's assigned missions.
        """

        db = get_db()

        return db.execute(
            """
            SELECT
                um.*,
                m.title,
                m.description,
                m.difficulty,
                m.xp_reward,
                m.coin_reward,
                m.category_id,
                m.is_daily
            FROM user_missions um
            INNER JOIN missions m
                ON m.id = um.mission_id
            WHERE
                um.user_id = ?
                AND um.assignment_date = DATE('now')
            ORDER BY
                um.assigned_at ASC
            """,
            (user_id,)
        ).fetchall()

    @staticmethod
    def get_assignment(assignment_id):
        """
        Return one assignment.
        """

        db = get_db()

        assignment = db.execute(
            """
            SELECT *
            FROM user_missions
            WHERE id = ?
            """,
            (assignment_id,)
        ).fetchone()

        return dict(assignment) if assignment else None

    @staticmethod
    def complete_assignment(assignment_id):
        """
        Mark an assignment completed.
        """

        db = get_db()

        db.execute(
            """
            UPDATE user_missions
            SET
                status='Completed',
                completed_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (assignment_id,)
        )

        db.commit()

    @staticmethod
    def update_progress(assignment_id, progress):
        """
        Update assignment progress.
        """

        db = get_db()

        db.execute(
            """
            UPDATE user_missions
            SET progress=?
            WHERE id=?
            """,
            (
                progress,
                assignment_id
            )
        )

        db.commit()

    @staticmethod
    def get_history(user_id):
        """
        Return assignment history.
        """

        db = get_db()

        return db.execute(
            """
            SELECT
                um.*,
                m.title,
                m.description
            FROM user_missions um
            INNER JOIN missions m
                ON m.id = um.mission_id
            WHERE
                um.user_id = ?
            ORDER BY
                um.assignment_date DESC,
                um.assigned_at DESC
            """,
            (user_id,)
        ).fetchall()