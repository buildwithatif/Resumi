"""
Location Normalizer
Handles location parsing and normalization
"""

import re
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class NormalizedLocation:
    """Normalized location data"""
    city: Optional[str]
    country: Optional[str]
    location_type: str  # 'remote', 'hybrid', 'onsite'
    raw: str


# Country mappings for common variations
COUNTRY_MAPPINGS = {
    # North America
    'usa': 'USA',
    'us': 'USA',
    'united states': 'USA',
    'canada': 'Canada',
    'ca': 'Canada',
    
    # Europe
    'uk': 'United Kingdom',
    'gb': 'United Kingdom',
    'united kingdom': 'United Kingdom',
    'germany': 'Germany',
    'france': 'France',
    
    # Asia-Pacific (V2 Priority)
    'india': 'India',
    'in': 'India',
    'uae': 'UAE',
    'united arab emirates': 'UAE',
    'dubai': 'UAE',  # Often used as country
    'singapore': 'Singapore',
    'sg': 'Singapore',
    'australia': 'Australia',
    'au': 'Australia',
}

# City aliases (common variations)
CITY_ALIASES = {
    'bengaluru': 'Bangalore',
    'bangalore': 'Bangalore',
    'bombay': 'Mumbai',
    'mumbai': 'Mumbai',
    'new delhi': 'Delhi',
    'delhi': 'Delhi',
    'gurugram': 'Gurgaon',
    'gurgaon': 'Gurgaon',
}

# Major cities (for better parsing)
MAJOR_CITIES = {
    # India
    'mumbai', 'bangalore', 'bengaluru', 'delhi', 'new delhi', 'gurgaon', 'gurugram',
    'hyderabad', 'pune', 'chennai', 'kolkata', 'ahmedabad', 'noida',
    
    # UAE
    'dubai', 'abu dhabi', 'sharjah', 'ajman',
    
    # Other major cities
    'singapore', 'london', 'new york', 'san francisco', 'seattle', 'boston',
}

# Remote keywords
REMOTE_KEYWORDS = ['remote', 'anywhere', 'worldwide', 'global', 'work from home', 'wfh']
HYBRID_KEYWORDS = ['hybrid', 'flexible', 'remote-friendly']


def normalize_location(location_str: str) -> NormalizedLocation:
    """
    Normalize location string to structured format
    
    Args:
        location_str: Raw location string
        
    Returns:
        NormalizedLocation object
    """
    if not location_str:
        return NormalizedLocation(
            city=None,
            country=None,
            location_type='onsite',
            raw='Not specified'
        )
    
    location_lower = location_str.lower().strip()
    
    # Check for remote
    if any(keyword in location_lower for keyword in REMOTE_KEYWORDS):
        return NormalizedLocation(
            city=None,
            country=None,
            location_type='remote',
            raw=location_str
        )
    
    # Check for hybrid
    if any(keyword in location_lower for keyword in HYBRID_KEYWORDS):
        location_type = 'hybrid'
    else:
        location_type = 'onsite'
    
    # Parse city and country
    city, country = _parse_city_country(location_str)
    
    return NormalizedLocation(
        city=city,
        country=country,
        location_type=location_type,
        raw=location_str
    )


def _parse_city_country(location_str: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse city and country from location string"""
    # Common patterns: "City, Country" or "City, State, Country"
    parts = [p.strip() for p in location_str.split(',')]
    
    if len(parts) == 0:
        return None, None
    elif len(parts) == 1:
        # Could be city or country - check aliases
        single = parts[0].lower()
        if single in CITY_ALIASES:
            return CITY_ALIASES[single], None
        return parts[0], None
    elif len(parts) == 2:
        # City, Country
        city = parts[0].lower()
        city = CITY_ALIASES.get(city, parts[0])  # Apply alias if exists
        country = _normalize_country(parts[1])
        return city, country
    else:
        # City, State, Country (or similar)
        city = parts[0].lower()
        city = CITY_ALIASES.get(city, parts[0])  # Apply alias if exists
        country = _normalize_country(parts[-1])
        return city, country


def _normalize_country(country_str: str) -> str:
    """Normalize country name"""
    country_lower = country_str.lower().strip()
    return COUNTRY_MAPPINGS.get(country_lower, country_str.title())


def score_location_match(
    job_location: NormalizedLocation,
    preferred_locations: list[str],
    open_to_relocation: bool = False,
    open_to_international: bool = False,
    remote_only: bool = False
) -> float:
    """
    Score how well a job location matches user preferences
    
    Args:
        job_location: Normalized job location
        preferred_locations: List of preferred location strings
        open_to_relocation: Whether user is open to relocation
        open_to_international: Whether user is open to international roles
        remote_only: Whether user only wants remote positions
        
    Returns:
        Score between 0.0 and 1.0
    """
    # Remote jobs always score high if user is open to them
    if job_location.location_type == 'remote':
        return 1.0
    
    # If user wants remote only, penalize non-remote
    if remote_only and job_location.location_type != 'remote':
        return 0.2
    
    # If no preferred locations specified, give neutral score
    if not preferred_locations:
        return 0.5
    
    # Normalize preferred locations
    normalized_prefs = [normalize_location(loc) for loc in preferred_locations]
    
    # Check for matches
    best_score = 0.0
    
    for pref in normalized_prefs:
        # Exact city match
        if job_location.city and pref.city and job_location.city.lower() == pref.city.lower():
            best_score = max(best_score, 1.0)
            continue
        
        # Same country
        if job_location.country and pref.country and job_location.country.lower() == pref.country.lower():
            best_score = max(best_score, 0.7)
            continue
    
    # If no match found but open to relocation
    if best_score == 0.0:
        if open_to_relocation:
            # Check if same country at least
            if job_location.country:
                for pref in normalized_prefs:
                    if pref.country and job_location.country.lower() == pref.country.lower():
                        best_score = max(best_score, 0.5)
                        break
            
            # International role
            if best_score == 0.0 and open_to_international:
                best_score = 0.4
            elif best_score == 0.0:
                best_score = 0.1
    
    return best_score
