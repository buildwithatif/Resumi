"""
External Search Schemas
Defines data models for external search recommendations
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class SearchPlatform(str, Enum):
    """Supported job search platforms"""
    NAUKRI = "Naukri"
    INSTAHYRE = "Instahyre"


class ExternalSearchRecommendation(BaseModel):
    """
    External search URL recommendation
    
    Represents a single optimized search URL for a job portal
    """
    platform: SearchPlatform = Field(..., description="Job search platform")
    role_focus: str = Field(..., description="Primary role being searched")
    location_focus: str = Field(..., description="Location being searched")
    experience_band: str = Field(..., description="Experience range (e.g., '2-4 years')")
    search_url: str = Field(..., description="Complete search URL")
    why_this_search: str = Field(..., description="Human-readable explanation")
    relevance_score: int = Field(..., description="Relevance score (0-10)")
    
    class Config:
        use_enum_values = True


class SearchGenerationRequest(BaseModel):
    """Request for generating external search URLs"""
    
    # Resume Intelligence
    primary_roles: List[str] = Field(..., description="Primary roles from resume")
    role_family: str = Field(..., description="Role family (Ops, Finance, etc.)")
    years_of_experience: float = Field(..., description="Total years of experience")
    top_skills: List[str] = Field(default_factory=list, description="Top 5-8 skills")
    
    # User Preferences
    preferred_locations: List[str] = Field(default_factory=list, description="Preferred locations")
    location_flexibility: str = Field("flexible", description="strict | flexible")
    experience_flexibility: bool = Field(True, description="Allow ±1 year variance")
    
    # Optional
    include_mba_tag: bool = Field(True, description="Include 'MBA' in search phrases")


class SearchGenerationResponse(BaseModel):
    """Response containing generated search URLs"""
    
    naukri_searches: List[ExternalSearchRecommendation] = []
    instahyre_searches: List[ExternalSearchRecommendation] = []
    total_recommendations: int
    generation_metadata: dict = {}
