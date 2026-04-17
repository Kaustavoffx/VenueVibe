from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_serve_index():
    """Validates the root endpoint serves the HTML successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_gemini_validation_error():
    """Validates that the API blocks empty or malformed requests (Security/Validation)."""
    response = client.post("/api/ask-gemini", json={})
    assert response.status_code == 422 # Standard FastAPI validation failure

def test_gemini_payload_structure():
    """Validates that the endpoint accepts properly formatted Pydantic models."""
    payload = {
        "user_location": "Gate 3",
        "query": "Where is the nearest exit?"
    }
    response = client.post("/api/ask-gemini", json=payload)
    # Status will be 200 (success) or 503 (if API key isn't in the test environment)
    assert response.status_code in [200, 503]
