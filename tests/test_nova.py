"""
tests/test_nova.py
Tests for the Nova AI Coach Service.
"""

from services.nova_service import NovaService


def test_nova_fallback_without_stats():
    """Test Nova returns a fallback message when no stats are provided."""
    result = NovaService.generate_daily_coaching(1, None, [])
    assert result["type"] == "motivation"
    assert result["icon"] == "✨"
    assert "cta_text" in result

def test_nova_all_missions_complete():
    """Test Nova returns a success message when all daily missions are completed."""
    stats = {"current_streak": 1, "current_level": 1, "current_xp": 10}
    today_missions = [
        {"id": 1, "status": "Completed"},
        {"id": 2, "status": "Completed"}
    ]
    result = NovaService.generate_daily_coaching(1, stats, today_missions)
    assert result["type"] == "success"
    assert result["icon"] == "🌟"
    assert "cta_text" in result

def test_nova_level_up_imminent():
    """Test Nova encourages the user when close to leveling up."""
    # Assuming XP_PER_LEVEL is 1000
    # Current level 1 ends at 1000. 850 means 150 remaining, which is < 20% (200).
    stats = {"current_streak": 1, "current_level": 1, "current_xp": 850}
    today_missions = [
        {"id": 1, "status": "Assigned"}
    ]
    result = NovaService.generate_daily_coaching(1, stats, today_missions)
    assert result["type"] == "goal"
    assert result["icon"] == "⚡"
    assert "level up" in result["message"].lower() or "xp away" in result["message"].lower()

def test_nova_streak_encouragement(monkeypatch):
    """Test Nova encourages streak maintenance if streak >= 3 and missions remain."""
    stats = {"current_streak": 5, "current_level": 1, "current_xp": 500}
    today_missions = [
        {"id": 1, "status": "Assigned"}
    ]
    
    # Mock datetime to evening
    import datetime
    class MockDatetime:
        @classmethod
        def now(cls):
            return datetime.datetime(2023, 1, 1, 18, 0, 0)
    
    monkeypatch.setattr("services.nova_service.datetime", MockDatetime)
    
    result = NovaService.generate_daily_coaching(1, stats, today_missions)
    assert result["type"] == "streak"
    assert result["icon"] == "🔥"
    assert "streak" in result["message"].lower()
