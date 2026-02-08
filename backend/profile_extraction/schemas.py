"""
Profile Data Schemas
Pydantic models for profile validation
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator


class ProfileSchema(BaseModel):
    """Structured profile extracted from resume"""
    
    primary_role: str = Field(..., description="Primary role family (e.g., 'software engineer')")
    seniority: str = Field(..., description="Seniority level: junior, mid, senior, lead, principal")
    skills: List[str] = Field(default_factory=list, description="Technical skills")
    tools: List[str] = Field(default_factory=list, description="Tools and technologies")
    experience_years: int = Field(..., ge=0, description="Total years of experience")
    education: List[str] = Field(default_factory=list, description="Education background")
    location_mentions: List[str] = Field(default_factory=list, description="Locations mentioned in resume")
    skill_clusters: List[str] = Field(default_factory=list, description="High-level skill categories")
    job_titles: List[str] = Field(default_factory=list, description="Previous job titles")
    
    @validator('seniority')
    def validate_seniority(cls, v):
        valid_levels = ['junior', 'mid', 'senior', 'lead', 'principal']
        if v not in valid_levels:
            return 'mid'  # Default fallback
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "primary_role": "software engineer",
                "seniority": "senior",
                "skills": ["python", "fastapi", "react", "postgresql"],
                "tools": ["git", "docker", "kubernetes"],
                "experience_years": 6,
                "education": ["BS Computer Science"],
                "location_mentions": ["San Francisco", "California"],
                "skill_clusters": ["backend", "frontend", "cloud"],
                "job_titles": ["Senior Software Engineer", "Software Developer"]
            }
        }


class UserPreferences(BaseModel):
    """User preferences for job matching"""
    
    career_goals: Optional[str] = Field(None, description="Career goals and aspirations")
    preferred_locations: List[str] = Field(default_factory=list, description="Preferred work locations")
    open_to_relocation: bool = Field(default=False, description="Willing to relocate")
    open_to_international: bool = Field(default=False, description="Open to international roles")
    remote_only: bool = Field(default=False, description="Only interested in remote positions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "career_goals": "Looking for senior backend roles in cloud infrastructure",
                "preferred_locations": ["San Francisco", "Remote"],
                "open_to_relocation": False,
                "open_to_international": True,
                "remote_only": False
            }
        }
