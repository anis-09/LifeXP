import pytest
from app import create_app
from database.db import get_db, initialize_database
from services.notification_service import NotificationService

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DATABASE": "database/database.db"
    })
    
    with app.app_context():
        # Using existing DB for tests, let's insert a test user or just assume user 1 exists
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_notification_service_create(app):
    with app.app_context():
        success = NotificationService.create(user_id=1, title="Test", message="Test Msg")
        assert success is True
        
        # Verify it was added
        unread = NotificationService.get_unread_for_user(1)
        assert len(unread) > 0
        assert unread[0]["title"] == "Test"

def test_notification_service_mark_read(app):
    with app.app_context():
        # Mark all as read
        NotificationService.mark_as_read(1)
        unread = NotificationService.get_unread_for_user(1)
        # Should be empty or at least not have the test message if it was the only one
        assert len(unread) == 0

def test_api_get_notifications_unauthorized(client):
    res = client.get("/api/notifications")
    assert res.status_code == 401

def test_api_mark_read_unauthorized(client):
    res = client.put("/api/notifications/read", json={"notification_id": 1})
    assert res.status_code == 401
