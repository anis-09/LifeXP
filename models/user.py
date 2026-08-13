"""
models/user.py
--------------
User model: all database operations related to the users table.
Uses parameterised queries to prevent SQL injection.
"""

from database.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash


def create_user(full_name: str, email: str, password: str) -> int:
    """
    Insert a new user into the users table.
    Password is hashed with werkzeug's pbkdf2 method.
    Returns the new user's row id.
    """
    db = get_db()
    hashed = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    cursor = db.execute(
        """
        INSERT INTO users (full_name, email, password_hash)
        VALUES (?, ?, ?)
        """,
        (full_name.strip(), email.strip().lower(), hashed)
    )
    db.commit()
    return cursor.lastrowid


def get_user_by_email(email: str):
    """Return a user row dict by email, or None if not found."""
    db = get_db()
    row = db.execute(
        "SELECT * FROM users WHERE email = ?",
        (email.strip().lower(),)
    ).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: int):
    """Return a user row dict by primary key, or None if not found."""
    db = get_db()
    row = db.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    return dict(row) if row else None


def email_exists(email: str) -> bool:
    """Return True if the email is already registered."""
    return get_user_by_email(email) is not None


def verify_password(stored_hash: str, password: str) -> bool:
    """Compare a plain-text password against the stored hash."""
    return check_password_hash(stored_hash, password)


def update_last_login(user_id: int) -> None:
    """Set users.last_login to the current timestamp for the given user."""
    db = get_db()
    db.execute(
        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
        (user_id,)
    )
    db.commit()


def update_profile(user_id: int, full_name: str, avatar: str) -> None:
    """Update the user's full name and avatar."""
    db = get_db()
    db.execute(
        """
        UPDATE users 
        SET full_name = ?, avatar = ? 
        WHERE id = ?
        """,
        (full_name.strip(), avatar.strip(), user_id)
    )
    db.commit()
