import pytest
from unittest.mock import patch, MagicMock
from pymongo.errors import ConnectionFailure, OperationFailure  # Itt van a hiányzó import
from app.utils.database import DatabaseService

@pytest.fixture
def mock_mongo_client():
    """
    Fixture to provide a mocked MongoClient.
    """
    mock_client = MagicMock()
    mock_client.admin.command.return_value = {"ok": 1}  # Simulate successful ping response
    return mock_client

def test_initialize_client_success(mock_mongo_client):
    """
    Test successful initialization of MongoDB client.
    """
    # Reset the DatabaseService singleton instance
    DatabaseService._instance = None

    with patch("app.utils.database.MongoClient", return_value=mock_mongo_client) as patched_client:
        db_service = DatabaseService(uri="mongodb://mocked_uri")
        client = db_service.get_client()
        patched_client.assert_called_once_with("mongodb://mocked_uri")
        assert client == mock_mongo_client

def test_initialize_client_connection_failure():
    """
    Test initialization failure due to a ConnectionFailure.
    """
    with patch("app.utils.database.MongoClient", side_effect=ConnectionFailure("Connection failed.")):
        with pytest.raises(RuntimeError, match="MongoDB connection failed."):
            DatabaseService(uri="mongodb://invalid_uri")._initialize_client()

def test_initialize_client_operation_failure():
    """
    Test initialization failure due to an OperationFailure.
    """
    with patch("app.utils.database.MongoClient") as mock_client:
        instance = mock_client.return_value
        instance.admin.command.side_effect = OperationFailure("Operation failed.")
        with pytest.raises(RuntimeError, match="MongoDB operation failed."):
            DatabaseService(uri="mongodb://mocked_uri")._initialize_client()

def test_get_client_when_uninitialized(mock_mongo_client):
    """
    Test that the client reinitializes if uninitialized.
    """
    with patch("app.utils.database.MongoClient", return_value=mock_mongo_client):
        db_service = DatabaseService(uri="mongodb://mocked_uri")
        db_service.client = None  # Simulate uninitialized client
        client = db_service.get_client()
        assert client == mock_mongo_client
        mock_mongo_client.admin.command.assert_called_once_with("ping")

def test_singleton_behavior(mock_mongo_client):
    """
    Test that DatabaseService follows the Singleton pattern.
    """
    with patch("app.utils.database.MongoClient", return_value=mock_mongo_client):
        db_service_1 = DatabaseService(uri="mongodb://mocked_uri")
        db_service_2 = DatabaseService(uri="mongodb://mocked_uri")
        assert db_service_1 is db_service_2

def test_get_database_success(mock_mongo_client):
    """
    Test that get_database returns a working MongoClient.
    """
    with patch("app.utils.database.MongoClient", return_value=mock_mongo_client):
        from app.utils.database import get_database
        client = get_database()
        assert client is not None  # Ensure a client is returned
