from unittest.mock import patch
from fastapi.testclient import TestClient
from zomato_ai.phase2.api import app
from zomato_ai.phase3.llm_client import LLMClient

client = TestClient(app)

def test_llm_failure_failsafe_fallback():
    # Mock LLM Client get_recommendations_with_reasoning method to throw exception
    with patch.object(LLMClient, 'get_recommendations_with_reasoning', side_effect=RuntimeError("API quota limits exceeded")):
        payload = {
            "location": "Whitefield",
            "min_budget": 500,
            "max_budget": 1200,
            "cuisine": "Chinese",
            "min_rating": 4.0,
            "additional_preferences": "famous for dim sums"
        }
        
        response = client.post("/api/recommend", json=payload)
        
        # Verify response is HTTP 200 OK despite the mocked Gemini error
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        
        data = response.json()
        assert "recommendations" in data
        recs = data["recommendations"]
        
        # Verify that candidate entries are returned using the fallback formatting
        assert len(recs) > 0, "No recommendations returned in fallback state"
        
        first_rec = recs[0]
        assert first_rec["name"], "Expected restaurant name"
        assert first_rec["ai_explanation"], "Expected explanation string"
        
        # Assert that explanation fits the fallback structure specified in api.py
        assert "perfectly aligns with your Chinese preference" in first_rec["ai_explanation"]
        assert "within your budget range of" in first_rec["ai_explanation"]
        print("Success! Fallback validation test passed.")
