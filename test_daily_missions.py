"""
test_daily_missions.py
----------------------
Programmatic verification of the daily mission integration.
"""

import sys, os, sqlite3, urllib.request, urllib.parse, http.cookiejar

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DATABASE_PATH

BASE = "http://127.0.0.1:5000"
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
opener.addheaders = [("User-Agent", "TestRunner/1.0")]

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

print("=== Login ===")
data = urllib.parse.urlencode(
    {"email": "developer@lifexp.local", "password": "dev123"}
).encode()
resp = opener.open(BASE + "/login", data)
print("Logged in")

print("\n=== Test Dashboard Route (Assignment Trigger) ===")
dash_resp = opener.open(BASE + "/dashboard")
dash_html = dash_resp.read().decode("utf-8", errors="replace")

check("Dashboard renders without error", dash_resp.getcode() == 200)
check("Today's Missions section is present", "Today&#39;s Missions" in dash_html or "Today's Missions" in dash_html)
check("Mission title 'Read 10 pages' is present", "Read 10 pages" in dash_html)

print("\n=== Test DB Assignments ===")
conn = sqlite3.connect(DATABASE_PATH)
assignments = conn.execute("SELECT mission_id FROM user_missions WHERE assignment_date = DATE('now')").fetchall()
conn.close()

check("User mission assigned in DB", len(assignments) >= 1)
mission_ids = [a[0] for a in assignments]
print(f"Assigned mission IDs for today: {mission_ids}")

print("\n=== Test Idempotency (Reload Dashboard) ===")
dash_resp2 = opener.open(BASE + "/dashboard")
check("Dashboard reloads without error", dash_resp2.getcode() == 200)

conn = sqlite3.connect(DATABASE_PATH)
assignments2 = conn.execute("SELECT mission_id FROM user_missions WHERE assignment_date = DATE('now')").fetchall()
conn.close()
check("No duplicate assignments created", len(assignments2) == len(assignments))

if errors:
    print(f"\nFAILED ({len(errors)} checks):")
    for e in errors:
        print(f"  ✗ {e}")
    sys.exit(1)
else:
    print("\nAll checks passed. ✓")
