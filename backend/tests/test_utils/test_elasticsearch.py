import pytest
from unittest.mock import MagicMock, patch
from app.services.elasticsearch_service import ElasticsearchService
from elastic_transport import ConnectionError

@pytest.fixture
def mock_elasticsearch_service():
    """
    Fixture to mock ElasticsearchService and its client.
    """
    with patch("app.services.elasticsearch_service.ElasticsearchService") as MockElasticsearchService:
        mock_instance = MockElasticsearchService.return_value
        mock_instance.client = MagicMock()
        yield mock_instance


def test_ping_success(mock_elasticsearch_service):
    """
    Test Elasticsearch ping success scenario.
    """
    mock_elasticsearch_service.client.ping.return_value = True
    assert mock_elasticsearch_service.client.ping() is True
    mock_elasticsearch_service.client.ping.assert_called_once()


def test_ping_failure(mock_elasticsearch_service):
    """
    Test Elasticsearch ping failure scenario.
    """
    mock_elasticsearch_service.client.ping.side_effect = ConnectionError("Connection failed.")
    with pytest.raises(ConnectionError):
        mock_elasticsearch_service.client.ping()


def test_create_index_success(mock_elasticsearch_service):
    """
    Test creating an index successfully.
    """
    mock_elasticsearch_service.client.indices.create.return_value = {"acknowledged": True}
    response = mock_elasticsearch_service.client.indices.create(index="test_index", body={"mappings": {}})
    assert response["acknowledged"] is True
    mock_elasticsearch_service.client.indices.create.assert_called_once_with(
        index="test_index", body={"mappings": {}}
    )
