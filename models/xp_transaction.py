"""
models/xp_transaction.py
------------------------
XP Transaction Model
"""

from database.db import get_db
from config import FIRESTORE_USER_STATS_ENABLED

def get_fs():
    from services.firebase_service import get_firestore_client
    return get_firestore_client()


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
        if FIRESTORE_USER_STATS_ENABLED:
            from firebase_admin import firestore
            doc_ref = get_fs().collection("users").document(f"sqlite_{user_id}").collection("transactions").document()
            doc_ref.set({
                "currency_type": "xp",
                "source": source,
                "reference_id": reference_id,
                "amount": amount,
                "created_at": firestore.SERVER_TIMESTAMP
            })
            return

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
        if FIRESTORE_USER_STATS_ENABLED:
            from firebase_admin import firestore
            txs = get_fs().collection("users").document(f"sqlite_{user_id}").collection("transactions")\
                .where(filter=firestore.FieldFilter("currency_type", "==", "xp"))\
                .order_by("created_at", direction=firestore.Query.DESCENDING).get()
            return [tx.to_dict() for tx in txs]

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