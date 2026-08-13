"""
LifeXP Configuration
Version: 1.0
"""

from pathlib import Path
import os

# --------------------------------------------------
# Project Information
# --------------------------------------------------

PROJECT_NAME = "LifeXP"
PROJECT_VERSION = "0.2.0"
PROJECT_AUTHOR = "Md Anis Akhtar"

# --------------------------------------------------
# Base Directory
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

# --------------------------------------------------
# Database
# --------------------------------------------------

DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "database.db"

# --------------------------------------------------
# Flask
# --------------------------------------------------

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "CHANGE_THIS_IN_PRODUCTION"
)

DEBUG = True

# --------------------------------------------------
# Uploads
# --------------------------------------------------

UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"

MAX_CONTENT_LENGTH = 5 * 1024 * 1024

# --------------------------------------------------
# Application Settings
# --------------------------------------------------

DEFAULT_THEME = "dark"

DEFAULT_LANGUAGE = "en"

# --------------------------------------------------
# Firebase (Phase 1 foundation only)
# --------------------------------------------------

# Firebase remains optional while LifeXP continues to use SQLite.  Keep the
# service-account key outside source control and provide its path via the
# environment when running locally.
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "")
FIREBASE_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

# --------------------------------------------------
# Feature Flags
# --------------------------------------------------

FIRESTORE_NOTIFICATIONS_ENABLED = os.environ.get("FIRESTORE_NOTIFICATIONS_ENABLED", "false").lower() == "true"
FIRESTORE_USER_STATS_ENABLED = os.environ.get("FIRESTORE_USER_STATS_ENABLED", "false").lower() == "true"
