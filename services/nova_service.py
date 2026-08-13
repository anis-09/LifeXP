"""
services/nova_service.py
------------------------
Service for generating contextual AI coaching messages (Nova).
"""

from datetime import datetime
import random

from constants import XP_PER_LEVEL


class NovaService:
    """
    Rule-based engine for the Nova AI Coach.
    Generates personalized daily motivation, mission suggestions,
    and streak encouragement based on user stats.
    """

    @staticmethod
    def generate_daily_coaching(user_id, stats, today_missions):
        """
        Analyze user state and return a dictionary containing the
        Nova message, an icon, and a specific call to action if any.
        """
        if not stats:
            return NovaService._fallback_message()

        current_streak = stats["current_streak"] if "current_streak" in stats.keys() else 0
        current_level = stats["current_level"] if "current_level" in stats.keys() else 1
        current_xp = stats["current_xp"] if "current_xp" in stats.keys() else 0

        # Calculate XP needed for next level
        level_start_xp = (current_level - 1) * XP_PER_LEVEL
        level_end_xp = current_level * XP_PER_LEVEL
        xp_remaining = max(level_end_xp - current_xp, 0)

        # Analyze daily missions
        total_missions = len(today_missions)
        completed_missions = sum(1 for m in today_missions if m["status"] == "Completed")
        uncompleted_missions = total_missions - completed_missions
        all_completed = (total_missions > 0 and uncompleted_missions == 0)

        hour = datetime.now().hour
        is_morning = 5 <= hour < 12
        is_evening = 17 <= hour < 23

        # Rule 1: All daily missions complete
        if all_completed:
            messages = [
                "Incredible work today, Hero! Rest up, you've earned it.",
                "You crushed all your daily missions! Consistency builds mastery.",
                "Perfect day! The Nova system is highly impressed by your dedication."
            ]
            return {
                "message": random.choice(messages),
                "icon": "🌟",
                "type": "success",
                "cta_text": "View Achievements",
                "cta_link": "/profile"
            }

        # Rule 2: Close to leveling up (less than 20% of level xp left)
        if xp_remaining > 0 and xp_remaining <= (XP_PER_LEVEL * 0.2):
            return {
                "message": f"You're only {xp_remaining} XP away from Level {current_level + 1}! Complete a mission right now to level up.",
                "icon": "⚡",
                "type": "goal",
                "cta_text": "Complete Mission",
                "cta_link": "#daily-missions-section"
            }

        # Rule 3: High streak encouragement
        if current_streak >= 3 and uncompleted_missions > 0:
            if is_evening:
                return {
                    "message": f"The day is ending, but your {current_streak}-day streak doesn't have to! Complete a mission to keep the fire alive.",
                    "icon": "🔥",
                    "type": "streak",
                    "cta_text": "Save Streak",
                    "cta_link": "#daily-missions-section"
                }
            else:
                return {
                    "message": f"You're on a magnificent {current_streak}-day streak! Let's keep that momentum going today.",
                    "icon": "🔥",
                    "type": "streak",
                    "cta_text": "View Missions",
                    "cta_link": "#daily-missions-section"
                }

        # Rule 4: Morning motivation (uncompleted missions)
        if is_morning and uncompleted_missions > 0:
            messages = [
                "Morning, Hero! A new day brings new opportunities. Let's tackle those missions.",
                "Rise and shine! The best time to build a habit is right now.",
                "Good morning! Plan your day, execute your missions, and claim your rewards."
            ]
            return {
                "message": random.choice(messages),
                "icon": "🌅",
                "type": "motivation",
                "cta_text": "Start Day",
                "cta_link": "#daily-missions-section"
            }

        # Rule 5: Evening push
        if is_evening and uncompleted_missions > 0:
            return {
                "message": f"Evening check-in! You still have {uncompleted_missions} mission(s) left. Don't let today slip away.",
                "icon": "🌙",
                "type": "productivity",
                "cta_text": "Finish Strong",
                "cta_link": "#daily-missions-section"
            }

        # Fallback Rule: General Productivity / Motivation
        return NovaService._fallback_message()

    @staticmethod
    def _fallback_message():
        """
        Return a random generic motivation message.
        """
        messages = [
            "Every epic journey begins with a single step. Take that step today!",
            "Small daily improvements are the key to staggering long-term results.",
            "Your potential is limitless. Complete missions to unlock it.",
            "Discipline is choosing between what you want now and what you want most."
        ]
        return {
            "message": random.choice(messages),
            "icon": "✨",
            "type": "motivation",
            "cta_text": "Explore Missions",
            "cta_link": "#daily-missions-section"
        }
