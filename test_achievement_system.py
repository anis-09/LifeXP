"""
test_achievement_system.py
--------------------------
End-to-end tests for the Sprint 4.1 Achievement System.

Uses a temporary in-memory copy of the DB schema so we never touch
the production database.  All 10 scenarios are tested inside a Flask
app context so get_db() / g work correctly.
"""

import sys, os, sqlite3, logging

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

# Patch config so initialize_database and get_db point at a temp file
import config
import tempfile

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
TEST_DB_PATH = _tmp.name
_tmp.close()

from pathlib import Path
config.DATABASE_PATH = Path(TEST_DB_PATH)

# Now import app (this triggers initialize_database which creates schema)
from app import create_app, initialize_database

# Re-initialise with the patched path
initialize_database()

app = create_app()

# Apply the NEW migration on top of the old schema
conn = sqlite3.connect(TEST_DB_PATH)
# Drop the old achievements / user_achievements tables created by schema.sql
conn.execute("DROP TABLE IF EXISTS user_achievements")
conn.execute("DROP TABLE IF EXISTS achievements")
migration_sql = open("migrations/2024_08_add_achievement_tables.sql").read()
conn.executescript(migration_sql)
conn.commit()
conn.close()

# ── Seed data helper ────────────────────────────────────────────────

def seed_test_data(db):
    """Insert test achievements and a test user with stats."""

    # Make sure we have a test user (id=99)
    db.execute("""
        INSERT OR IGNORE INTO users (id, full_name, email, password_hash)
        VALUES (99, 'TestUser', 'test@lifexp.dev',
                'pbkdf2:sha256:260000$test$abc123')
    """)

    # Create stats for the test user
    db.execute("""
        INSERT OR IGNORE INTO user_stats (user_id, current_level, current_xp,
            current_coins, current_streak, longest_streak,
            last_activity_date, missions_completed, missions_failed)
        VALUES (99, 1, 0, 0, 0, 0, NULL, 0, 0)
    """)

    # Seed achievements covering all rule types
    achievements = [
        # (name, description, category, condition_key, target_value, badge_tier, icon, xp_reward, coin_reward, is_hidden, display_order)
        ("First Steps",      "Complete 1 mission",   "mission", "total_missions", 1,    "bronze", "🎯", 50,  10, 0, 1),
        ("Mission Master",   "Complete 5 missions",  "mission", "total_missions", 5,    "silver", "⭐", 100, 25, 0, 2),
        ("XP Novice",        "Earn 100 XP",          "xp",      "xp_earned",      100,  "bronze", "💎", 25,  5,  0, 3),
        ("XP Warrior",       "Earn 500 XP",          "xp",      "xp_earned",      500,  "gold",   "🔥", 75,  15, 0, 4),
        ("Level Up",         "Reach level 2",        "level",   "level_reached",  2,    "bronze", "📈", 50,  10, 0, 5),
        ("Streak Starter",   "3-day streak",         "streak",  "streak_days",    3,    "bronze", "🔥", 30,  5,  0, 6),
        ("Secret Explorer",  "Hidden achievement",   "secret",  "unknown_key",    1,    "gold",   "🕵️", 100, 50, 1, 7),
    ]

    for a in achievements:
        db.execute("""
            INSERT OR IGNORE INTO achievements
                (name, description, category, condition_key, target_value,
                 badge_tier, icon, xp_reward, coin_reward, is_hidden, display_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, a)

    db.commit()


def set_user_stats(db, **kwargs):
    """Update test user stats."""
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [99]
    db.execute(f"UPDATE user_stats SET {sets} WHERE user_id = ?", vals)
    db.commit()


def clear_user_achievements(db):
    """Remove all achievement unlocks for test user."""
    db.execute("DELETE FROM user_achievements WHERE user_id = 99")
    db.commit()


def get_unlocked_names(db):
    """Return set of achievement names unlocked by test user."""
    rows = db.execute("""
        SELECT a.name FROM user_achievements ua
        JOIN achievements a ON a.id = ua.achievement_id
        WHERE ua.user_id = 99
    """).fetchall()
    return {r[0] for r in rows}


# ── Run tests inside Flask app context ──────────────────────────────

with app.app_context():
    from database.db import get_db
    from services.achievement_service import AchievementService
    from models.user_achievement import UserAchievementModel

    db = get_db()
    seed_test_data(db)

    # ================================================================
    # TEST 1: First Mission Achievement
    # ================================================================
    print("\n--- TEST 1: First Mission Achievement ---")
    print("  Steps: Set missions_completed=1, run AchievementService.check(99)")
    print("  Expected: 'First Steps' unlocked")

    clear_user_achievements(db)
    set_user_stats(db, missions_completed=1, current_xp=0, current_level=1,
                   current_streak=0, longest_streak=0)

    result = AchievementService.check(99)
    unlocked_names = {a["name"] for a in result}

    check("First Steps unlocked", "First Steps" in unlocked_names, f"got: {unlocked_names}")
    check("Mission Master NOT unlocked (need 5)", "Mission Master" not in unlocked_names)
    print(f"  Actual: Unlocked = {unlocked_names}")

    # ================================================================
    # TEST 2: Duplicate Achievement (idempotency)
    # ================================================================
    print("\n--- TEST 2: Duplicate Achievement (idempotency) ---")
    print("  Steps: Run AchievementService.check(99) again with same stats")
    print("  Expected: No new achievements unlocked (First Steps already granted)")

    result2 = AchievementService.check(99)
    check("No duplicate unlocks", len(result2) == 0, f"newly unlocked: {[a['name'] for a in result2]}")
    print(f"  Actual: Newly unlocked = {[a.get('name') for a in result2]}")

    # ================================================================
    # TEST 3: XP Milestone Achievement
    # ================================================================
    print("\n--- TEST 3: XP Milestone Achievement ---")
    print("  Steps: Set current_xp=150, run check")
    print("  Expected: 'XP Novice' unlocked (target=100)")

    clear_user_achievements(db)
    set_user_stats(db, missions_completed=0, current_xp=150, current_level=1,
                   current_streak=0, longest_streak=0)

    result = AchievementService.check(99)
    unlocked_names = {a["name"] for a in result}
    check("XP Novice unlocked", "XP Novice" in unlocked_names, f"got: {unlocked_names}")
    check("XP Warrior NOT unlocked (need 500)", "XP Warrior" not in unlocked_names)
    print(f"  Actual: Unlocked = {unlocked_names}")

    # ================================================================
    # TEST 4: Level Milestone Achievement
    # ================================================================
    print("\n--- TEST 4: Level Milestone Achievement ---")
    print("  Steps: Set current_level=3, run check")
    print("  Expected: 'Level Up' unlocked (target=2)")

    clear_user_achievements(db)
    set_user_stats(db, missions_completed=0, current_xp=0, current_level=3,
                   current_streak=0, longest_streak=0)

    result = AchievementService.check(99)
    unlocked_names = {a["name"] for a in result}
    check("Level Up unlocked", "Level Up" in unlocked_names, f"got: {unlocked_names}")
    print(f"  Actual: Unlocked = {unlocked_names}")

    # ================================================================
    # TEST 5: Streak Achievement
    # ================================================================
    print("\n--- TEST 5: Streak Achievement ---")
    print("  Steps: Set longest_streak=5, run check")
    print("  Expected: 'Streak Starter' unlocked (target=3)")

    clear_user_achievements(db)
    set_user_stats(db, missions_completed=0, current_xp=0, current_level=1,
                   current_streak=5, longest_streak=5)

    result = AchievementService.check(99)
    unlocked_names = {a["name"] for a in result}
    check("Streak Starter unlocked", "Streak Starter" in unlocked_names, f"got: {unlocked_names}")
    print(f"  Actual: Unlocked = {unlocked_names}")

    # ================================================================
    # TEST 6: Multiple Achievements Unlocked in One Action
    # ================================================================
    print("\n--- TEST 6: Multiple Achievements in One Action ---")
    print("  Steps: Set missions=10, xp=600, level=3, streak=5 — run check")
    print("  Expected: All 5 visible achievements unlocked at once")

    clear_user_achievements(db)
    set_user_stats(db, missions_completed=10, current_xp=2600, current_level=3,
                   current_streak=5, longest_streak=5)

    result = AchievementService.check(99)
    unlocked_names = {a["name"] for a in result}

    expected = {"First Steps", "Mission Master", "XP Novice", "XP Warrior",
                "Level Up", "Streak Starter"}
    check("All 6 visible achievements unlocked", expected.issubset(unlocked_names),
          f"missing: {expected - unlocked_names}")
    check("Secret Explorer NOT unlocked (unknown_key)", "Secret Explorer" not in unlocked_names)
    print(f"  Actual: Unlocked = {unlocked_names}")

    # ================================================================
    # TEST 7: Refresh Persistence
    # ================================================================
    print("\n--- TEST 7: Refresh Persistence ---")
    print("  Steps: After test 6, read directly from DB to verify persistence")
    print("  Expected: All 6 achievements still recorded in user_achievements")

    persisted = get_unlocked_names(db)
    check("All 6 persisted in DB after refresh", expected.issubset(persisted),
          f"persisted: {persisted}")
    print(f"  Actual: Persisted = {persisted}")

    # ================================================================
    # TEST 8: Logout/Login Persistence
    # ================================================================
    print("\n--- TEST 8: Logout/Login Persistence ---")
    print("  Steps: Close and re-open DB connection, verify achievements still present")
    print("  Expected: Same 6 achievements persisted")

    # Simulate logout/login by reading from a fresh connection
    fresh_conn = sqlite3.connect(TEST_DB_PATH)
    fresh_conn.row_factory = sqlite3.Row
    rows = fresh_conn.execute("""
        SELECT a.name FROM user_achievements ua
        JOIN achievements a ON a.id = ua.achievement_id
        WHERE ua.user_id = 99
    """).fetchall()
    fresh_names = {r["name"] for r in rows}
    fresh_conn.close()

    check("Achievements survive logout/login", expected.issubset(fresh_names),
          f"got: {fresh_names}")
    print(f"  Actual: After reconnect = {fresh_names}")

    # ================================================================
    # TEST 9: Unknown condition_key Handling
    # ================================================================
    print("\n--- TEST 9: Unknown condition_key Handling ---")
    print("  Steps: 'Secret Explorer' uses condition_key='unknown_key'")
    print("  Expected: Logged warning, not unlocked, no crash")

    # Set up logging to capture the warning
    log_capture = []
    handler = logging.Handler()
    handler.emit = lambda record: log_capture.append(record)

    logger = logging.getLogger("services.achievement_service")
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)

    clear_user_achievements(db)
    set_user_stats(db, missions_completed=10, current_xp=600, current_level=3,
                   current_streak=5, longest_streak=5)

    result = AchievementService.check(99)
    unlocked_names = {a["name"] for a in result}

    check("Secret Explorer NOT unlocked", "Secret Explorer" not in unlocked_names)

    # Check that a warning was logged for 'unknown_key'
    warning_logged = any("unknown_key" in r.getMessage() for r in log_capture)
    check("Warning logged for unknown condition_key", warning_logged,
          f"log records: {len(log_capture)}")
    print(f"  Actual: Unlocked = {unlocked_names}, warnings logged = {len(log_capture)}")

    logger.removeHandler(handler)

    # ================================================================
    # TEST 10: Transaction Rollback on Reward Failure
    # ================================================================
    print("\n--- TEST 10: Transaction Rollback on Reward Failure ---")
    print("  Steps: Monkey-patch RewardService.grant_xp to raise, run check")
    print("  Expected: Achievement NOT persisted in DB, exception handled")

    clear_user_achievements(db)
    set_user_stats(db, missions_completed=1, current_xp=0, current_level=1,
                   current_streak=0, longest_streak=0)

    from services.reward_service import RewardService
    original_grant_xp = RewardService.grant_xp

    def failing_grant_xp(*args, **kwargs):
        raise RuntimeError("Simulated reward failure")

    RewardService.grant_xp = staticmethod(failing_grant_xp)

    rollback_error = None
    try:
        result = AchievementService.check(99)
    except RuntimeError as e:
        rollback_error = str(e)

    RewardService.grant_xp = original_grant_xp

    # Check that the achievement was NOT persisted (rolled back)
    persisted_after_fail = get_unlocked_names(db)
    check("Achievement NOT persisted after reward failure",
          "First Steps" not in persisted_after_fail,
          f"persisted: {persisted_after_fail}")
    check("Exception was raised and propagated", rollback_error is not None,
          f"error: {rollback_error}")
    print(f"  Actual: Persisted = {persisted_after_fail}, error = {rollback_error}")


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
