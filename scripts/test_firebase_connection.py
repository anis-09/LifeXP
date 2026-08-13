"""Verify Phase 1 Firebase Admin + Firestore access without writing data."""

import sys
from pathlib import Path

# Support direct execution from the project root, as documented below.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.firebase_service import get_firestore_client, get_firebase_status


def main() -> int:
    status = get_firebase_status()
    if not status["configured"]:
        print(f"Firebase connection skipped: {status['message']}")
        return 1

    try:
        # This is a read-only permission/connectivity check. It does not create,
        # update, or delete any LifeXP or Firebase document.
        next(get_firestore_client().collections(), None)
    except Exception as exc:
        print(f"Firebase Firestore connection failed: {type(exc).__name__}")
        return 1

    print(f"Firebase Firestore connection succeeded for project: {status['project_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
