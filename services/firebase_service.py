"""Optional Firebase Admin integration for LifeXP Phase 1.

This module deliberately has no SQLite knowledge and makes no network request
until a caller asks for a Firestore client.  It is therefore safe to include
during the staged migration while the existing application remains SQLite-backed.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import firebase_admin
from firebase_admin import credentials, firestore

from config import BASE_DIR, FIREBASE_CREDENTIALS_PATH, FIREBASE_PROJECT_ID


class FirebaseConfigurationError(RuntimeError):
    """Raised when the optional local Firebase configuration is incomplete."""


def _credential_path() -> Path:
    """Return the configured service-account file without reading its contents."""
    configured_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", FIREBASE_CREDENTIALS_PATH)
    if not configured_path:
        configured_path = str(BASE_DIR / "firebase-credentials.json")

    path = Path(configured_path).expanduser()
    if not path.is_file():
        raise FirebaseConfigurationError(
            "Firebase is not configured. Set GOOGLE_APPLICATION_CREDENTIALS to a "
            "local service-account JSON file."
        )
    return path


def _project_id() -> str:
    project_id = os.getenv("FIREBASE_PROJECT_ID", FIREBASE_PROJECT_ID).strip()
    if not project_id:
        raise FirebaseConfigurationError(
            "Firebase is not configured. Set FIREBASE_PROJECT_ID."
        )
    return project_id


def get_firebase_app() -> firebase_admin.App:
    """Initialise and return the default Admin SDK app exactly once."""
    try:
        return firebase_admin.get_app()
    except ValueError:
        credential_path = _credential_path()
        service_account = credentials.Certificate(str(credential_path))
        project_id = _project_id()
        if service_account.project_id != project_id:
            raise FirebaseConfigurationError(
                "FIREBASE_PROJECT_ID does not match the local service-account file."
            )
        return firebase_admin.initialize_app(
            service_account,
            {"projectId": project_id},
        )


def get_firestore_client() -> Any:
    """Return an authenticated Firestore Admin client, initializing lazily."""
    return firestore.client(app=get_firebase_app())


def get_firebase_status() -> dict[str, Any]:
    """Return safe diagnostic information; never return credential contents."""
    try:
        app = get_firebase_app()
        return {
            "configured": True,
            "project_id": app.project_id,
            "message": "Firebase Admin SDK initialized.",
        }
    except FirebaseConfigurationError as exc:
        return {"configured": False, "message": str(exc)}

def format_firestore_timestamp(dt) -> str:
    """Format a Firestore datetime object into SQLite-compatible string."""
    if not dt:
        return ""
    # Convert to local time or leave as UTC? SQLite usually stores UTC or localtime
    # Let's just do YYYY-MM-DD HH:MM:SS format
    return dt.strftime("%Y-%m-%d %H:%M:%S")
