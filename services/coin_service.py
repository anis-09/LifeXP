"""
services/coin_service.py
------------------------
Coin Reward Service
"""

from models.user_stats import UserStatsModel
from models.coin_transaction import CoinTransactionModel


class CoinService:
    """
    Handles coin rewards and transactions.
    """

    @staticmethod
    def reward(
        user_id,
        amount,
        source,
        reference_id
    ):
        """
        Reward coins to a user.
        """

        stats = UserStatsModel.get(user_id)

        if stats is None:
            UserStatsModel.create(user_id)
            stats = UserStatsModel.get(user_id)

        CoinTransactionModel.create(
            user_id=user_id,
            source=source,
            reference_id=reference_id,
            amount=amount
        )

        UserStatsModel.add_coins(
            user_id=user_id,
            coins=amount
        )

        stats = UserStatsModel.get(user_id)

        return {
            "coins": stats["current_coins"]
        }