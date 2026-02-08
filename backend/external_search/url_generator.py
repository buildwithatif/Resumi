"""
URL Generator
Generates portal-specific search URLs for Naukri and Instahyre
"""

import logging
from typing import List, Dict
from urllib.parse import quote_plus

from backend.external_search.schemas import ExternalSearchRecommendation, SearchPlatform

logger = logging.getLogger(__name__)


def generate_naukri_urls(
    roles: List[str],
    experience_bands: List[str],
    locations: List[str]
) -> List[Dict]:
    """
    Generate 2-3 Naukri search URLs
    
    Strategy:
    1. Exact match: Best role + exact location
    2. Flexible location: Best role + PAN India
    3. Adjacent role: Second role + exact location
    
    Args:
        roles: Top 2 role titles
        experience_bands: Experience bands (e.g., ["2-4 years"])
        locations: Normalized locations
        
    Returns:
        List of URL data dictionaries
    """
    urls = []
    
    if not roles or not experience_bands or not locations:
        return urls
    
    primary_role = roles[0]
    primary_exp = experience_bands[0]
    primary_location = locations[0]
    
    # URL 1: Exact match (primary role + primary location)
    if primary_location != 'PAN India' and primary_location != 'Remote':
        search_keywords = quote_plus(primary_role)
        location_slug = primary_location.lower().replace(' ', '-')
        
        urls.append({
            'url': f"https://www.naukri.com/{primary_role.lower().replace(' ', '-')}-jobs-in-{location_slug}?k={search_keywords}&experience={quote_plus(primary_exp)}",
            'role_focus': primary_role,
            'location_focus': primary_location,
            'experience_band': primary_exp,
            'url_type': 'exact_match'
        })
    
    # URL 2: Flexible location (primary role + PAN India)
    if len(locations) > 1 or primary_location == 'PAN India':
        search_keywords = quote_plus(primary_role)
        
        urls.append({
            'url': f"https://www.naukri.com/{primary_role.lower().replace(' ', '-')}-jobs?k={search_keywords}&experience={quote_plus(primary_exp)}",
            'role_focus': primary_role,
            'location_focus': 'PAN India',
            'experience_band': primary_exp,
            'url_type': 'flexible_location'
        })
    
    # URL 3: Adjacent role (second role + primary location)
    if len(roles) > 1:
        adjacent_role = roles[1]
        search_keywords = quote_plus(adjacent_role)
        
        if primary_location != 'PAN India' and primary_location != 'Remote':
            location_slug = primary_location.lower().replace(' ', '-')
            urls.append({
                'url': f"https://www.naukri.com/{adjacent_role.lower().replace(' ', '-')}-jobs-in-{location_slug}?k={search_keywords}&experience={quote_plus(primary_exp)}",
                'role_focus': adjacent_role,
                'location_focus': primary_location,
                'experience_band': primary_exp,
                'url_type': 'adjacent_role'
            })
        else:
            urls.append({
                'url': f"https://www.naukri.com/{adjacent_role.lower().replace(' ', '-')}-jobs?k={search_keywords}&experience={quote_plus(primary_exp)}",
                'role_focus': adjacent_role,
                'location_focus': 'PAN India',
                'experience_band': primary_exp,
                'url_type': 'adjacent_role'
            })
    
    return urls[:3]  # Max 3 URLs


def generate_instahyre_urls(
    roles: List[str],
    experience_bands: List[str],
    locations: List[str]
) -> List[Dict]:
    """
    Generate 1-2 Instahyre search URLs
    
    Strategy:
    - Cleaner role titles
    - Less keyword density
    - Focus on role + location + experience
    
    Args:
        roles: Top 2 role titles
        experience_bands: Experience bands
        locations: Normalized locations
        
    Returns:
        List of URL data dictionaries
    """
    urls = []
    
    if not roles or not experience_bands or not locations:
        return urls
    
    primary_role = roles[0]
    primary_exp = experience_bands[0]
    primary_location = locations[0]
    
    # URL 1: Primary role + location
    if primary_location != 'PAN India' and primary_location != 'Remote':
        search_query = quote_plus(primary_role)
        location_query = quote_plus(primary_location)
        
        urls.append({
            'url': f"https://www.instahyre.com/search-jobs/?q={search_query}&l={location_query}&exp={quote_plus(primary_exp)}",
            'role_focus': primary_role,
            'location_focus': primary_location,
            'experience_band': primary_exp,
            'url_type': 'exact_match'
        })
    
    # URL 2: Flexible location (if applicable)
    if len(locations) > 1 or primary_location == 'PAN India':
        search_query = quote_plus(primary_role)
        
        urls.append({
            'url': f"https://www.instahyre.com/search-jobs/?q={search_query}&exp={quote_plus(primary_exp)}",
            'role_focus': primary_role,
            'location_focus': 'All Locations',
            'experience_band': primary_exp,
            'url_type': 'flexible_location'
        })
    
    return urls[:2]  # Max 2 URLs


def rank_urls(urls: List[Dict], user_preferences: Dict) -> List[Dict]:
    """
    Rank URLs by relevance
    
    Scoring:
    - Exact location match: +5
    - Primary role: +5
    - Flexible location: +3
    - Adjacent role: +2
    
    Args:
        urls: List of URL data dictionaries
        user_preferences: User's preferences
        
    Returns:
        Ranked and filtered URLs (score >= 5)
    """
    for url_data in urls:
        score = 0
        
        # Exact location match
        if url_data['location_focus'] in user_preferences.get('preferred_locations', []):
            score += 5
        
        # Primary role match
        if url_data['role_focus'] in user_preferences.get('primary_roles', []):
            score += 5
        
        # Flexible location bonus
        if url_data['location_focus'] in ['PAN India', 'All Locations']:
            score += 3
        
        # URL type bonuses
        if url_data['url_type'] == 'exact_match':
            score += 2
        elif url_data['url_type'] == 'adjacent_role':
            score += 1
        
        url_data['relevance_score'] = score
    
    # Sort by score (descending)
    urls.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    # Filter low-confidence URLs (score < 5)
    return [url for url in urls if url['relevance_score'] >= 5]


def generate_explanation(url_data: Dict, resume_data: Dict) -> str:
    """
    Generate human-readable explanation for why this search was generated
    
    Args:
        url_data: URL data dictionary
        resume_data: Resume intelligence data
        
    Returns:
        1-2 line explanation
    """
    templates = {
        'exact_match': "Based on your {role} experience and {location} preference.",
        'flexible_location': "Expanded to {location} to find more {role} opportunities.",
        'adjacent_role': "Includes {role} roles common in MBA hiring for {exp} profiles.",
        'mba_pattern': "Generated based on common MBA hiring patterns for {role} roles."
    }
    
    # Select template based on URL type
    url_type = url_data.get('url_type', 'exact_match')
    template = templates.get(url_type, templates['exact_match'])
    
    # Format explanation
    explanation = template.format(
        role=url_data['role_focus'],
        location=url_data['location_focus'],
        exp=url_data['experience_band']
    )
    
    return explanation
