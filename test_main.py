from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

def test_serve_index():
    """Validates the root endpoint serves the HTML successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_gemini_validation_error():
    """Validates that the API blocks empty requests (Security)."""
    response = client.post("/api/ask-gemini", json={})
    assert response.status_code == 422 

@patch("main.client")
def test_gemini_mocked_success(mock_client):
    """Testing: Mocks the Google GenAI SDK to ensure isolated unit testing without API keys."""
    # Mock the AI's response
    mock_client.models.generate_content.return_value.text = "Mocked AI route recommendation."
    
    payload = {
        "user_location": "Gate 3",
        "query": "Where is the nearest exit?"
    }
    response = client.post("/api/ask-gemini", json=payload)
    
    # Even if API keys are missing, the mock forces a 200 OK
    assert response.status_code == 200
