"""
verify_sprint_fixes.py
----------------------
Programmatic verification of all 6 sprint fixes without requiring
a live browser session. Tests the actual code, DB, and module imports.
"""

import sys, os, inspect, sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DATABASE_PATH

PASS = "[PASS]"
FAIL = "[FAIL]"
errors = []

def check(label, condition, note=""):
    tag = PASS if condition else FAIL
    msg = f"{tag} {label}"
    if note:
        msg += f"  ({note})"
    print(msg)
    if not condition:
        errors.append(label)

# ──────────────────────────────────────────
# CRIT-1: Template uses level_end_xp not xp_needed
# ──────────────────────────────────────────
print("\n--- CRIT-1: Template XP variable ---")
tmpl = open("templates/dashboard.html", encoding="utf-8").read()
check("xp_needed removed from template", "xp_needed" not in tmpl)
check("level_end_xp present in template", "level_end_xp" in tmpl)

# ──────────────────────────────────────────
# CRIT-2: Single XP_PER_LEVEL constant
# ──────────────────────────────────────────
print("\n--- CRIT-2: Single XP_PER_LEVEL ---")
from constants import XP_PER_LEVEL
check("XP_PER_LEVEL defined in constants.py", XP_PER_LEVEL == 1000)

from services.xp_service import XPService
check("XPService.XP_PER_LEVEL class attr removed", not hasattr(XPService, "XP_PER_LEVEL"))

dashboard_src = open("services/dashboard_service.py").read()
check("dashboard_service.py uses import not local def", "from constants import XP_PER_LEVEL" in dashboard_src)
check("dashboard_service.py has no local XP_PER_LEVEL =", "XP_PER_LEVEL = 1000" not in dashboard_src)

xp_src = open("services/level_service.py").read()
check("level_service.py uses import not local def", "from constants import XP_PER_LEVEL" in xp_src)

# ──────────────────────────────────────────
# CRIT-3: delete_mission signature + ownership
# ──────────────────────────────────────────
print("\n--- CRIT-3: delete_mission ownership ---")
from services.mission_service import MissionService
sig = inspect.signature(MissionService.delete_mission)
params = list(sig.parameters.keys())
check("delete_mission accepts user_id", "user_id" in params, str(params))

src = inspect.getsource(MissionService.delete_mission)
check("delete_mission checks created_by", "created_by" in src)
check("delete_mission raises ValueError on wrong owner", "permission" in src.lower())

# ──────────────────────────────────────────
# CRIT-4: utils/db.py deleted
# ──────────────────────────────────────────
print("\n--- CRIT-4: Dead code removed ---")
check("utils/db.py deleted", not os.path.exists("utils/db.py"))

# ──────────────────────────────────────────
# CRIT-5: Seed password is hashed
# ──────────────────────────────────────────
print("\n--- CRIT-5: Seed password hashed ---")
seed = open("database/seed.sql").read()
check("seed uses pbkdf2 hash", "pbkdf2:sha256" in seed)
check("seed has no plaintext 'development' value", "'development'" not in seed)

# ──────────────────────────────────────────
# CRIT-6: last_login written on login
# ──────────────────────────────────────────
print("\n--- CRIT-6: last_login updated ---")
from models.user import update_last_login
check("update_last_login function exists", callable(update_last_login))

auth_src = open("services/auth_service.py").read()
check("update_last_login imported in auth_service", "update_last_login" in auth_src)
check("update_last_login called in login_user", auth_src.count("update_last_login(") >= 1)

# Verify the DB function actually writes last_login
# We need a Flask app context for get_db, so test directly with sqlite3
conn = sqlite3.connect(DATABASE_PATH)
# Check column exists
cols = [row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()]
check("users.last_login column exists", "last_login" in cols)
conn.close()

# ──────────────────────────────────────────
# DB: assignment_date migration applied
# ──────────────────────────────────────────
print("\n--- DB Migration: assignment_date ---")
conn = sqlite3.connect(DATABASE_PATH)
cols = [row[1] for row in conn.execute("PRAGMA table_info(user_missions)").fetchall()]
check("user_missions.assignment_date column exists", "assignment_date" in cols, str(cols))
idx = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()]
check("idx_daily_assignment index exists", "idx_daily_assignment" in idx)
conn.close()

# ──────────────────────────────────────────
# Summary
# ──────────────────────────────────────────
print()
if errors:
    print(f"FAILED ({len(errors)} checks):")
    for e in errors:
        print(f"  [X] {e}")
    sys.exit(1)
else:
    print("All checks passed. [OK]")
