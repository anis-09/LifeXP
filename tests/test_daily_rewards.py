import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from firebase_admin import firestore
from services.daily_reward_service import DailyRewardService
import datetime as dt

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DATABASE": "database/database.db",
        "FIRESTORE_DAILY_REWARDS_ENABLED": True
    })
    with app.app_context():
        yield app

@patch('services.daily_reward_service.get_firestore_client')
@patch('services.daily_reward_service.RewardService')
@patch('services.daily_reward_service.NotificationService')
def test_firestore_claim_success(mock_ns, mock_rs, mock_get_fs, app):
    """Test that a Firestore claim gives correct rewards and increments total_daily_claims."""
    mock_fs = MagicMock()
    mock_get_fs.return_value = mock_fs
    
    # Mock user_stats document reference
    stats_doc_ref = MagicMock()
    saved_data = {}
    
    def mock_set(data, merge=False):
        for k, v in data.items():
            if isinstance(v, firestore.Increment):
                saved_data[k] = saved_data.get(k, 0) + v.value
            else:
                saved_data[k] = v
                
    stats_doc_ref.set.side_effect = mock_set
    
    def mock_collection(name):
        coll_mock = MagicMock()
        if name == 'user_stats':
            coll_mock.document.return_value = stats_doc_ref
        return coll_mock
        
    mock_fs.collection.side_effect = mock_collection
    
    with patch.object(DailyRewardService, '_get_next_day_number', return_value=1), \
         patch.object(DailyRewardService, '_get_today_claim', return_value=None):
        
        result = DailyRewardService.claim(999)
        
        # Verify first claim gives 20 coins
        assert result["day_number"] == 1
        assert result["coins_granted"] == 20
        assert result["xp_granted"] == 0
        
        # Verify total_daily_claims increments correctly
        assert saved_data["total_daily_claims"] == 1
        mock_rs.grant_coins.assert_called_with(user_id=999, amount=20, source="DailyReward", reference_id=1)

@patch('services.daily_reward_service.get_firestore_client')
def test_firestore_same_day_claim_rejected(mock_get_fs, app):
    """Test that a same-day second claim is rejected."""
    with patch.object(DailyRewardService, '_get_today_claim', return_value={"day_number": 1}):
        with pytest.raises(ValueError, match="already claimed today"):
            DailyRewardService.claim(999)

@patch('services.daily_reward_service.get_firestore_client')
def test_firestore_recent_claims_query(mock_get_fs, app):
    """Test that recent claims query works."""
    mock_fs = MagicMock()
    mock_get_fs.return_value = mock_fs
    
    # Mock firestore stream for recent claims
    mock_doc1 = MagicMock()
    mock_doc1.to_dict.return_value = {
        "day_number": 1,
        "reward_type": "coins",
        "reward_value": 20,
        "claimed_at": dt.datetime.now()
    }
    
    mock_query = MagicMock()
    mock_query.stream.return_value = [mock_doc1]
    
    mock_fs.collection().document().collection().order_by().limit.return_value = mock_query
    
    claims = DailyRewardService.get_recent_claims(999, limit=1)
    
    assert len(claims) == 1
    assert claims[0]["day_number"] == 1
    assert claims[0]["reward_type"] == "coins"
    assert claims[0]["reward_value"] == 20
    assert "label" in claims[0]
