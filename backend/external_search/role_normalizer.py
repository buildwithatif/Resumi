"""
Role Normalizer
Expands primary roles into realistic adjacent titles for MBA profiles
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


# MBA-aligned role expansions
ROLE_EXPANSIONS: Dict[str, List[str]] = {
    # Operations
    "Operations Analyst": [
        "Business Operations",
        "Program Management",
        "PMO",
        "Strategy & Operations",
        "Operations Manager"
    ],
    "Operations Manager": [
        "Business Operations Manager",
        "Program Manager",
        "Operations Lead",
        "Process Excellence Manager"
    ],
    "Supply Chain Analyst": [
        "Supply Chain Manager",
        "Logistics Manager",
        "Supply Chain Operations",
        "Procurement Manager"
    ],
    
    # Strategy
    "Strategy Consultant": [
        "Business Strategy",
        "Corporate Strategy",
        "Strategy Manager",
        "Management Consultant",
        "Business Analyst"
    ],
    "Business Analyst": [
        "Strategy Analyst",
        "Management Consultant",
        "Business Strategy",
        "Corporate Strategy Analyst"
    ],
    
    # Finance
    "Finance Analyst": [
        "Financial Analyst",
        "Investment Analyst",
        "Corporate Finance",
        "FP&A Analyst",
        "Finance Manager"
    ],
    "Financial Analyst": [
        "Investment Analyst",
        "FP&A Analyst",
        "Corporate Finance Analyst",
        "Finance Associate"
    ],
    "Investment Analyst": [
        "Investment Banking Analyst",
        "Equity Research Analyst",
        "Financial Analyst",
        "Portfolio Analyst"
    ],
    
    # Marketing
    "Marketing Manager": [
        "Growth Marketing",
        "Digital Marketing Manager",
        "Brand Manager",
        "Product Marketing",
        "Marketing Lead"
    ],
    "Brand Manager": [
        "Product Marketing Manager",
        "Marketing Manager",
        "Brand Marketing",
        "Category Manager"
    ],
    "Digital Marketing Manager": [
        "Growth Marketing Manager",
        "Performance Marketing",
        "Marketing Manager",
        "Demand Generation Manager"
    ],
    
    # Sales
    "Sales Manager": [
        "Business Development Manager",
        "Account Manager",
        "Sales Lead",
        "Revenue Manager"
    ],
    "Business Development Manager": [
        "Sales Manager",
        "Account Manager",
        "Partnership Manager",
        "Growth Manager"
    ],
    
    # HR
    "HR Manager": [
        "HR Business Partner",
        "Talent Acquisition Manager",
        "People Operations",
        "HR Lead"
    ],
    "Talent Acquisition": [
        "Recruitment Manager",
        "HR Business Partner",
        "Talent Manager",
        "Hiring Manager"
    ],
    
    # Product
    "Product Manager": [
        "Product Management",
        "Associate Product Manager",
        "Product Lead",
        "Product Strategy"
    ],
    
    # General Management
    "General Manager": [
        "Business Manager",
        "Operations Head",
        "Department Head",
        "Unit Manager"
    ]
}


# Role family to generic titles
ROLE_FAMILY_DEFAULTS: Dict[str, List[str]] = {
    "Operations": ["Business Operations", "Operations Manager", "Program Manager"],
    "Finance": ["Financial Analyst", "Finance Manager", "FP&A Analyst"],
    "Marketing": ["Marketing Manager", "Brand Manager", "Growth Marketing"],
    "Strategy": ["Strategy Manager", "Business Analyst", "Management Consultant"],
    "HR": ["HR Manager", "Talent Acquisition", "HR Business Partner"],
    "Sales": ["Sales Manager", "Business Development", "Account Manager"],
    "Consulting": ["Management Consultant", "Strategy Consultant", "Business Analyst"],
    "Product Management": ["Product Manager", "Associate Product Manager"],
    "General Management": ["General Manager", "Business Manager"]
}


def normalize_role(primary_role: str, role_family: str) -> List[str]:
    """
    Expand primary role into 3-5 realistic adjacent titles
    
    Args:
        primary_role: Primary role from resume
        role_family: Role family (Ops, Finance, etc.)
        
    Returns:
        List of 3-5 expanded role titles
    """
    # Try exact match first
    if primary_role in ROLE_EXPANSIONS:
        return ROLE_EXPANSIONS[primary_role]
    
    # Try role family defaults
    if role_family in ROLE_FAMILY_DEFAULTS:
        return ROLE_FAMILY_DEFAULTS[role_family]
    
    # Fallback to primary role only
    logger.warning(f"No expansion found for role: {primary_role}, family: {role_family}")
    return [primary_role]


def select_top_roles(
    expanded_roles: List[str],
    resume_experience: float,
    mba_patterns: Dict = None
) -> List[str]:
    """
    Select top 2 role titles that best match resume + MBA patterns
    
    Args:
        expanded_roles: List of expanded role titles
        resume_experience: Years of experience
        mba_patterns: Learned MBA patterns (optional)
        
    Returns:
        Top 2 role titles
    """
    if not expanded_roles:
        return []
    
    # If no patterns, return first 2
    if not mba_patterns:
        return expanded_roles[:2]
    
    # Score each role
    scored_roles = []
    for role in expanded_roles:
        score = 0
        
        # Check if common in MBA patterns
        common_titles = mba_patterns.get('common_titles', {})
        if role in common_titles:
            score += 5
        
        # Check if realistic for experience level
        if _is_realistic_for_experience(role, resume_experience):
            score += 3
        
        scored_roles.append((role, score))
    
    # Sort by score and return top 2
    scored_roles.sort(key=lambda x: x[1], reverse=True)
    return [role for role, score in scored_roles[:2]]


def _is_realistic_for_experience(role: str, years: float) -> bool:
    """
    Check if role is realistic for experience level
    
    Rules:
    - Manager roles: 2+ years
    - Lead roles: 3+ years
    - Analyst roles: 0+ years
    """
    role_lower = role.lower()
    
    # Senior/Lead roles need 3+ years
    if any(kw in role_lower for kw in ['lead', 'head', 'director', 'vp']):
        return years >= 3
    
    # Manager roles need 2+ years
    if 'manager' in role_lower:
        return years >= 2
    
    # Analyst/Associate roles are OK for all
    return True


def get_experience_bands(years: float) -> List[str]:
    """
    Convert exact years into soft experience bands
    
    Args:
        years: Years of experience
        
    Returns:
        List of 1-2 experience bands
    """
    if years < 1:
        return ["0-1 years", "Fresher"]
    elif years < 2:
        return ["0-2 years", "1-3 years"]
    elif years < 3:
        return ["1-3 years", "2-4 years"]
    elif years < 5:
        return ["2-4 years", "3-5 years"]
    elif years < 7:
        return ["4-7 years", "5-8 years"]
    else:
        return ["7+ years", "5-10 years"]


def normalize_location(
    preferred_locations: List[str],
    location_flexibility: str
) -> List[str]:
    """
    Normalize locations for search
    
    Args:
        preferred_locations: User's preferred locations
        location_flexibility: 'strict' or 'flexible'
        
    Returns:
        Normalized location list
    """
    normalized = []
    
    for loc in preferred_locations:
        loc_lower = loc.lower()
        
        # India cities
        if loc_lower in ['mumbai', 'bangalore', 'bengaluru', 'delhi', 'gurgaon', 
                         'gurugram', 'hyderabad', 'pune', 'chennai', 'kolkata', 
                         'ahmedabad', 'noida']:
            # Normalize city names
            if loc_lower in ['bengaluru', 'bangalore']:
                normalized.append('Bangalore')
            elif loc_lower in ['gurgaon', 'gurugram']:
                normalized.append('Gurgaon')
            else:
                normalized.append(loc.title())
        
        # UAE cities
        elif loc_lower in ['dubai', 'abu dhabi', 'sharjah', 'ajman']:
            normalized.append(loc.title())
        
        # Countries
        elif 'india' in loc_lower:
            if location_flexibility == 'flexible':
                normalized.append('PAN India')
            else:
                normalized.append('India')
        
        elif 'uae' in loc_lower:
            normalized.append('UAE')
        
        # Remote
        elif 'remote' in loc_lower:
            normalized.append('Remote')
    
    # Default to PAN India if nothing specified
    return normalized if normalized else ['PAN India']
