import pytest
from unittest.mock import MagicMock, patch
from app.services.elasticsearch_service import ElasticsearchService
from app.services.openai_service import OpenAIService
from dotenv import load_dotenv

# Load test-specific environment variables
load_dotenv(".env.test")

@pytest.fixture(autouse=True)
def mock_openai_service(monkeypatch):
    """
    Mock the OpenAIService for all tests.
    """
    mock_service = MagicMock(spec=OpenAIService)
    mock_service.generate_response.return_value = "Mocked response"
    monkeypatch.setattr("app.services.openai_service.OpenAIService", mock_service)
    return mock_service

@pytest.fixture
def mock_elasticsearch():
    """
    Mock the ElasticsearchService for tests.
    """
    with patch("app.services.elasticsearch_service.ElasticsearchService") as MockElasticsearchService:
        mock_instance = MockElasticsearchService.return_value
        mock_instance.client = MagicMock()
        mock_instance.client.ping.return_value = True
        mock_instance.client.indices.exists.return_value = False
        mock_instance.client.indices.create.return_value = {"acknowledged": True}
        yield mock_instance
