"""
Strict location filtering for India/UAE preference
"""

from typing import List, Optional
from backend.location_logic.normalizer import NormalizedLocation, normalize_location


def filter_jobs_by_location(
    jobs: List[dict],
    user_countries: List[str],
    open_to_remote: bool = True
) -> List[dict]:
    """
    Strictly filter jobs by user's country preferences
    
    Args:
        jobs: List of job dictionaries
        user_countries: List of countries user is interested in (e.g., ['India', 'UAE'])
        open_to_remote: Whether user is open to remote positions
        
    Returns:
        Filtered list of jobs
    """
    filtered = []
    
    for job in jobs:
        location_raw = job.get('location_raw', '')
        normalized = normalize_location(location_raw)
        
        # Always include remote jobs if user is open to them
        if open_to_remote and normalized.location_type == 'remote':
            filtered.append(job)
            continue
        
        # Check if job country matches user preferences
        if normalized.country:
            if normalized.country in user_countries:
                filtered.append(job)
                continue
        
        # If no country specified but city is in user's preferred countries
        # (e.g., "Mumbai" without "India")
        if normalized.city and not normalized.country:
            # Check if city is in any of the user's preferred countries
            # This is a heuristic - in production, we'd have a city->country mapping
            city_lower = normalized.city.lower()
            
            india_cities = ['mumbai', 'bangalore', 'delhi', 'gurgaon', 'hyderabad', 
                          'pune', 'chennai', 'kolkata', 'ahmedabad', 'noida']
            uae_cities = ['dubai', 'abu dhabi', 'sharjah', 'ajman']
            
            if 'India' in user_countries and city_lower in india_cities:
                filtered.append(job)
            elif 'UAE' in user_countries and city_lower in uae_cities:
                filtered.append(job)
    
    return filtered


def get_location_preference_from_user(user_profile: dict) -> List[str]:
    """
    Extract location preferences from user profile
    
    Args:
        user_profile: User profile dictionary
        
    Returns:
        List of preferred countries
    """
    preferences = user_profile.get('preferences', {})
    
    # Check explicit country preferences
    countries = []
    
    # Parse preferred locations
    preferred_locations = preferences.get('preferred_locations', [])
    for loc in preferred_locations:
        normalized = normalize_location(loc)
        if normalized.country:
            if normalized.country not in countries:
                countries.append(normalized.country)
    
    # If no countries specified, default to India (for V2 target audience)
    if not countries:
        countries = ['India']
    
    return countries
