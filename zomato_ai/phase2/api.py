import os
import logging
from typing import Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from zomato_ai.phase2.models import RecommendationRequest, RecommendationResponse, RestaurantResponse
from zomato_ai.phase2.repository import RestaurantRepository
from zomato_ai.phase2.filtering import score_and_select_candidates
from zomato_ai.phase3.llm_client import LLMClient
from zomato_ai.phase3.prompt_builder import build_recommendation_prompt
from zomato_ai.config import settings

# Setup logging
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Zomato AI Recommendation Engine API",
    description="Backend microservices to filter, score, and rank Zomato restaurants with heuristic models and LLMs",
    version="1.0.0"
)

# Enable CORS for frontend cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database repository
repo = RestaurantRepository()

@app.get("/api/locations", response_model=list[str])
async def get_locations():
    """Returns a sorted list of unique restaurant neighborhoods in Bangalore."""
    try:
        return repo.get_unique_locations()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

@app.get("/api/cuisines", response_model=list[str])
async def get_cuisines():
    """Returns a sorted list of unique cuisines served across all Bangalore restaurants."""
    try:
        return repo.get_unique_cuisines()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

def generate_fallback_response(ranked_candidates: list, request: RecommendationRequest) -> list[RestaurantResponse]:
    """Generates dynamic heuristic fallback responses if the Gemini API fails."""
    fallback_recs = []
    for idx, item in enumerate(ranked_candidates[:20], 1):
        rate_val = item.get("rate")
        rate_display = f"{rate_val}/5" if rate_val is not None else "N/A"
        votes = item.get("votes") or 0
        
        cuisine_pref = f"{request.cuisine} preference" if request.cuisine and request.cuisine.strip() else "dining preferences"
        
        explanation = (
            f"Rank #{idx} recommendation: {item['name']} perfectly aligns with your {cuisine_pref} "
            f"in {item['location']} within your budget range of ₹{request.min_budget} - ₹{request.max_budget}. "
            f"The establishment features an average cost of ₹{item['approx_cost']} for two, a customer score of "
            f"{rate_display}, and is backed by {votes} community ratings."
        )
        
        fallback_recs.append(
            RestaurantResponse(
                name=item["name"],
                cuisine=item["cuisines"],
                rating=rate_val,
                approx_cost=item["approx_cost"],
                Location=item["location"],
                ai_explanation=explanation
            )
        )
    return fallback_recs

@app.post("/api/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """Processes user preferences, filters database, scores matches with heuristics, and outputs recommendations."""
    try:
        # 1. Query matching records from the database using direct ranges
        candidates = repo.query_restaurants(
            location=request.location,
            min_rating=request.min_rating,
            min_cost=request.min_budget,
            max_cost=request.max_budget,
            cuisine=request.cuisine
        )

        if not candidates:
            return RecommendationResponse(recommendations=[])

        # 2. Apply Heuristic Rating and Popularity sorting
        ranked_candidates = score_and_select_candidates(candidates, top_n=30)

        # 3. Safeguard: De-duplicate candidates by name to prevent duplicates
        seen_names = set()
        unique_candidates = []
        for c in ranked_candidates:
            c_name = c["name"].strip().lower()
            if c_name not in seen_names:
                seen_names.add(c_name)
                unique_candidates.append(c)
        ranked_candidates = unique_candidates[:20]

        # 4. Generate recommendations using Gemini, or fallback to heuristics
        try:
            # Check if LLM bypass is enabled for ultra-low latency
            if settings.BYPASS_LLM:
                logger.info("BYPASS_LLM is enabled. Returning heuristic fallback recommendations immediately.")
                fallback_recs = generate_fallback_response(ranked_candidates, request)
                return RecommendationResponse(recommendations=fallback_recs)

            llm_client = LLMClient()
            # Prepare preferences context
            pref_data = {
                "location": request.location,
                "cuisine": request.cuisine,
                "budget": f"₹{request.min_budget} - ₹{request.max_budget}",
                "min_rating": request.min_rating,
                "additional_preferences": request.additional_preferences
            }
            
            prompt = build_recommendation_prompt(ranked_candidates, pref_data)
            
            # Send prompt to Gemini API
            recommendations_data = await llm_client.get_recommendations_with_reasoning(prompt)
            
            # Map dynamic AI results back to target Pydantic Response schemas
            recommendations = []
            for item in recommendations_data:
                # Ensure the recommended restaurant exists in our deduplicated list
                candidate_match = next((c for c in ranked_candidates if c["name"].strip().lower() == item["name"].strip().lower()), None)
                if candidate_match:
                    recommendations.append(
                        RestaurantResponse(
                            name=candidate_match["name"],
                            cuisine=candidate_match["cuisines"],
                            rating=candidate_match.get("rate"),
                            approx_cost=candidate_match.get("approx_cost") or request.min_budget,
                            Location=request.location,
                            ai_explanation=item.get("ai_explanation", "")
                        )
                    )
            
            if not recommendations:
                raise ValueError("LLM generated zero valid recommendations.")
                
            return RecommendationResponse(recommendations=recommendations)

        except Exception as llm_err:
            logger.warning(f"LLM Recommendation failed: {llm_err}. Using heuristic fallback response.")
            fallback_recs = generate_fallback_response(ranked_candidates, request)
            return RecommendationResponse(recommendations=fallback_recs)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation processing error: {str(e)}")

@app.get("/api/restaurant", response_model=Optional[RestaurantResponse])
async def get_restaurant(name: str):
    """Returns a single restaurant details by exact name."""
    try:
        res = repo.get_restaurant_by_name(name)
        if not res:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        rate_val = float(res["rate"]) if res["rate"] else None
        return RestaurantResponse(
            name=res["name"],
            cuisine=res["cuisines"],
            rating=rate_val,
            approx_cost=res["approx_cost"],
            Location=res["location"],
            ai_explanation=f"Highly recommended spot in {res['location']} serving {res['cuisines']}. Popular amongst locals with {res['votes']} reviews."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

# Mount static folder (declared AFTER API routes to prevent route masking)
static_path = Path(__file__).resolve().parent.parent / "static"
static_path.mkdir(parents=True, exist_ok=True)
app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")
