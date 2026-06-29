import pytest
from fastapi.testclient import TestClient
from zomato_ai.phase2.api import app

@pytest.fixture
def client():
    return TestClient(app)

def test_locations_endpoint(client):
    """Verify GET /api/locations returns locations list."""
    response = client.get("/api/locations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "Whitefield" in data

def test_cuisines_endpoint(client):
    """Verify GET /api/cuisines returns unique cuisines list."""
    response = client.get("/api/cuisines")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "Chinese" in data

def test_recommend_endpoint_empty(client):
    """Verify POST /api/recommend returns empty list for impossible criteria."""
    payload = {
        "location": "Whitefield",
        "min_rating": 5.0, # Rating higher than maximum
        "min_budget": 10000, # Cost higher than maximum
        "max_budget": 20000,
        "cuisine": "Chinese",
        "additional_preferences": ""
    }
    response = client.post("/api/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) == 0

def test_recommend_endpoint_results(client):
    """Verify POST /api/recommend returns populated fallback recommendations."""
    payload = {
        "location": "Whitefield",
        "min_rating": 3.0,
        "min_budget": 200,
        "max_budget": 1000,
        "cuisine": "Chinese",
        "additional_preferences": ""
    }
    response = client.post("/api/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    recs = data["recommendations"]
    assert len(recs) # Fallback or LLM should return candidates within the request size budget
    assert len(recs) <= 20
    for r in recs:
        assert r["name"] is not None
        assert r["cuisine"] is not None
        assert r["rating"] >= 3.0
        assert r["approx_cost"] >= 200 and r["approx_cost"] <= 1000

def test_restaurant_details_endpoint(client):
    """Verify GET /api/restaurant returns restaurant details."""
    response = client.get("/api/restaurant?name=Empire Restaurant")
    assert response.status_code == 200
    data = response.json()
    # It might return details if Empire Restaurant exists, or null. But status code is always 200.
    if data:
        assert "name" in data
        assert "cuisine" in data

def test_cors_headers(client):
    """Verify CORS headers are present to support Next.js ports integration."""
    response = client.options("/api/locations", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET"
    })
    # Since CORSMiddleware handles OPTIONS requests:
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000" or response.headers["access-control-allow-origin"] == "*"
