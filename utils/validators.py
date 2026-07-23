"""
utils/validators.py
-------------------
Input validation utilities for user registration and login.
All functions return (is_valid: bool, error_message: str).
"""

import re


def validate_full_name(name: str):
    """Ensure full name is present and reasonable."""
    name = name.strip()
    if not name:
        return False, "Full name is required."
    if len(name) < 2:
        return False, "Full name must be at least 2 characters."
    if len(name) > 100:
        return False, "Full name must be under 100 characters."
    return True, ""


def validate_email(email: str):
    """Validate email format using RFC 5322-like regex."""
    email = email.strip().lower()
    if not email:
        return False, "Email address is required."
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Please enter a valid email address."
    return True, ""


def validate_password(password: str):
    """
    Strong password rules:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if not password:
        return False, "Password is required."
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-]', password):
        return False, "Password must contain at least one special character."
    return True, ""


def validate_confirm_password(password: str, confirm: str):
    """Ensure password and confirm password match."""
    if not confirm:
        return False, "Please confirm your password."
    if password != confirm:
        return False, "Passwords do not match."
    return True, ""
