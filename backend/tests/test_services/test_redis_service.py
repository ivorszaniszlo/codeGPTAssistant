import pytest
from unittest.mock import MagicMock
from app.services.redis_service import RedisService

@pytest.fixture
def mock_redis_service(mocker):
    """
    Mock RedisService for testing.
    """
    mock_redis_client = mocker.Mock()
    redis_service = RedisService(host="localhost", port=6379, db=0)
    redis_service.client = mock_redis_client
    return redis_service

def test_set_key(mock_redis_service):
    """
    Test the set method in RedisService.
    """
    mock_redis_service.client.set.return_value = True
    result = mock_redis_service.set("test_key", "test_value")
    assert result is True
    mock_redis_service.client.set.assert_called_once_with("test_key", "test_value", ex=None)

def test_get_key(mock_redis_service):
    """
    Test the get method in RedisService.
    """
    mock_redis_service.client.get.return_value = "test_value"
    result = mock_redis_service.get("test_key")
    assert result == "test_value"
    mock_redis_service.client.get.assert_called_once_with("test_key")

def test_delete_key(mock_redis_service):
    """
    Test the delete method in RedisService.
    """
    mock_redis_service.client.delete.return_value = 1
    result = mock_redis_service.delete("test_key")
    assert result is True
    mock_redis_service.client.delete.assert_called_once_with("test_key")
