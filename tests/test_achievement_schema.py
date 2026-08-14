"""
tests/test_achievement_schema.py
---------------------------------
Regression tests for the user_achievements schema fix (Issue #1).

Ensures:
  - user_achievements table uses 'unlocked_at' (not 'earned_at')
  - UserAchievementModel.get_unlocked_for_user() executes without OperationalError
  - UserAchievementModel.latest_unlocked() executes without OperationalError
  - GET /dashboard does not return HTTP 500 due to this schema mismatch

These tests guard against regression of the migration-induced column name mismatch
where the live DB had 'earned_at' but all application code expected 'unlocked_at'.
"""

import pytest
import sqlite3
from unittest.mock import patch
from app import create_app
from database.db import get_db
from models.user_achievement import UserAchievementModel


@pytest.fixture
def app():
    application = create_app()
    application.config.update({
        "TESTING": True,
        "DATABASE": "database/database.db",
        "FIRESTORE_DAILY_REWARDS_ENABLED": False,
    })
    with application.app_context():
        yield application


@pytest.fixture
def client(app):
    return app.test_client()


# ---------------------------------------------------------------------------
# Schema structure tests
# ---------------------------------------------------------------------------

def test_user_achievements_has_unlocked_at_column(app):
    """Verify live DB uses 'unlocked_at', not 'earned_at'."""
    with app.app_context():
        db = get_db()
        cols = db.execute("PRAGMA table_info(user_achievements)").fetchall()
        col_names = [c[1] for c in cols]
        assert "unlocked_at" in col_names, (
            "user_achievements is missing 'unlocked_at' column — "
            "run migrations/005_fix_achievements_schema.sql"
        )
        assert "earned_at" not in col_names, (
            "user_achievements still has stale 'earned_at' column"
        )


def test_achievements_has_canonical_sprint42_columns(app):
    """Verify achievements table has Sprint 4.2 canonical columns."""
    with app.app_context():
        db = get_db()
        cols = db.execute("PRAGMA table_info(achievements)").fetchall()
        col_names = [c[1] for c in cols]
        for required in ("name", "category", "condition_key", "target_value", "badge_tier"):
            assert required in col_names, (
                f"achievements table missing column '{required}' — "
                f"run migrations/005_fix_achievements_schema.sql"
            )


# ---------------------------------------------------------------------------
# Model query tests (no OperationalError)
# ---------------------------------------------------------------------------

def test_get_unlocked_for_user_no_error(app):
    """get_unlocked_for_user() must not raise OperationalError for 'unlocked_at'."""
    with app.app_context():
        result = UserAchievementModel.get_unlocked_for_user(1)
        assert isinstance(result, list)  # empty list is fine, error is not


def test_latest_unlocked_no_error(app):
    """latest_unlocked() must not raise OperationalError for 'unlocked_at'."""
    with app.app_context():
        result = UserAchievementModel.latest_unlocked(1)
        assert isinstance(result, list)


def test_count_unlocked_no_error(app):
    """count_unlocked() must not raise any schema error."""
    with app.app_context():
        result = UserAchievementModel.count_unlocked(1)
        assert isinstance(result, int)
        assert result >= 0


def test_get_locked_for_user_no_error(app):
    """get_locked_for_user() must not raise any schema error."""
    with app.app_context():
        result = UserAchievementModel.get_locked_for_user(1)
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# Dashboard route test — regression for HTTP 500
# ---------------------------------------------------------------------------

def test_dashboard_does_not_500_from_achievement_schema(client):
    """
    GET /dashboard must NOT return 500 due to 'ua.unlocked_at' column error.

    The dashboard requires an authenticated session. We inject one directly
    and check that the response is NOT 500 (could be 302 redirect if session
    injection fails, or 200 if fully authenticated — both are acceptable;
    only 500 is the failure condition we're guarding against).
    """
    with client.session_transaction() as sess:
        sess["user_id"] = 1  # developer@lifexp.local

    response = client.get("/dashboard")
    # 500 means the schema bug is back. 200 = success. 302 = redirect (e.g. auth issue).
    assert response.status_code != 500, (
        f"GET /dashboard returned HTTP 500 — likely schema mismatch in "
        f"user_achievements table (check 'unlocked_at' vs 'earned_at').\n"
        f"Response body snippet: {response.data[:500]}"
    )
