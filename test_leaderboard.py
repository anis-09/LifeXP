"""
test_leaderboard.py
-------------------
End-to-end tests for the Sprint 6 Leaderboard.
Uses a temporary in-memory copy of the DB schema.
"""

import sys, os, sqlite3, tempfile
from pathlib import Path
from datetime import date, timedelta

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

# ── Bootstrap Flask app with a TEMPORARY test DB ────────────────────

import config
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
TEST_DB_PATH = _tmp.name
_tmp.close()

config.DATABASE_PATH = Path(TEST_DB_PATH)

from app import create_app, initialize_database
from database.db import get_db

initialize_database()
app = create_app()

def seed_test_data(db):
    # Clear existing data from seed.sql and child tables
    db.execute("DELETE FROM notifications")
    db.execute("DELETE FROM daily_rewards")
    db.execute("DELETE FROM user_achievements")
    db.execute("DELETE FROM user_missions")
    db.execute("DELETE FROM user_stats")
    db.execute("DELETE FROM xp_transactions")
    db.execute("DELETE FROM users")
    db.commit()

    # Create 3 users
    users = [
        (1, 'Alpha', 'alpha@test.com'),
        (2, 'Beta', 'beta@test.com'),
        (3, 'Charlie', 'charlie@test.com')
    ]
    for u in users:
        db.execute("INSERT INTO users (id, full_name, email, password_hash) VALUES (?, ?, ?, 'hash')", u)

    # user_stats for each
    # Alpha: 1000 XP, Level 5, Streak 10
    # Beta: 1000 XP, Level 5, Streak 5
    # Charlie: 500 XP, Level 3, Streak 2
    stats = [
        (1, 5, 1000, 10),
        (2, 5, 1000, 5),
        (3, 3, 500, 2)
    ]
    for s in stats:
        db.execute("INSERT INTO user_stats (user_id, current_level, current_xp, current_streak) VALUES (?, ?, ?, ?)", s)

    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    last_week = start_of_week - timedelta(days=7)

    # xp_transactions
    # Alpha: 100 XP today (this week/month)
    # Beta: 200 XP today (this week/month)
    # Charlie: 0 XP this week, but 50 XP last week
    txs = [
        (1, 100, f"{today.isoformat()} 12:00:00"),
        (2, 200, f"{today.isoformat()} 12:00:00"),
        (3, 50, f"{last_week.isoformat()} 12:00:00")
    ]
    for tx in txs:
        db.execute("INSERT INTO xp_transactions (user_id, source, amount, created_at) VALUES (?, 'test', ?, ?)", tx)

    db.commit()

# ── Run tests inside Flask app context ──────────────────────────────

with app.app_context():
    from services.leaderboard_service import LeaderboardService

    db = get_db()
    seed_test_data(db)

    # TEST 1: Global Leaderboard Ranking & Tie-Breakers
    print("\n--- TEST 1: Global Leaderboard ---")
    data = LeaderboardService.get_leaderboard_data(user_id=3, period="global")
    top = data["top_players"]
    check("Global returns 3 users", len(top) == 3)
    check("Alpha is rank 1 (tie on XP and Level, wins on streak)", top[0]["user_id"] == 1 and top[0]["rank"] == 1)
    check("Beta is rank 2", top[1]["user_id"] == 2 and top[1]["rank"] == 2)
    check("Charlie is rank 3", top[2]["user_id"] == 3 and top[2]["rank"] == 3)
    
    # TEST 2: Weekly Leaderboard
    print("\n--- TEST 2: Weekly Leaderboard ---")
    data = LeaderboardService.get_leaderboard_data(user_id=1, period="weekly")
    top = data["top_players"]
    check("Weekly returns 2 users (Charlie has 0 XP this week)", len(top) == 2)
    check("Beta is rank 1 (200 XP vs 100 XP)", top[0]["user_id"] == 2 and top[0]["rank"] == 1)
    check("Alpha is rank 2", top[1]["user_id"] == 1 and top[1]["rank"] == 2)

    # TEST 3: Current User Rank row
    print("\n--- TEST 3: Current User Rank Row ---")
    data = LeaderboardService.get_leaderboard_data(user_id=3, period="weekly")
    user_row = data["user_rank_row"]
    check("Charlie gets a default row since he has 0 XP this week", user_row is not None)
    check("Charlie's rank is '-'", user_row["rank"] == "-")
    check("Charlie's XP is shown as 0 for weekly period", user_row["xp"] == 0)

    # TEST 4: Friends Tab
    print("\n--- TEST 4: Friends Tab ---")
    data = LeaderboardService.get_leaderboard_data(user_id=1, period="friends")
    check("Friends returns empty players", len(data["top_players"]) == 0)
    check("Friends returns None for user_rank_row", data["user_rank_row"] is None)

# ── Cleanup ─────────────────────────────────────────────────────────
try:
    os.unlink(TEST_DB_PATH)
except OSError:
    pass

# ── Summary ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
if errors:
    print(f"FAILED ({len(errors)} / {test_number} checks):")
    for e in errors:
        print(f"  ✗ {e}")
    sys.exit(1)
else:
    print(f"All {test_number} checks passed. [OK]")
