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
