"""
Campus Data Mapper
Maps campus portal JSON to ResumiMBAJob schema
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.mba_data.schemas import (
    ResumiMBAJob,
    RoleFamily,
    WorkMode,
    EmploymentType,
    CTCBand
)

logger = logging.getLogger(__name__)


def map_campus_job(campus_job: dict) -> Optional[ResumiMBAJob]:
    """
    Map campus portal job data to ResumiMBAJob schema
    
    Follows the authoritative mapping defined in STEP 17
    
    Args:
        campus_job: Raw campus portal job JSON
        
    Returns:
        ResumiMBAJob or None if mapping fails
    """
    try:
        # Extract company data
        company_data = campus_job.get('recruitingCompanyId', {})
        
        # Extract roles and select primary
        roles = campus_job.get('roles', [])
        primary_role = _select_primary_role(roles)
        
        # Extract team/function
        teams = campus_job.get('team', [])
        team_function = teams[0].get('name') if teams else None
        
        # Classify role family
        role_family = _classify_role_family(primary_role, team_function, campus_job.get('title', ''))
        
        # Extract locations
        job_locations = [loc.get('name') for loc in campus_job.get('location', []) if loc.get('name')]
        
        # Extract work mode
        work_arrangement = campus_job.get('workArrangement', {})
        work_mode = _map_work_mode(work_arrangement.get('mode'))
        
        # Extract CTC
        ctc_data = campus_job.get('ctc', {})
        ctc_min = ctc_data.get('from')
        ctc_max = ctc_data.get('to')
        ctc_currency = ctc_data.get('currency', 'INR')
        ctc_band = _calculate_ctc_band(ctc_min, ctc_max, ctc_currency)
        
        # Extract employment type
        employment_type = _map_employment_type(campus_job.get('type'))
        
        # Extract sectors
        sectors = company_data.get('sectors', [])
        company_sector = _extract_primary_sector(sectors)
        
        # Extract company locations
        company_locations = [loc.get('name') for loc in company_data.get('location', []) if loc.get('name')]
        
        # Extract JD attachments
        jd_files = campus_job.get('jdFiles', [])
        jd_attachments = [f.get('url') for f in jd_files if f.get('url')]
        
        return ResumiMBAJob(
            # Core Identity
            job_id=str(campus_job.get('_id', '')),
            job_title=campus_job.get('title', 'Unknown Title'),
            job_status=campus_job.get('status', 'UNKNOWN'),
            
            # Company Context
            company_name=company_data.get('companyName', 'Unknown Company'),
            company_sector=company_sector,
            company_size=company_data.get('companySize'),
            company_location=company_locations if company_locations else None,
            
            # Role Classification
            primary_role=primary_role,
            role_family=role_family,
            team_function=team_function,
            employment_type=employment_type,
            
            # Work & Location
            job_locations=job_locations,
            work_mode=work_mode,
            open_to_relocation="Unknown",  # Not in campus data
            
            # Compensation
            ctc_min=ctc_min,
            ctc_max=ctc_max,
            ctc_currency=ctc_currency,
            ctc_band=ctc_band,
            
            # Experience & Eligibility
            experience_required=campus_job.get('experience'),
            education_required=campus_job.get('educationCriteria'),
            eligibility_notes=campus_job.get('eligibilityCriteria'),
            
            # Job Content (INTERNAL ONLY)
            job_description_raw=campus_job.get('description'),
            jd_attachments=jd_attachments,
            
            # Metadata
            source='campus_data',
            imported_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to map campus job: {e}")
        return None


def _select_primary_role(roles: List[Dict]) -> Optional[str]:
    """
    Select the most business-facing role from multiple roles
    
    Priority:
    1. Strategy/Consulting roles
    2. Operations/Finance/Marketing roles
    3. Other business roles
    4. Tech roles (lowest priority for MBA)
    """
    if not roles:
        return None
    
    # Business role keywords (high priority)
    business_keywords = ['strategy', 'consultant', 'operations', 'finance', 'marketing', 'sales', 'hr']
    
    # Find most business-facing role
    for role in roles:
        role_name = role.get('name', '').lower()
        if any(keyword in role_name for keyword in business_keywords):
            return role.get('name')
    
    # Default to first role
    return roles[0].get('name')


def _classify_role_family(primary_role: Optional[str], team_function: Optional[str], job_title: str) -> RoleFamily:
    """
    Classify role into RoleFamily enum
    
    Uses primary_role, team_function, and job_title for classification
    """
    text = f"{primary_role or ''} {team_function or ''} {job_title}".lower()
    
    # Strategy/Consulting
    if any(kw in text for kw in ['strategy', 'strategic', 'consultant', 'consulting', 'business development']):
        return RoleFamily.STRATEGY
    
    # Operations
    if any(kw in text for kw in ['operations', 'supply chain', 'logistics', 'process', 'ops']):
        return RoleFamily.OPERATIONS
    
    # Finance
    if any(kw in text for kw in ['finance', 'financial', 'investment', 'accounting', 'treasury']):
        return RoleFamily.FINANCE
    
    # Marketing
    if any(kw in text for kw in ['marketing', 'brand', 'growth', 'digital marketing', 'demand gen']):
        return RoleFamily.MARKETING
    
    # Sales
    if any(kw in text for kw in ['sales', 'account', 'revenue', 'business development']):
        return RoleFamily.SALES
    
    # HR
    if any(kw in text for kw in ['hr', 'human resources', 'talent', 'people', 'recruiting']):
        return RoleFamily.HR
    
    # Product
    if any(kw in text for kw in ['product', 'product manager', 'product management']):
        return RoleFamily.PRODUCT
    
    # General Management
    if any(kw in text for kw in ['general management', 'ceo', 'coo', 'chief']):
        return RoleFamily.GENERAL_MGMT
    
    # Tech (for MBA-tech hybrid)
    if any(kw in text for kw in ['engineer', 'developer', 'software', 'data scientist', 'analyst']):
        return RoleFamily.TECH
    
    return RoleFamily.UNKNOWN


def _map_work_mode(mode: Optional[str]) -> WorkMode:
    """Map work arrangement mode to WorkMode enum"""
    if not mode:
        return WorkMode.UNKNOWN
    
    mode_lower = mode.lower()
    
    if 'remote' in mode_lower:
        return WorkMode.REMOTE
    elif 'hybrid' in mode_lower:
        return WorkMode.HYBRID
    elif 'onsite' in mode_lower or 'office' in mode_lower:
        return WorkMode.ONSITE
    
    return WorkMode.UNKNOWN


def _map_employment_type(emp_type: Optional[str]) -> EmploymentType:
    """Map employment type to EmploymentType enum"""
    if not emp_type:
        return EmploymentType.UNKNOWN
    
    type_lower = emp_type.lower()
    
    if 'full' in type_lower or 'permanent' in type_lower:
        return EmploymentType.FULL_TIME
    elif 'intern' in type_lower:
        return EmploymentType.INTERNSHIP
    elif 'contract' in type_lower:
        return EmploymentType.CONTRACT
    
    return EmploymentType.UNKNOWN


def _calculate_ctc_band(ctc_min: Optional[float], ctc_max: Optional[float], currency: str) -> CTCBand:
    """
    Calculate CTC band based on min/max values
    
    Bands (for INR in LPA):
    - Low: < 15
    - Medium: 15-25
    - High: 25-40
    - Very High: > 40
    """
    if currency != 'INR':
        return CTCBand.UNKNOWN
    
    # Use max if available, otherwise min
    ctc = ctc_max or ctc_min
    
    if ctc is None:
        return CTCBand.UNKNOWN
    
    # Convert to LPA if in absolute terms
    if ctc > 1000000:  # Likely in rupees, not LPA
        ctc = ctc / 100000
    
    if ctc < 15:
        return CTCBand.LOW
    elif ctc < 25:
        return CTCBand.MEDIUM
    elif ctc < 40:
        return CTCBand.HIGH
    else:
        return CTCBand.VERY_HIGH


def _extract_primary_sector(sectors: List[Dict]) -> Optional[str]:
    """Extract primary sector from sectors array"""
    if not sectors:
        return None
    
    # Return first sector name
    return sectors[0].get('name')
