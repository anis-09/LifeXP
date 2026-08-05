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
