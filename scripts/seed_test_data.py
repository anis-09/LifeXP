"""
scripts/seed_test_data.py
-------------------------
Create idempotent test data for local development.
"""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app import app
from models.user import get_user_by_email
from models.user_stats import UserStatsModel
from services.auth_service import register_user


TEST_USER_NAME = "Test User"
TEST_USER_EMAIL = "test@lifexp.local"
TEST_USER_PASSWORD = "TestUser123!"


def seed_test_user():
    """
    Create the default test user and its stats when they are missing.
    """

    with app.app_context():
        user = get_user_by_email(TEST_USER_EMAIL)

        if user is None:
            success, message, user_id = register_user(
                full_name=TEST_USER_NAME,
                email=TEST_USER_EMAIL,
                password=TEST_USER_PASSWORD,
                confirm=TEST_USER_PASSWORD
            )

            if not success:
                raise RuntimeError(message)

            print("Created test user.")
        else:
            user_id = user["id"]
            print("Skipped test user; it already exists.")

        stats = UserStatsModel.get(user_id)

        if stats is None:
            UserStatsModel.create(user_id)
            print("Created user stats.")
        else:
            print("Skipped user stats; they already exist.")


if __name__ == "__main__":
    seed_test_user()
