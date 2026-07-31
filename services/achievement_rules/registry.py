"""
services/achievement_rules/registry.py
--------------------------------------
Registry for achievement rule classes and lazy initialization.
"""

from __future__ import annotations


from typing import Any, Dict, List, Type

# Import rule classes (do not instantiate)
from .mission_rule import MissionRule
from .streak_rule import StreakRule
from .xp_rule import XPRule
from .level_rule import LevelRule

# Shared constants for condition keys (replace magic strings)
TOTAL_MISSIONS = "total_missions"
STREAK_DAYS = "streak_days"
XP_EARNED = "xp_earned"
LEVEL_REACHED = "level_reached"


class AchievementRuleRegistry:
    """Read‑only registry that maps condition keys to rule classes.

    Rules are instantiated lazily when ``get_rule`` is called.
    """

    # Mapping of condition key -> rule class (not instantiated)
    _rule_classes: Dict[str, Type[Any]] = {
        TOTAL_MISSIONS: MissionRule,
        STREAK_DAYS: StreakRule,
        XP_EARNED: XPRule,
        LEVEL_REACHED: LevelRule,
    }

    # Cache of instantiated rule objects
    _instances: Dict[str, Any] = {}

    @classmethod
    def get_rule(cls, condition_key: str) -> Any:
        """Return a rule instance for the given ``condition_key``.

        The rule class is instantiated on first request and then cached.
        """
        if condition_key not in cls._rule_classes:
            return None
        if condition_key not in cls._instances:
            rule_cls = cls._rule_classes[condition_key]
            cls._instances[condition_key] = rule_cls()
        return cls._instances[condition_key]

    @classmethod
    def get_all_rules(cls) -> List[Any]:
        """Return a list of all rule instances, initializing any that are not yet created."""
        return [cls.get_rule(key) for key in cls._rule_classes]

    # Prevent external modification
    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("AchievementRuleRegistry is read‑only")
