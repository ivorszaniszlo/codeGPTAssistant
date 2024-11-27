import pytest
from unittest.mock import MagicMock
from app.utils.redis import redis_set_key, redis_get_key, redis_delete_key

@pytest.fixture
def mock_redis_client():
    """
    Mock Redis client for testing utility functions.
    """
    return MagicMock()

def test_redis_set_key(mock_redis_client):
    """
    Test the redis_set_key utility function.
    """
    mock_redis_client.set.return_value = True
    result = redis_set_key(mock_redis_client, "test_key", "test_value")
    assert result is True
    mock_redis_client.set.assert_called_once_with("test_key", "test_value")

def test_redis_get_key(mock_redis_client):
    """
    Test the redis_get_key utility function.
    """
    mock_redis_client.get.return_value = "test_value"
    result = redis_get_key(mock_redis_client, "test_key")
    assert result == "test_value"
    mock_redis_client.get.assert_called_once_with("test_key")

def test_redis_delete_key(mock_redis_client):
    """
    Test the redis_delete_key utility function.
    """
    mock_redis_client.delete.return_value = 1
    result = redis_delete_key(mock_redis_client, "test_key")
    assert result is True
    mock_redis_client.delete.assert_called_once_with("test_key")
