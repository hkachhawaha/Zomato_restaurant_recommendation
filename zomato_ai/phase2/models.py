from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class RecommendationRequest(BaseModel):
    location: str = Field(..., description="Target area or neighborhood in Bangalore", min_length=2)
    min_budget: int = Field(default=0, ge=0, description="Minimum budget range for two people")
    max_budget: int = Field(default=99999, ge=0, description="Maximum budget range for two people")
    cuisine: Optional[str] = Field(default="", description="Preferred type of cuisine (e.g. Italian, Chinese, North Indian)")
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Minimum rating required (0.0 to 5.0)")
    additional_preferences: Optional[str] = Field(default="", description="Any additional semantic preferences")

class RestaurantResponse(BaseModel):
    name: str = Field(..., description="Restaurant name")
    cuisine: str = Field(..., description="Cuisines served")
    rating: Optional[float] = Field(default=None, description="Cleansed float rating")
    approx_cost: int = Field(..., description="Normalized cost for two people")
    Location: str = Field(..., description="Specific neighborhood location")
    ai_explanation: str = Field(..., description="AI generated or fallback rationale for recommendation")

class RecommendationResponse(BaseModel):
    recommendations: List[RestaurantResponse] = Field(..., description="List of matched and ranked recommendations")
