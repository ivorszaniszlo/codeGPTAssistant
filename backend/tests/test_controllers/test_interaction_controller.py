import pytest
from unittest.mock import MagicMock
from app.services.openai_service import OpenAIService
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(autouse=True)
def mock_openai_service(monkeypatch):
    """
    Mock the OpenAIService for all tests.
    """
    # Mock OpenAIService
    mock_service = MagicMock(spec=OpenAIService)
    mock_service.generate_response.return_value = "Mocked response"

    # Patch the OpenAIService instance used by the app
    monkeypatch.setattr("app.controllers.interaction_controller.openai_service", mock_service)
    return mock_service

def test_submit_endpoint_success(mock_openai_service):
    """
    Test the /submit endpoint for a successful response.
    """
    with TestClient(app) as client:
        response = client.post(
            "/submit",
            json={"prompt": "Test prompt", "code": "", "language": "Python"}
        )
        assert response.status_code == 200
        assert response.json()["response"] == "Mocked response"
