"""
services/auth_service.py
------------------------
Business logic for authentication:
- register_user()  — validate + create account + create user_stats row
- login_user()     — validate credentials + start session
"""

from models.user import create_user, get_user_by_email, email_exists, verify_password
from models.user_stats import UserStatsModel
from utils.validators import (
    validate_full_name,
    validate_email,
    validate_password,
    validate_confirm_password,
)


def register_user(full_name: str, email: str, password: str, confirm: str):
    """
    Run all validation checks then persist the new user.
    Also creates a default user_stats row for the new user.
    Returns (success: bool, message: str, user_id: int | None).
    """
    # --- Validate inputs ---
    ok, msg = validate_full_name(full_name)
    if not ok:
        return False, msg, None

    ok, msg = validate_email(email)
    if not ok:
        return False, msg, None

    ok, msg = validate_password(password)
    if not ok:
        return False, msg, None

    ok, msg = validate_confirm_password(password, confirm)
    if not ok:
        return False, msg, None

    # --- Duplicate email check ---
    if email_exists(email):
        return False, "An account with this email already exists.", None

    # --- Create user ---
    user_id = create_user(full_name, email, password)

    # --- Create default stats row for new user ---
    UserStatsModel.create(user_id)

    return True, "Account created successfully!", user_id


def login_user(email: str, password: str):
    """
    Validate credentials.
    Returns (success: bool, message: str, user: dict | None).
    """
    if not email or not password:
        return False, "Email and password are required.", None

    user = get_user_by_email(email)
    if not user:
        return False, "Invalid email or password.", None

    if not verify_password(user['password_hash'], password):
        return False, "Invalid email or password.", None

    return True, "Login successful.", user
