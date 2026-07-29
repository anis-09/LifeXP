"""
services/xp_service.py
----------------------
XP Reward Service
"""

from models.user_stats import UserStatsModel
from models.xp_transaction import XPTransactionModel


class XPService:
    """
    Handles XP rewards and level progression.
    """

    XP_PER_LEVEL = 1000

    @staticmethod
    def reward(
        user_id,
        amount,
        source,
        reference_id
    ):
        """
        Reward XP to a user.
        """

        stats = UserStatsModel.get(user_id)

        if stats is None:
            UserStatsModel.create(user_id)
            stats = UserStatsModel.get(user_id)

        XPTransactionModel.create(
            user_id=user_id,
            source=source,
            reference_id=reference_id,
            amount=amount
        )

        UserStatsModel.add_xp(
            user_id=user_id,
            xp=amount
        )

        UserStatsModel.increment_completed_missions(
            user_id=user_id
        )

        stats = UserStatsModel.get(user_id)

        level = (stats["current_xp"] // XPService.XP_PER_LEVEL) + 1

        UserStatsModel.update_level(
            user_id=user_id,
            level=level
        )

        return {
            "xp": stats["current_xp"],
            "level": level
        }