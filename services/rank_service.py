"""
services/rank_service.py
------------------------
Player Rank Service

Single source of truth for player rank titles based on level.
Rank thresholds are defined in constants.RANK_THRESHOLDS.

Usage:
    from services.rank_service import RankService
    rank = RankService.get_rank(level)   # e.g. {"title": "Explorer", "level": 7}
"""

from __future__ import annotations

from constants import RANK_THRESHOLDS


class RankService:
    """
    Provides rank title lookups based on player level.
    All rank data is sourced from constants.RANK_THRESHOLDS.
    """

    @staticmethod
    def get_rank(level: int) -> dict:
        """
        Return rank information for a given player level.

        Returns a dict with:
            title (str): Rank name e.g. "Explorer"
            level (int): The level passed in

        Falls back to "Novice" if level is below all thresholds.
        """
        title = "Novice"
        icon = "🌱"
        color = "#10b981"
        next_rank = None
        progress = 100

        for i, (min_lvl, max_lvl, r_title, r_icon, r_color) in enumerate(RANK_THRESHOLDS):
            if max_lvl is None:
                if level >= min_lvl:
                    title = r_title
                    icon = r_icon
                    color = r_color
                    next_rank = None
                    progress = 100
                    break
            elif min_lvl <= level <= max_lvl:
                title = r_title
                icon = r_icon
                color = r_color
                
                # Get next rank if exists
                if i + 1 < len(RANK_THRESHOLDS):
                    next_rank = RANK_THRESHOLDS[i + 1][2]
                    
                # Calculate progress through current rank tier
                tier_size = (max_lvl - min_lvl) + 1
                levels_in = (level - min_lvl)
                progress = int((levels_in / tier_size) * 100)
                break

        return {
            "title": title,
            "icon": icon,
            "color": color,
            "next_rank": next_rank,
            "progress": progress,
            "level": level,
        }

    @staticmethod
    def get_rank_title(level: int) -> str:
        """
        Convenience method — returns just the rank title string.
        """
        return RankService.get_rank(level)["title"]

    @staticmethod
    def all_ranks() -> list:
        """
        Return a list of all rank definitions for display purposes.
        Each item: {"min_level": int, "max_level": int|None, "title": str}
        """
        return [
            {"min_level": mn, "max_level": mx, "title": t}
            for mn, mx, t in RANK_THRESHOLDS
        ]
