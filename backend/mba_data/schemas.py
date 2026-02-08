"""
MBA Data Schemas
Defines the ResumiMBAJob schema for standardized MBA job representation
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime


class RoleFamily(str, Enum):
    """MBA Role Families"""
    OPERATIONS = "Operations"
    FINANCE = "Finance"
    MARKETING = "Marketing"
    STRATEGY = "Strategy"
    HR = "HR"
    GENERAL_MGMT = "General Management"
    TECH = "Tech"  # For MBA-tech hybrid roles
    SALES = "Sales"
    CONSULTING = "Consulting"
    PRODUCT = "Product Management"
    UNKNOWN = "Unknown"


class WorkMode(str, Enum):
    """Work arrangement mode"""
    ONSITE = "Onsite"
    HYBRID = "Hybrid"
    REMOTE = "Remote"
    UNKNOWN = "Unknown"


class EmploymentType(str, Enum):
    """Type of employment"""
    FULL_TIME = "Full-time"
    INTERNSHIP = "Internship"
    CONTRACT = "Contract"
    UNKNOWN = "Unknown"


class CTCBand(str, Enum):
    """CTC bands for Indian market (in LPA)"""
    LOW = "Low"          # < 15 LPA
    MEDIUM = "Medium"    # 15-25 LPA
    HIGH = "High"        # 25-40 LPA
    VERY_HIGH = "Very High"  # > 40 LPA
    UNKNOWN = "Unknown"


class ResumiMBAJob(BaseModel):
    """
    Standardized MBA Job Schema
    
    This is the ONLY schema used for reasoning about MBA jobs.
    All campus data must be mapped to this format.
    
    CRITICAL: This data is INTERNAL ONLY - never expose to users
    """
    
    # Core Identity
    job_id: str = Field(..., description="Unique job identifier from source")
    job_title: str = Field(..., description="Job title as posted")
    job_status: str = Field(default="UNKNOWN", description="ACTIVE | INACTIVE | UNKNOWN")
    
    # Company Context
    company_name: str = Field(..., description="Recruiting company name")
    company_sector: Optional[str] = Field(None, description="Primary sector/industry")
    company_size: Optional[str] = Field(None, description="Company size category")
    company_location: Optional[List[str]] = Field(None, description="Company HQ/office locations")
    
    # Role Classification
    primary_role: Optional[str] = Field(None, description="Primary role title")
    role_family: RoleFamily = Field(RoleFamily.UNKNOWN, description="Classified role family")
    team_function: Optional[str] = Field(None, description="Team/department function")
    employment_type: EmploymentType = Field(EmploymentType.UNKNOWN, description="Employment type")
    
    # Work & Location
    job_locations: List[str] = Field(default_factory=list, description="Job location(s)")
    work_mode: WorkMode = Field(WorkMode.UNKNOWN, description="Work arrangement")
    open_to_relocation: str = Field("Unknown", description="Relocation flexibility")
    
    # Compensation
    ctc_min: Optional[float] = Field(None, description="Minimum CTC")
    ctc_max: Optional[float] = Field(None, description="Maximum CTC")
    ctc_currency: str = Field("INR", description="Currency code")
    ctc_band: CTCBand = Field(CTCBand.UNKNOWN, description="Derived CTC band")
    
    # Experience & Eligibility
    experience_required: Optional[str] = Field(None, description="Work experience requirement")
    education_required: Optional[str] = Field(None, description="Education requirement")
    eligibility_notes: Optional[str] = Field(None, description="Additional eligibility criteria")
    
    # Job Content (NEVER DISPLAY TO USERS)
    job_description_raw: Optional[str] = Field(None, description="Raw job description - INTERNAL ONLY")
    jd_attachments: List[str] = Field(default_factory=list, description="JD file URLs - INTERNAL ONLY")
    
    # Metadata
    source: str = Field("campus_data", description="Data source identifier")
    imported_at: Optional[str] = Field(None, description="Import timestamp")
    
    class Config:
        use_enum_values = True


class MBAJobPattern(BaseModel):
    """Pattern learned from MBA job data"""
    pattern_type: str  # role | skill | eligibility | location
    role_family: Optional[RoleFamily] = None
    pattern_data: dict
    sample_count: int
    confidence: float  # 0.0 to 1.0
    last_updated: str


class SkillCluster(BaseModel):
    """Skill cluster for a role family"""
    role_family: RoleFamily
    must_have_skills: List[str] = []
    nice_to_have_skills: List[str] = []
    rarely_required_skills: List[str] = []
    sample_count: int
    
    
class LocationPattern(BaseModel):
    """Location pattern for a role family"""
    role_family: RoleFamily
    india_cities: List[str] = []
    uae_cities: List[str] = []
    other_locations: List[str] = []
    pan_india: bool = False
    sample_count: int
