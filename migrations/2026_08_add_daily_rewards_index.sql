-- Migration: 2026_08_add_daily_rewards_index
-- Purpose:   Add performance index on daily_rewards(user_id, claimed_at)
--            to make "was claimed today?" queries fast.
-- Safe:      CREATE INDEX IF NOT EXISTS is idempotent — safe to re-run.

CREATE INDEX IF NOT EXISTS idx_daily_rewards_user
ON daily_rewards(user_id, claimed_at);
