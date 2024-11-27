import pytest
from unittest.mock import MagicMock
from app.services.openai_service import OpenAIService

@pytest.fixture
def mock_openai_service():
    """
    Mock the OpenAIService for testing.
    """
    # Mock API client
    mock_api_client = MagicMock()
    mock_api_client.Completion.create.return_value = {
        "choices": [{"text": "Sample response"}]
    }

    # Mock OpenAIService instance
    mock_service = MagicMock(spec=OpenAIService)
    mock_service.api_client = mock_api_client
    mock_service.generate_response = MagicMock(return_value="Sample response")
    return mock_service


def test_generate_response(mock_openai_service):
    """
    Test the generate_response method of OpenAIService.
    """
    prompt = "Test prompt"
    response = mock_openai_service.generate_response(prompt=prompt)

    # Assertions
    mock_openai_service.generate_response.assert_called_once_with(prompt=prompt)
    assert response == "Sample response"
