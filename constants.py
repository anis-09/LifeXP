"""
LifeXP Constants
Version: 1.0
"""

# -----------------------------
# Mission Status
# -----------------------------

MISSION_STATUS = (
    "Pending",
    "In Progress",
    "Completed",
    "Skipped",
)

# -----------------------------
# Mission Difficulty
# -----------------------------

MISSION_DIFFICULTY = (
    "Easy",
    "Medium",
    "Hard",
    "Epic",
)

# -----------------------------
# Mission Categories
# -----------------------------

MISSION_CATEGORIES = (
    "Study",
    "Fitness",
    "Reading",
    "Coding",
    "Meditation",
    "Health",
    "Work",
    "Personal",
)

# -----------------------------
# Notification Types
# -----------------------------

NOTIFICATION_TYPES = (
    "Success",
    "Warning",
    "Info",
    "Achievement",
    "Reward",
    "LevelUp",
)

# -----------------------------
# Themes
# -----------------------------

THEMES = (
    "dark",
    "light",
)

# -----------------------------
# Languages
# -----------------------------

LANGUAGES = (
    "en",
    "hi",
)

# -----------------------------
# XP Rules
# -----------------------------

LEVEL_XP = {
    1: 0,
    2: 100,
    3: 250,
    4: 450,
    5: 700,
    6: 1000,
}

# XP required to complete a single level (flat-band model used by XPService
# and the dashboard progress bar). A single shared definition — never redefine
# this value in other modules; import from here instead.
XP_PER_LEVEL = 1000

# -----------------------------
# Streak Milestone Bonuses
# -----------------------------

# Maps consecutive-day streak counts to (xp_bonus, coin_bonus).
# When a user's streak reaches one of these thresholds after completing a
# mission, the bonus is awarded automatically via RewardService.
# Import from here — never hard-code milestone values in services.
STREAK_MILESTONES = {
    7:  (50,  20),
    14: (100, 50),
    30: (200, 100),
}

# -----------------------------
# Rank System
# -----------------------------

# Maps (min_level, max_level_inclusive) -> (title, icon, color).
# Evaluated in order — first matching range wins.
# Import from here; never hard-code rank strings in services or templates.
RANK_THRESHOLDS = [
    (1,  4,  "Novice",   "🌱", "#10b981"),
    (5,  9,  "Explorer", "🧭", "#06b6d4"),
    (10, 19, "Warrior",  "⚔️", "#8b5cf6"),
    (20, 34, "Champion", "🏆", "#f59e0b"),
    (35, 49, "Master",   "👁️", "#ec4899"),
    (50, None, "Legend", "👑", "#eab308"),
]

# -----------------------------
# Badge Tier Display Order
# -----------------------------

# Ordered list used by ProfileService to group achievements by tier.
# Add new tiers here — the grouping logic is fully data-driven.
BADGE_TIER_ORDER = [
    "bronze",
    "silver",
    "gold",
    "platinum",
    "diamond",
    "legendary",
]

# Tier display metadata (emoji label and CSS variable name).
BADGE_TIER_META = {
    "bronze":    {"label": "Bronze",    "emoji": "🥉"},
    "silver":    {"label": "Silver",    "emoji": "🥈"},
    "gold":      {"label": "Gold",      "emoji": "🥇"},
    "platinum":  {"label": "Platinum",  "emoji": "💎"},
    "diamond":   {"label": "Diamond",   "emoji": "💠"},
    "legendary": {"label": "Legendary", "emoji": "👑"},
}

# -----------------------------
# Daily Reward Schedule
# -----------------------------

# 7-day rotating daily login reward cycle (repeats after Day 7).
# reward_type values:
#   "coins"       — award coin_value coins immediately
#   "xp"          — award xp_value XP immediately
#   "chest"       — award coin_value coins + xp_value XP immediately
#                   (full chest-opening mechanic deferred to Phase 7)
#   "xp_bonus"    — award xp_value XP immediately
#                   (duration-based XP boosters deferred to Phase 7)
#   "avatar_item" — record in DB; no physical item granted until Phase 7
# Never hard-code these values in services — always import from here.
DAILY_REWARD_SCHEDULE = {
    1: {
        "type":       "coins",
        "xp_value":   0,
        "coin_value": 20,
        "label":      "20 Coins",
        "icon":       "💰",
        "color":      "--color-gold",
    },
    2: {
        "type":       "xp",
        "xp_value":   50,
        "coin_value": 0,
        "label":      "50 XP",
        "icon":       "⚡",
        "color":      "--color-purple",
    },
    3: {
        "type":       "chest",
        "xp_value":   20,
        "coin_value": 30,
        "label":      "Common Chest",
        "icon":       "📦",
        "color":      "--color-cyan",
    },
    4: {
        "type":       "avatar_item",
        "xp_value":   0,
        "coin_value": 0,
        "label":      "Avatar Item",
        "icon":       "🎁",
        "color":      "--color-pink",
    },
    5: {
        "type":       "coins",
        "xp_value":   0,
        "coin_value": 50,
        "label":      "50 Coins",
        "icon":       "💰",
        "color":      "--color-gold",
    },
    6: {
        "type":       "xp_bonus",
        "xp_value":   100,
        "coin_value": 0,
        "label":      "XP Bonus",
        "icon":       "🚀",
        "color":      "--color-purple",
    },
    7: {
        "type":       "chest",
        "xp_value":   200,
        "coin_value": 100,
        "label":      "Epic Chest",
        "icon":       "🏆",
        "color":      "--color-gold",
    },
}