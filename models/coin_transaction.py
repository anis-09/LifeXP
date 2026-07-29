"""
models/coin_transaction.py
--------------------------
Coin Transaction Model
"""

from database.db import get_db


class CoinTransactionModel:
    """
    Coin transaction model.
    """

    @staticmethod
    def create(
        user_id,
        source,
        reference_id,
        amount
    ):
        """
        Create a coin transaction.
        """

        db = get_db()

        db.execute(
            """
            INSERT INTO coin_transactions
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
        Return all coin transactions for a user.
        """

        db = get_db()

        return db.execute(
            """
            SELECT *
            FROM coin_transactions
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,)
        ).fetchall()