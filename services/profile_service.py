"""
services/profile_service.py
----------------------------
Profile Page Data Aggregation Service — Sprint 4.4

Reuses:
    AchievementService  — progress calculations (no duplication)
    UserAchievementModel — unlocked/locked queries
    UserStatsModel      — stats
    RankService         — rank title

Returns a single dict consumed by the profile template.
Zero SQL inside the template.
"""

from __future__ import annotations

from typing import Dict, List

from constants import BADGE_TIER_ORDER, BADGE_TIER_META, XP_PER_LEVEL
from models.user import get_user_by_id
from models.user_achievement import UserAchievementModel
from models.user_stats import UserStatsModel
from models.achievement import AchievementModel
from services.achievement_service import AchievementService
from services.rank_service import RankService


class ProfileService:
    """
    Aggregates all data needed to render the player profile page.
    """

    @staticmethod
    def get_profile_data(user_id: int) -> Dict | None:
        """
        Build the full profile data dict for a user.

        Returns None if the user is not found.
        """
        user = get_user_by_id(user_id)
        if not user:
            return None

        stats = UserStatsModel.get(user_id)
        if not stats:
            UserStatsModel.create(user_id)
            stats = UserStatsModel.get(user_id)

        current_level = stats["current_level"]
        current_xp    = stats["current_xp"]

        # Rank from single source of truth
        rank_info  = RankService.get_rank(current_level)
        rank_title = rank_info["title"]

        # XP progress bar for hero section
        level_start_xp          = (current_level - 1) * XP_PER_LEVEL
        level_end_xp             = current_level * XP_PER_LEVEL
        xp_into_level            = current_xp - level_start_xp
        xp_required_this_level   = level_end_xp - level_start_xp
        xp_progress              = (
            int((xp_into_level / xp_required_this_level) * 100)
            if xp_required_this_level else 0
        )

        # Achievements — reuse AchievementService (no duplicated logic)
        achievements_data  = AchievementService.get_user_achievements_with_progress(user_id)
        unlocked           = achievements_data["unlocked"]
        locked_with_progress = achievements_data["locked"]

        # Filter hidden from locked progress list (visible ones only)
        locked_visible = [a for a in locked_with_progress if not a.get("is_hidden")]

        # Group unlocked achievements by badge_tier for the collection grid
        tier_groups = ProfileService._group_by_tier(unlocked)

        # Recent achievement timeline (newest first, limit 10)
        recent_timeline = UserAchievementModel.latest_unlocked(user_id, limit=10)

        # Count unlocked and total
        achievements_unlocked = len(unlocked)
        achievements_total = len(AchievementModel.get_visible())
        achievements_completion_pct = int((achievements_unlocked / achievements_total) * 100) if achievements_total > 0 else 0

        return {
            "user":                  user,
            "stats":                 stats,
            "rank_info":             rank_info,
            "rank_title":            rank_title,

            # XP progress
            "current_xp":            current_xp,
            "current_level":         current_level,
            "level_start_xp":        level_start_xp,
            "level_end_xp":          level_end_xp,
            "xp_into_level":         xp_into_level,
            "xp_required_this_level": xp_required_this_level,
            "xp_progress":           xp_progress,

            # Achievement collection
            "tier_groups":           tier_groups,
            "tier_meta":             BADGE_TIER_META,
            "recent_timeline":       recent_timeline,
            "locked_achievements":   locked_visible,
            "achievements_unlocked": achievements_unlocked,
            "achievements_total":    achievements_total,
            "achievements_completion_pct": achievements_completion_pct,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _group_by_tier(unlocked: List[Dict]) -> List[Dict]:
        """
        Group a list of unlocked achievements by badge_tier.

        Returns a list of dicts in canonical tier order:
            [
                {
                    "tier":  "bronze",
                    "meta":  {"label": "Bronze", "emoji": "🥉"},
                    "items": [achievement_dict, ...]
                },
                ...
            ]

        Tiers with zero unlocked achievements are omitted.
        """
        buckets: Dict[str, List[Dict]] = {tier: [] for tier in BADGE_TIER_ORDER}

        for ach in unlocked:
            tier = (ach.get("badge_tier") or "bronze").lower()
            if tier in buckets:
                buckets[tier].append(ach)
            else:
                # Unknown tier — fall back to bronze bucket
                buckets["bronze"].append(ach)

        result = []
        for tier in BADGE_TIER_ORDER:
            items = buckets[tier]
            if items:
                result.append({
                    "tier":  tier,
                    "meta":  BADGE_TIER_META.get(tier, {"label": tier.title(), "emoji": "🏅"}),
                    "items": items,
                })

        return result
