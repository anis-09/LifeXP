"""
services/achievement_rules/base_rule.py
---------------------------------------
Abstract Base Class for Achievement Rules
"""


class AchievementRule:
    """
    Abstract base class for all achievement rules.
    """

    def get_current_value(self, user_id: int) -> int:
        """
        Get the current progress value for this rule for a user.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement get_current_value()")

    def evaluate(self, user_id: int, target_value: int) -> bool:
        """
        Evaluate if the given user_id has met the target_value for this rule.
        """
        return self.get_current_value(user_id) >= target_value
