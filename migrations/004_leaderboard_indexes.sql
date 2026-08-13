--------------------------------------------------
-- SPRINT 6: LEADERBOARD INDEXES
--------------------------------------------------

-- Optimize global leaderboard sorting
CREATE INDEX IF NOT EXISTS idx_user_stats_leaderboard
ON user_stats(current_xp DESC, current_level DESC, current_streak DESC);

-- Optimize weekly/monthly XP aggregations
CREATE INDEX IF NOT EXISTS idx_xp_transactions_date
ON xp_transactions(created_at);
