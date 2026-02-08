"""
Unified Job Discovery
Combines API-based job listings with smart search URLs
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class JobSource(str, Enum):
    """Job source types"""
    API = "api"  # Actual job from API
    SEARCH_URL = "search_url"  # Smart search URL
    CAMPUS = "campus"  # Campus placement data


class JobType(str, Enum):
    """Job listing types"""
    DIRECT = "direct"  # Can apply directly
    EXTERNAL = "external"  # Redirects to external site


class UnifiedJob(BaseModel):
    """
    Unified job representation
    
    Can represent either:
    - Actual job listing (from API)
    - Smart search URL (for platforms without APIs)
    """
    # Core fields
    job_id: str
    title: str
    company: str
    location: str
    
    # Source metadata
    source: JobSource
    source_platform: str  # "LinkedIn", "Indeed", "Naukri", etc.
    job_type: JobType
    
    # Job details (optional for search URLs)
    description: Optional[str] = None
    posted_date: Optional[str] = None
    salary_range: Optional[str] = None
    experience_required: Optional[str] = None
    
    # Action
    action_url: str  # Either apply URL or search URL
    action_label: str  # "Apply Now" or "Search on Naukri"
    
    # Match metadata
    match_score: Optional[int] = None  # 0-100
    match_reason: Optional[str] = None
    
    # Additional metadata
    is_remote: bool = False
    is_verified: bool = False
    
    class Config:
        use_enum_values = True


class UnifiedJobResponse(BaseModel):
    """Response containing all job discoveries"""
    
    # Actual job listings
    api_jobs: List[UnifiedJob] = []
    
    # Smart search URLs
    search_recommendations: List[UnifiedJob] = []
    
    # Summary
    total_api_jobs: int = 0
    total_search_urls: int = 0
    total_results: int = 0
    
    # Metadata
    search_metadata: dict = {}


class JobDiscoveryRequest(BaseModel):
    """Request for unified job discovery"""
    
    # Resume intelligence
    primary_roles: List[str]
    role_family: str
    years_of_experience: float
    top_skills: List[str] = []
    
    # Preferences
    preferred_locations: List[str] = []
    location_flexibility: str = "flexible"
    salary_expectation: Optional[str] = None
    
    # API keys (optional)
    linkedin_api_key: Optional[str] = None
    indeed_api_key: Optional[str] = None
