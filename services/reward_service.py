"""
services/reward_service.py
-------------------------
Reward Coordination Service
"""

from services.coin_service import CoinService
from services.level_service import LevelService
from services.streak_service import StreakService
from services.xp_service import XPService


class RewardService:
    """
    Coordinates rewards issued for completed missions.
    """

    @staticmethod
    def reward_user(user_id, mission):
        """
        Reward a user with the XP and coins defined by a mission.
        Also updates the user's streak and awards milestone bonuses when due.
        """

        previous_level = RewardService._get_current_level(user_id)

        RewardService._reward_xp(user_id=user_id, mission=mission)
        RewardService._reward_coins(user_id=user_id, mission=mission)

        # Update streak — must run after the mission reward so the
        # activity date is correct for today.
        streak_result = StreakService.update_streak(user_id)
        current_streak = streak_result["current_streak"]
        longest_streak = streak_result["longest_streak"]

        # Check for a streak milestone and award bonus rewards.
        xp_bonus, coin_bonus = StreakService.get_streak_bonus(current_streak)
        streak_milestone = current_streak if (xp_bonus or coin_bonus) else None

        if xp_bonus:
            XPService.reward(
                user_id=user_id,
                amount=xp_bonus,
                source="StreakBonus",
                reference_id=current_streak
            )

        if coin_bonus:
            CoinService.reward(
                user_id=user_id,
                amount=coin_bonus,
                source="StreakBonus",
                reference_id=current_streak
            )

        current_level = RewardService._get_current_level(user_id)

        return {
            "xp": mission["xp_reward"],
            "coins": mission["coin_reward"],
            "level": current_level,
            "level_up": current_level > previous_level,
            "streak": current_streak,
            "longest_streak": longest_streak,
            "streak_milestone": streak_milestone,
            "bonus_xp": xp_bonus,
            "bonus_coins": coin_bonus,
        }

    @staticmethod
    def _get_current_level(user_id):
        """
        Return the user's level based on current total XP.
        """

        total_xp = XPService.get_total_xp(user_id)

        return LevelService.calculate_level(total_xp)

    @staticmethod
    def _reward_xp(user_id, mission):
        """
        Delegate XP rewards to XPService.
        """

        return XPService.reward(
            user_id=user_id,
            amount=mission["xp_reward"],
            source="Mission",
            reference_id=mission["id"]
        )

    @staticmethod
    def _reward_coins(user_id, mission):
        """
        Delegate coin rewards to CoinService.
        """

        return CoinService.reward(
            user_id=user_id,
            amount=mission["coin_reward"],
            source="Mission",
            reference_id=mission["id"]
        )

    # ------------------------------------------------------------------
    # Generic reward helpers (used by AchievementService and others)
    # ------------------------------------------------------------------

    @staticmethod
    def grant_xp(user_id: int, amount: int, source: str, reference_id: int) -> None:
        """
        Award XP to a user. Centralises all XP issuance through RewardService.
        """
        if amount > 0:
            XPService.reward(
                user_id=user_id,
                amount=amount,
                source=source,
                reference_id=reference_id,
            )

    @staticmethod
    def grant_coins(user_id: int, amount: int, source: str, reference_id: int) -> None:
        """
        Award coins to a user. Centralises all coin issuance through RewardService.
        """
        if amount > 0:
            CoinService.reward(
                user_id=user_id,
                amount=amount,
                source=source,
                reference_id=reference_id,
            )
