"""
services/achievement_service.py
-------------------------------
Achievement Service
"""

from __future__ import annotations

import logging
from typing import Dict, List

from database.db import get_db
from models.user_achievement import UserAchievementModel
from services.achievement_rules.registry import AchievementRuleRegistry
from services.reward_service import RewardService

logger = logging.getLogger(__name__)


class AchievementService:
    """
    Service for checking and granting achievements.
    """

    @staticmethod
    def get_user_achievements_with_progress(user_id: int) -> Dict[str, List[Dict]]:
        """
        Returns all unlocked and locked achievements for a user.
        Injects current_progress and progress_percentage into locked achievements.
        """
        unlocked = UserAchievementModel.get_unlocked_for_user(user_id)
        locked = UserAchievementModel.get_locked_for_user(user_id)

        for ach in locked:
            rule = AchievementRuleRegistry.get_rule(ach["condition_key"])
            target = ach["target_value"]
            if rule:
                current_val = rule.get_current_value(user_id)
                percentage = min(100.0, (current_val / target) * 100) if target > 0 else 100.0
                ach["current_progress"] = current_val
                ach["progress_percentage"] = round(percentage, 1)
            else:
                ach["current_progress"] = 0
                ach["progress_percentage"] = 0.0

        return {
            "unlocked": unlocked,
            "locked": locked
        }

    @staticmethod
    def check(user_id: int) -> List[Dict]:
        """
        Check all locked achievements for the user and grant any that are met.
        Returns a list of newly unlocked achievements.
        """
        locked_achievements = UserAchievementModel.get_locked_for_user(user_id)
        newly_unlocked: List[Dict] = []

        for achievement in locked_achievements:
            condition_key = achievement["condition_key"]
            target_value = achievement["target_value"]

            rule = AchievementRuleRegistry.get_rule(condition_key)
            if not rule:
                logger.warning(
                    "Unknown condition_key '%s' for achievement '%s' (id=%s). Skipping.",
                    condition_key,
                    achievement.get("name"),
                    achievement.get("id"),
                )
                continue

            if rule.evaluate(user_id, target_value):
                AchievementService._grant(user_id, achievement)
                newly_unlocked.append(achievement)

        return newly_unlocked

    @staticmethod
    def _grant(user_id: int, achievement: Dict) -> None:
        """
        Unlock the achievement and delegate rewards to RewardService
        inside a single database transaction.
        """
        db = get_db()
        try:
            # Unlock the achievement
            UserAchievementModel.unlock(user_id, achievement["id"])

            # Delegate rewards to RewardService
            xp_reward = achievement.get("xp_reward", 0)
            coin_reward = achievement.get("coin_reward", 0)

            if xp_reward > 0:
                RewardService.grant_xp(
                    user_id=user_id,
                    amount=xp_reward,
                    source="Achievement",
                    reference_id=achievement["id"],
                )

            if coin_reward > 0:
                RewardService.grant_coins(
                    user_id=user_id,
                    amount=coin_reward,
                    source="Achievement",
                    reference_id=achievement["id"],
                )

            db.commit()
        except Exception:
            db.rollback()
            logger.exception(
                "Failed to grant achievement '%s' (id=%s) to user %s.",
                achievement.get("name"),
                achievement.get("id"),
                user_id,
            )
            raise
