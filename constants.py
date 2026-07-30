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