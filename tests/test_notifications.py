import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from database.db import get_db
import services.notification_service as notif_module
from services.notification_service import NotificationService

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DATABASE": "database/database.db"
    })
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

# --- SQLite Mode Tests (Default Fallback) ---

@patch("services.notification_service.FIRESTORE_NOTIFICATIONS_ENABLED", False)
def test_sqlite_create_and_read(app, caplog):
    """Verify SQLite fallback logic when Firestore is disabled."""
    with app.app_context():
        # Clear existing
        NotificationService.mark_as_read(1)
        
        success = NotificationService.create(user_id=1, title="SQLite Test", message="Test Msg")
        if not success:
            print("CAPLOG:", caplog.text)
        assert success is True
        
        unread = NotificationService.get_unread_for_user(1)
        assert len(unread) > 0
        assert unread[0]["title"] == "SQLite Test"
        
        # Cleanup
        NotificationService.mark_as_read(1)
        assert len(NotificationService.get_unread_for_user(1)) == 0


@patch("services.notification_service.FIRESTORE_NOTIFICATIONS_ENABLED", False)
def test_sqlite_daily_reminder_duplicate_prevention(app):
    """Verify SQLite reminder duplicate prevention."""
    with app.app_context():
        # Mocking get_db to return a mock DB that pretends there's an incomplete daily
        with patch("services.notification_service.get_db") as mock_get_db:
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            
            mock_db.execute.return_value.fetchone.side_effect = [
                {"id": 1}, # Pretend there are incomplete dailies
                None       # Pretend no reminder exists today
            ]
            
            with patch.object(NotificationService, "create") as mock_create:
                NotificationService.create_mission_reminder_if_needed(1)
                mock_create.assert_called_once()


# --- Firestore Mode Tests ---

@patch("services.notification_service.FIRESTORE_NOTIFICATIONS_ENABLED", True)
@patch("services.notification_service.NotificationService._get_fs")
def test_firestore_create_and_read(mock_get_fs, app):
    """Verify Firestore adapter routes reads and writes to Firestore correctly."""
    
    # Mock Firestore Client and Collections
    mock_fs = MagicMock()
    mock_get_fs.return_value = mock_fs
    
    mock_doc_ref = MagicMock()
    mock_fs.collection().document().collection().document.return_value = mock_doc_ref
    
    with app.app_context():
        # Test Create
        success = NotificationService.create(user_id=1, title="FS Test", message="Msg")
        assert success is True
        mock_doc_ref.set.assert_called_once()
        
        # Test Read
        mock_query = MagicMock()
        mock_fs.collection().document().collection().where().order_by().stream.return_value = [
            MagicMock(id="notif_1", to_dict=lambda: {"title": "FS Test", "created_at": None})
        ]
        
        unread = NotificationService.get_unread_for_user(1)
        assert len(unread) == 1
        assert unread[0]["id"] == "notif_1"
        assert unread[0]["title"] == "FS Test"


@patch("services.notification_service.FIRESTORE_NOTIFICATIONS_ENABLED", True)
@patch("services.notification_service.NotificationService._get_fs")
def test_firestore_mark_read(mock_get_fs, app):
    """Verify Firestore batch mark-as-read logic."""
    mock_fs = MagicMock()
    mock_get_fs.return_value = mock_fs
    
    # Mock a stream returning 2 documents
    mock_fs.collection().document().collection().where().stream.return_value = [
        MagicMock(reference="ref1"),
        MagicMock(reference="ref2")
    ]
    
    mock_batch = MagicMock()
    mock_fs.batch.return_value = mock_batch
    
    with app.app_context():
        success = NotificationService.mark_as_read(1) # Mark all
        assert success is True
        
        # Verify batch was used to update both
        assert mock_batch.update.call_count == 2
        mock_batch.commit.assert_called_once()


@patch("services.notification_service.FIRESTORE_NOTIFICATIONS_ENABLED", True)
@patch("services.notification_service.NotificationService._get_fs")
def test_firestore_fallback_on_client_error(mock_get_fs, app, caplog):
    """Verify safe fallback if Firestore client fails to initialize."""
    mock_get_fs.return_value = None # Simulates FirebaseConfigurationError caught in _get_fs
    
    with app.app_context():
        # Create should fall back to SQLite if fs is None
        with patch("services.notification_service.get_db") as mock_get_db:
            NotificationService.create(user_id=1, title="Test", message="Test")
            mock_get_db.assert_called_once() # Verify SQLite was called as fallback


# --- API Tests ---

def test_api_get_notifications_unauthorized(client):
    res = client.get("/api/notifications")
    assert res.status_code == 401

def test_api_mark_read_unauthorized(client):
    res = client.put("/api/notifications/read", json={"notification_id": 1})
    assert res.status_code == 401
