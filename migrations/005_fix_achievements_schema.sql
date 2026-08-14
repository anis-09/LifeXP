-- migrations/005_fix_achievements_schema.sql
-- -------------------------------------------
-- Upgrade achievements and user_achievements to Sprint 4.2 canonical schema.
--
-- Root cause: The live DB was created with an older minimal schema that used
-- column names 'earned_at' (user_achievements) and a reduced achievements
-- structure without category, condition_key, badge_tier, etc.
-- All application code and schema.sql expect the Sprint 4.2 structure with
-- 'unlocked_at'. Both tables have 0 rows so DROP + CREATE is fully safe.
--
-- Safe because:
--   - user_achievements has 0 rows (verified by QA on 2026-08-14).
--   - achievements has 0 rows (verified by QA on 2026-08-14).
--   - Uses CREATE TABLE IF NOT EXISTS after DROP so subsequent runs are no-ops
--     once the correct table is in place.

PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS user_achievements;
DROP TABLE IF EXISTS achievements;

CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    condition_key TEXT NOT NULL,
    target_value INTEGER NOT NULL,
    badge_tier TEXT CHECK(badge_tier IN ('bronze', 'silver', 'gold', 'platinum', 'diamond', 'legendary')),
    icon TEXT,
    xp_reward INTEGER DEFAULT 0,
    coin_reward INTEGER DEFAULT 0,
    is_hidden INTEGER NOT NULL DEFAULT 0,
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_achievements (
    user_id INTEGER NOT NULL,
    achievement_id INTEGER NOT NULL,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, achievement_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE
);

PRAGMA foreign_keys = ON;
