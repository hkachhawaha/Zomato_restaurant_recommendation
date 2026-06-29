import json
from typing import List, Dict, Any

def build_recommendation_prompt(candidates: List[Dict[str, Any]], preferences: Dict[str, Any]) -> str:
    """
    Constructs the natural language prompt that contains candidate restaurant context
    and user preference constraints to guide the LLM recommendation generation.
    """
    # Clean candidates context to pass only necessary fields (reduces prompt tokens and clears noise)
    cleaned_candidates = []
    for item in candidates:
        cleaned_candidates.append({
            "name": item.get("name"),
            "url": item.get("url"),
            "address": item.get("address"),
            "rate": item.get("rate"),
            "votes": item.get("votes"),
            "rest_type": item.get("rest_type"),
            "dish_liked": item.get("dish_liked"),
            "cuisines": item.get("cuisines"),
            "approx_cost": item.get("approx_cost"),
            "Location": item.get("location")
        })

    # Serialize candidate data
    candidates_json = json.dumps(cleaned_candidates, indent=2)

    # Extract user preference fields with fallback mappings
    location = preferences.get("location", "N/A")
    cuisine = preferences.get("cuisine", "")
    if not cuisine or not cuisine.strip():
        cuisine = "Any Cuisine (no specific preference)"
    budget = preferences.get("budget", "N/A")
    min_rating = preferences.get("min_rating", 0.0)
    additional = preferences.get("additional_preferences", "")
    if not additional.strip():
        additional = "None specified"

    # Construct the instruction template
    prompt = f"""User Preferences:
- Target Neighborhood Location: {location}
- Preferred Cuisine: {cuisine}
- Budget Range: {budget}
- Minimum Quality Rating: {min_rating}
- Additional Custom Requirements: {additional}

Candidate List Context:
{candidates_json}
"""
    return prompt
