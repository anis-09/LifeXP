"""
test_daily_rewards.py
---------------------
Sprint 5 — Daily Reward Service Unit Tests

Tests run inside a Flask app context with an in-memory SQLite DB
(same pattern as test_achievement_system.py). Never touches production data.
"""

import sys
import os
import sqlite3
import logging
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Helpers ──────────────────────────────────────────────────────────

PASS = "[PASS]"
FAIL = "[FAIL]"
errors = []
test_number = 0


def check(label, condition, note=""):
    global test_number
    test_number += 1
    tag = PASS if condition else FAIL
    msg = f"  {tag} {label}"
    if note:
        msg += f"  ({note})"
    print(msg)
    if not condition:
        errors.append(label)


# ── In-Memory DB Setup ────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id),
    current_xp INTEGER NOT NULL DEFAULT 0,
    current_coins INTEGER NOT NULL DEFAULT 0,
    current_level INTEGER NOT NULL DEFAULT 1,
    current_streak INTEGER NOT NULL DEFAULT 0,
    longest_streak INTEGER NOT NULL DEFAULT 0,
    missions_completed INTEGER NOT NULL DEFAULT 0,
    last_activity_date TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS daily_rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    day_number INTEGER NOT NULL,
    reward_type TEXT NOT NULL,
    reward_value INTEGER NOT NULL DEFAULT 0,
    claimed INTEGER NOT NULL DEFAULT 0,
    claimed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS xp_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    amount INTEGER NOT NULL,
    source TEXT,
    reference_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS coin_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    amount INTEGER NOT NULL,
    source TEXT,
    reference_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_daily_rewards_user ON daily_rewards(user_id, claimed_at);
"""

# Insert a test user + stats
SEED = """
INSERT INTO users (id, email, password_hash, full_name) VALUES (999, 'test@test.com', 'x', 'Test User');
INSERT INTO user_stats (user_id, current_xp, current_coins, current_level, current_streak, longest_streak, missions_completed)
  VALUES (999, 0, 0, 1, 0, 0, 0);
"""


def make_memory_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    conn.executescript(SEED)
    conn.commit()
    return conn


# ── Flask App Context Setup ───────────────────────────────────────────

import flask
from unittest.mock import patch, MagicMock

app = flask.Flask(__name__)
app.secret_key = "test"

USER_ID = 999


def get_test_db():
    if not hasattr(get_test_db, "_conn") or get_test_db._conn is None:
        get_test_db._conn = make_memory_db()
    return get_test_db._conn


def reset_db():
    """Wipe and re-seed daily_rewards + user_stats for clean state."""
    conn = get_test_db()
    conn.execute("DELETE FROM daily_rewards WHERE user_id = ?", (USER_ID,))
    conn.execute("DELETE FROM xp_transactions WHERE user_id = ?", (USER_ID,))
    conn.execute("DELETE FROM coin_transactions WHERE user_id = ?", (USER_ID,))
    conn.execute("UPDATE user_stats SET current_xp=0, current_coins=0 WHERE user_id=?", (USER_ID,))
    conn.commit()


# ── Import service under test ─────────────────────────────────────────

from constants import DAILY_REWARD_SCHEDULE
from services.daily_reward_service import DailyRewardService

# ── Helper: patch get_db in daily_reward_service ─────────────────────

def run_in_ctx(fn):
    """Run fn inside Flask app context with patched get_db."""
    with app.app_context():
        with patch("services.daily_reward_service.get_db", side_effect=get_test_db), \
             patch("services.daily_reward_service.RewardService") as mock_rs:
            # Stub RewardService so we don't need full DB schema for XP/coins
            mock_rs.grant_xp = MagicMock()
            mock_rs.grant_coins = MagicMock()
            return fn(mock_rs)


# ────────────────────────────────────────────────────────────────────
# TEST 1: New user gets Day 1
# ────────────────────────────────────────────────────────────────────

print("\n--- TEST 1: New user gets Day 1 ---")
reset_db()

def t1(rs):
    day = DailyRewardService._get_next_day_number(USER_ID)
    check("New user day number is 1", day == 1, f"got: {day}")
    sched = DAILY_REWARD_SCHEDULE[day]
    check("Day 1 reward type is 'coins'", sched["type"] == "coins", f"got: {sched['type']}")

run_in_ctx(t1)


# ────────────────────────────────────────────────────────────────────
# TEST 2: get_reward_status returns unclaimed for fresh user
# ────────────────────────────────────────────────────────────────────

print("\n--- TEST 2: Unclaimed status for new user ---")
reset_db()

def t2(rs):
    status = DailyRewardService.get_reward_status(USER_ID)
    check("claimed is False for new user", status["claimed"] == False)
    check("day_number is 1", status["day_number"] == 1)
    check("schedule has 7 items", len(status["schedule"]) == 7)
    check("seconds_until_next > 0", status["seconds_until_next"] > 0)
    check("seconds_until_next <= 86400", status["seconds_until_next"] <= 86400)

run_in_ctx(t2)


# ────────────────────────────────────────────────────────────────────
# TEST 3: Claim Day 1 (Coins) — inserts DB row, calls grant_coins
# ────────────────────────────────────────────────────────────────────

print("\n--- TEST 3: Claim Day 1 (Coins) ---")
reset_db()

def t3(rs):
    result = DailyRewardService.claim(USER_ID)
    check("claim returns day_number=1", result["day_number"] == 1)
    check("coins_granted = 20", result["coins_granted"] == 20, f"got: {result['coins_granted']}")
    check("xp_granted = 0", result["xp_granted"] == 0, f"got: {result['xp_granted']}")
    # Verify grant_coins was called
    check("RewardService.grant_coins called", rs.grant_coins.called)
    # Verify grant_xp NOT called (Day 1 is coins only)
    check("RewardService.grant_xp NOT called for coins-only day", not rs.grant_xp.called)
    # Verify DB row inserted
    conn = get_test_db()
    row = conn.execute("SELECT * FROM daily_rewards WHERE user_id=? AND claimed=1", (USER_ID,)).fetchone()
    check("daily_rewards row inserted", row is not None)
    check("day_number in DB = 1", row["day_number"] == 1)

run_in_ctx(t3)


# ────────────────────────────────────────────────────────────────────
# TEST 4: Double-claim on same day raises ValueError
# ────────────────────────────────────────────────────────────────────

print("\n--- TEST 4: Double-claim raises ValueError ---")
reset_db()

def t4(rs):
    # First claim (valid)
    DailyRewardService.claim(USER_ID)
    # Second claim (should fail)
    raised = False
    try:
        DailyRewardService.claim(USER_ID)
    except ValueError as e:
        raised = True
        check("ValueError message mentions 'claimed'", "claimed" in str(e).lower(), f"got: {e}")
    check("ValueError raised on double-claim", raised)

run_in_ctx(t4)


# ────────────────────────────────────────────────────────────────────
# TEST 5: After Day 1 claim, get_reward_status shows claimed=True
# ────────────────────────────────────────────────────────────────────

print("\n--- TEST 5: Status shows claimed after claim ---")
reset_db()

def t5(rs):
    DailyRewardService.claim(USER_ID)
    status = DailyRewardService.get_reward_status(USER_ID)
    check("claimed=True after claim", status["claimed"] == True)
    check("claimed_at is not None", status["claimed_at"] is not None)

run_in_ctx(t5)


# ────────────────────────────────────────────────────────────────────
# TEST 6: Day cycle — after 7 claims, next day = 1 again
# ────────────────────────────────────────────────────────────────────

print("\n--- TEST 6: 7-day cycle wraps to Day 1 ---")
reset_db()

def t6(rs):
    conn = get_test_db()
    # Insert 7 fake past claims (different days, different dates to bypass today guard)
    for i in range(1, 8):
        past_date = (date.today() - timedelta(days=8 - i)).isoformat()
        conn.execute(
            "INSERT INTO daily_rewards (user_id, day_number, reward_type, reward_value, claimed, claimed_at) "
            "VALUES (?, ?, 'coins', 0, 1, ?)",
            (USER_ID, i, past_date)
        )
    conn.commit()
    next_day = DailyRewardService._get_next_day_number(USER_ID)
    check("After 7 claims, next day_number = 1", next_day == 1, f"got: {next_day}")

run_in_ctx(t6)


# ────────────────────────────────────────────────────────────────────
# TEST 7: Day 2 (XP) — grants XP, no coins
# ────────────────────────────────────────────────────────────────────

print("\n--- TEST 7: Day 2 (XP) grants XP ---")
reset_db()

def t7(rs):
    conn = get_test_db()
    # Insert 1 past claim (Day 1) on a different date to put user on Day 2
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    conn.execute(
        "INSERT INTO daily_rewards (user_id, day_number, reward_type, reward_value, claimed, claimed_at) "
        "VALUES (?, 1, 'coins', 20, 1, ?)",
        (USER_ID, yesterday)
    )
    conn.commit()
    day = DailyRewardService._get_next_day_number(USER_ID)
    check("User is on Day 2", day == 2, f"got: {day}")
    result = DailyRewardService.claim(USER_ID)
    check("Day 2 xp_granted = 50", result["xp_granted"] == 50, f"got: {result['xp_granted']}")
    check("Day 2 coins_granted = 0", result["coins_granted"] == 0, f"got: {result['coins_granted']}")
    check("grant_xp called", rs.grant_xp.called)
    check("grant_coins NOT called for XP day", not rs.grant_coins.called)

run_in_ctx(t7)


# ────────────────────────────────────────────────────────────────────
# TEST 8: _seconds_until_midnight is sane
# ────────────────────────────────────────────────────────────────────

print("\n--- TEST 8: _seconds_until_midnight sanity ---")

def t8(rs):
    secs = DailyRewardService._seconds_until_midnight()
    check("seconds > 0", secs > 0, f"got: {secs}")
    check("seconds <= 86400", secs <= 86400, f"got: {secs}")

run_in_ctx(t8)


# ────────────────────────────────────────────────────────────────────
# TEST 9: Schedule strip has correct states
# ────────────────────────────────────────────────────────────────────

print("\n--- TEST 9: Schedule strip states ---")
reset_db()

def t9(rs):
    strip = DailyRewardService._build_schedule_strip(USER_ID, current_day=3)
    check("Strip has 7 items", len(strip) == 7)
    check("Day 1 is 'past'", strip[0]["state"] == "past", f"got: {strip[0]['state']}")
    check("Day 2 is 'past'", strip[1]["state"] == "past", f"got: {strip[1]['state']}")
    check("Day 3 is 'today'", strip[2]["state"] == "today", f"got: {strip[2]['state']}")
    check("Day 4 is 'upcoming'", strip[3]["state"] == "upcoming", f"got: {strip[3]['state']}")
    check("Day 7 is 'upcoming'", strip[6]["state"] == "upcoming", f"got: {strip[6]['state']}")

run_in_ctx(t9)


# ────────────────────────────────────────────────────────────────────
# TEST 10: get_recent_claims returns history
# ────────────────────────────────────────────────────────────────────

print("\n--- TEST 10: get_recent_claims history ---")
reset_db()

def t10(rs):
    conn = get_test_db()
    for i in range(1, 4):
        past_date = (date.today() - timedelta(days=4 - i)).isoformat()
        conn.execute(
            "INSERT INTO daily_rewards (user_id, day_number, reward_type, reward_value, claimed, claimed_at) "
            "VALUES (?, ?, 'coins', 20, 1, ?)",
            (USER_ID, i, past_date)
        )
    conn.commit()
    claims = DailyRewardService.get_recent_claims(USER_ID, limit=7)
    check("get_recent_claims returns 3 items", len(claims) == 3, f"got: {len(claims)}")
    check("Each item has 'label'", all("label" in c for c in claims))
    check("Each item has 'icon'", all("icon" in c for c in claims))

run_in_ctx(t10)


# ────────────────────────────────────────────────────────────────────
# TEST 11: App routes registered (integration smoke test)
# ────────────────────────────────────────────────────────────────────

print("\n--- TEST 11: Routes registered in app ---")

from app import create_app as real_create_app

real_app = real_create_app()
rules = {str(r) for r in real_app.url_map.iter_rules()}
check("GET /rewards registered", "/rewards" in rules, f"rules: {rules}")
check("GET /api/rewards/status registered", "/api/rewards/status" in rules)
check("POST /api/rewards/claim registered", "/api/rewards/claim" in rules)


# ────────────────────────────────────────────────────────────────────
# TEST 12: /rewards redirects unauthenticated users
# ────────────────────────────────────────────────────────────────────

print("\n--- TEST 12: /rewards auth guard ---")

with real_app.test_client() as client:
    resp = client.get("/rewards")
    check("/rewards redirects unauthenticated", resp.status_code in (301, 302), f"got: {resp.status_code}")


# ── Summary ───────────────────────────────────────────────────────────

print()
if errors:
    print(f"FAILED ({len(errors)} checks):")
    for e in errors:
        print(f"  ✗ {e}")
    sys.exit(1)
else:
    print(f"All {test_number} checks passed. [OK]")
