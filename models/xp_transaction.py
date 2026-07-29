"""
models/xp_transaction.py
------------------------
XP Transaction Model
"""

from database.db import get_db


class XPTransactionModel:
    """
    XP transaction model.
    """

    @staticmethod
    def create(
        user_id,
        source,
        reference_id,
        amount
    ):
        """
        Create an XP transaction.
        """

        db = get_db()

        db.execute(
            """
            INSERT INTO xp_transactions
            (
                user_id,
                source,
                reference_id,
                amount
            )
            VALUES
            (
                ?, ?, ?, ?
            )
            """,
            (
                user_id,
                source,
                reference_id,
                amount
            )
        )

        db.commit()

    @staticmethod
    def get_all(user_id):
        """
        Return all XP transactions for a user.
        """

        db = get_db()

        return db.execute(
            """
            SELECT *
            FROM xp_transactions
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,)
        ).fetchall()