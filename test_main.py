import pytest
from fastapi.testclient import TestClient
from main import app, client
from unittest.mock import MagicMock, patch

test_client = TestClient(app)

def test_read_index():
    response = test_client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Navigate the Arena with AI" in response.text

@patch("main.client")
def test_ask_gemini_success(mock_client):
    # Mocking the Gemini response
    mock_response = MagicMock()
    mock_response.text = "The closest restroom is near Gate 4. Wait time is 5 minutes."
    
    mock_models = MagicMock()
    mock_models.generate_content.return_value = mock_response
    mock_client.models = mock_models

    response = test_client.post(
        "/api/ask-gemini",
        json={"user_location": "Gate 4", "query": "Which restroom has the shortest line?"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["response"] == "The closest restroom is near Gate 4. Wait time is 5 minutes."

@patch("main.client")
def test_ask_gemini_error(mock_client):
    # Mocking an exception in Gemini API
    mock_models = MagicMock()
    mock_models.generate_content.side_effect = Exception("API error")
    mock_client.models = mock_models

    response = test_client.post(
        "/api/ask-gemini",
        json={"user_location": "Gate 4", "query": "Which restroom has the shortest line?"}
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Error communicating with AI services."

def test_ask_gemini_no_api_key():
    # If API key is not configured, we want to ensure we handle it or mock appropriately
    with patch("main.client", None):
        response = test_client.post(
            "/api/ask-gemini",
            json={"user_location": "Gate 4", "query": "Which restroom has the shortest line?"}
        )
        assert response.status_code == 500
        assert response.json()["detail"] == "Gemini API Key is not configured."
