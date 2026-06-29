import streamlit as st
import asyncio
import os
from typing import List
from zomato_ai.config import settings
from zomato_ai.phase2.repository import RestaurantRepository
from zomato_ai.phase2.filtering import score_and_select_candidates
from zomato_ai.phase3.llm_client import LLMClient
from zomato_ai.phase3.prompt_builder import build_recommendation_prompt
from zomato_ai.phase2.models import RecommendationRequest, RestaurantResponse
from zomato_ai.phase2.api import generate_fallback_response

# Page configuration
st.set_page_config(
    page_title="GourmetAI - Taste Engineering Portal",
    page_icon="🥘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Outfit', sans-serif;
    }
    .main-title {
        color: #B91C1C;
        font-weight: 700;
        font-size: 2.8rem;
        margin-bottom: 0.25rem;
    }
    .subtitle {
        color: #6B7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .restaurant-card {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
        border: 1px solid #E5E7EB;
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .restaurant-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.08), 0 4px 6px -4px rgb(0 0 0 / 0.08);
    }
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .restaurant-name {
        color: #1C1917;
        font-size: 1.35rem;
        font-weight: 600;
        margin: 0;
    }
    .rating-badge {
        background-color: #FEF2F2;
        color: #B91C1C;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid #FEE2E2;
    }
    .meta-row {
        color: #4B5563;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }
    .explanation-bubble {
        background-color: #FAFAF9;
        border-left: 4px solid #B91C1C;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        font-style: italic;
        color: #374151;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">🥘 GourmetAI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Bangalore\'s premium restaurant recommendation engine, deployed on Streamlit Cloud</div>', unsafe_allow_html=True)

# Initialize DB access
@st.cache_resource
def get_repository():
    return RestaurantRepository(settings.db_path)

repo = get_repository()

@st.cache_data
def get_metadata():
    locations = repo.get_unique_locations()
    cuisines = repo.get_unique_cuisines()
    return locations, cuisines

try:
    available_locations, available_cuisines = get_metadata()
except Exception as e:
    available_locations = ["Whitefield", "Indiranagar", "Koramangala", "Jayanagar", "HSR"]
    available_cuisines = ["Chinese", "North Indian", "Continental", "South Indian", "Italian", "American"]

# Build sidebar form
with st.sidebar:
    st.header("🎯 Preferences")
    
    # Neighborhood select
    location = st.selectbox(
        "Bangalore Neighborhood",
        options=sorted(available_locations),
        index=sorted(available_locations).index("Whitefield") if "Whitefield" in available_locations else 0
    )
    
    # Cuisine select
    cuisine = st.selectbox(
        "Preferred Cuisine (Optional)",
        options=["Any Cuisine"] + sorted(available_cuisines),
        index=0
    )
    selected_cuisine = "" if cuisine == "Any Cuisine" else cuisine
    
    # Budget slider
    st.write("**Budget Range (For Two)**")
    min_budget, max_budget = st.slider(
        "Price range (₹)",
        min_value=0,
        max_value=5000,
        value=(200, 1500),
        step=50
    )
    
    # Rating slider
    min_rating = st.slider(
        "Minimum Rating Threshold",
        min_value=0.0,
        max_value=5.0,
        value=3.5,
        step=0.1
    )
    
    # Vibe details
    additional_preferences = st.text_area(
        "Special Vibe & Preferences",
        placeholder="e.g. rooftop, craft beer, family friendly, famous for pizzas..."
    )
    
    submit_clicked = st.button("Find My Match →", use_container_width=True, type="primary")

# Execute matching on submit
if submit_clicked:
    st.subheader(f"✨ Match Curations in {location}")
    
    with st.spinner("Scoring and filtering candidate restaurants..."):
        candidates = repo.query_restaurants(
            location=location,
            min_rating=min_rating,
            min_cost=min_budget,
            max_cost=max_budget,
            cuisine=selected_cuisine
        )
        
        # Heuristic scoring and deduplication
        seen_names = set()
        unique_candidates = []
        for c in candidates:
            c_name = c["name"].strip().lower()
            if c_name not in seen_names:
                seen_names.add(c_name)
                unique_candidates.append(c)
        
        ranked_candidates = unique_candidates[:20]
        
    if not ranked_candidates:
        st.warning("No matches found matching your filters. Try broadening your location, rating, or budget parameters.")
    else:
        req = RecommendationRequest(
            location=location,
            min_budget=min_budget,
            max_budget=max_budget,
            cuisine=selected_cuisine,
            min_rating=min_rating,
            additional_preferences=additional_preferences
        )
        
        recommendations = []
        
        # Run bypass if configured
        if settings.BYPASS_LLM:
            st.info("⚡ Low-latency heuristics mode active. Served immediately.")
            recommendations = generate_fallback_response(ranked_candidates, req)
        else:
            with st.spinner("Generating AI match rationale justifications..."):
                try:
                    llm_client = LLMClient()
                    pref_data = {
                        "location": location,
                        "cuisine": selected_cuisine,
                        "budget": f"₹{min_budget} - ₹{max_budget}",
                        "min_rating": min_rating,
                        "additional_preferences": additional_preferences
                    }
                    prompt = build_recommendation_prompt(ranked_candidates, pref_data)
                    
                    async def fetch():
                        return await llm_client.get_recommendations_with_reasoning(prompt)
                    
                    recommendations = asyncio.run(fetch())
                except Exception as err:
                    st.warning(f"Gemini API could not compile rationales: {err}. Serving heuristic templates.")
                    recommendations = generate_fallback_response(ranked_candidates, req)
                    
        # Render Results
        # Normalize: recommendations can be Pydantic models or raw dicts from LLM
        normalized = []
        for rec in recommendations:
            if hasattr(rec, "model_dump"):
                normalized.append(rec.model_dump())
            elif isinstance(rec, dict):
                normalized.append(rec)
            else:
                normalized.append(dict(rec))
        
        st.write(f"Displaying **{len(normalized)}** top recommendations:")
        for idx, rec in enumerate(normalized, 1):
            rating_val = rec.get("rating")
            rating_display = f"⭐ {rating_val:.1f}" if rating_val is not None else "⭐ N/A"
            cost_display = f"₹{rec.get('approx_cost', 'N/A')} for two"
            rec_name = rec.get("name", "Unknown")
            rec_location = rec.get("Location", rec.get("location", ""))
            rec_cuisine = rec.get("cuisine", rec.get("cuisines", ""))
            rec_explanation = rec.get("ai_explanation", "")
            
            st.markdown(f"""
            <div class="restaurant-card">
                <div class="card-header">
                    <span class="restaurant-name">{idx}. {rec_name}</span>
                    <span class="rating-badge">{rating_display}</span>
                </div>
                <div class="meta-row">
                    📍 {rec_location} &nbsp;•&nbsp; 🍴 {rec_cuisine} &nbsp;•&nbsp; 💰 {cost_display}
                </div>
                <div class="explanation-bubble">
                    "{rec_explanation}"
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    # Landing page state
    st.info("👈 Set your neighborhood, budget range, and preferred cuisines in the sidebar, then click **Find My Match** to generate curations!")
