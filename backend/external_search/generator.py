"""
External Search Generator
Main orchestrator for generating external search recommendations
"""

import logging
from typing import List

from backend.external_search.schemas import (
    SearchGenerationRequest,
    SearchGenerationResponse,
    ExternalSearchRecommendation,
    SearchPlatform
)
from backend.external_search.role_normalizer import (
    normalize_role,
    select_top_roles,
    get_experience_bands,
    normalize_location
)
from backend.external_search.url_generator import (
    generate_naukri_urls,
    generate_instahyre_urls,
    rank_urls,
    generate_explanation
)

logger = logging.getLogger(__name__)


def generate_external_searches(request: SearchGenerationRequest) -> SearchGenerationResponse:
    """
    Generate external search URL recommendations
    
    Main orchestration function that:
    1. Normalizes roles
    2. Selects top roles
    3. Generates experience bands
    4. Normalizes locations
    5. Generates portal-specific URLs
    6. Ranks URLs
    7. Generates explanations
    
    Args:
        request: SearchGenerationRequest with resume intelligence and preferences
        
    Returns:
        SearchGenerationResponse with Naukri and Instahyre URLs
    """
    logger.info(f"Generating external searches for roles: {request.primary_roles}")
    
    # STEP 1: Role Normalization
    primary_role = request.primary_roles[0] if request.primary_roles else "Business Analyst"
    expanded_roles = normalize_role(primary_role, request.role_family)
    
    logger.info(f"Expanded {primary_role} to {len(expanded_roles)} roles: {expanded_roles}")
    
    # STEP 2: Role Selection
    # TODO: Load MBA patterns from learned data
    mba_patterns = {}  # Placeholder
    top_roles = select_top_roles(expanded_roles, request.years_of_experience, mba_patterns)
    
    if not top_roles:
        top_roles = expanded_roles[:2]  # Fallback
    
    logger.info(f"Selected top roles: {top_roles}")
    
    # STEP 3: Experience Banding
    experience_bands = get_experience_bands(request.years_of_experience)
    logger.info(f"Experience bands: {experience_bands}")
    
    # STEP 4: Location Handling
    locations = normalize_location(
        request.preferred_locations,
        request.location_flexibility
    )
    logger.info(f"Normalized locations: {locations}")
    
    # STEP 5 & 6: Generate Portal-Specific URLs
    
    # Naukri URLs
    naukri_url_data = generate_naukri_urls(top_roles, experience_bands, locations)
    logger.info(f"Generated {len(naukri_url_data)} Naukri URLs")
    
    # Instahyre URLs
    instahyre_url_data = generate_instahyre_urls(top_roles, experience_bands, locations)
    logger.info(f"Generated {len(instahyre_url_data)} Instahyre URLs")
    
    # STEP 7: Ranking
    user_prefs = {
        'preferred_locations': request.preferred_locations,
        'primary_roles': request.primary_roles
    }
    
    naukri_url_data = rank_urls(naukri_url_data, user_prefs)
    instahyre_url_data = rank_urls(instahyre_url_data, user_prefs)
    
    # STEP 8: Generate Explanations & Create Recommendations
    resume_data = {
        'primary_role': primary_role,
        'years_of_experience': request.years_of_experience
    }
    
    naukri_recommendations = []
    for url_data in naukri_url_data:
        explanation = generate_explanation(url_data, resume_data)
        
        naukri_recommendations.append(ExternalSearchRecommendation(
            platform=SearchPlatform.NAUKRI,
            role_focus=url_data['role_focus'],
            location_focus=url_data['location_focus'],
            experience_band=url_data['experience_band'],
            search_url=url_data['url'],
            why_this_search=explanation,
            relevance_score=url_data['relevance_score']
        ))
    
    instahyre_recommendations = []
    for url_data in instahyre_url_data:
        explanation = generate_explanation(url_data, resume_data)
        
        instahyre_recommendations.append(ExternalSearchRecommendation(
            platform=SearchPlatform.INSTAHYRE,
            role_focus=url_data['role_focus'],
            location_focus=url_data['location_focus'],
            experience_band=url_data['experience_band'],
            search_url=url_data['url'],
            why_this_search=explanation,
            relevance_score=url_data['relevance_score']
        ))
    
    # Create response
    response = SearchGenerationResponse(
        naukri_searches=naukri_recommendations,
        instahyre_searches=instahyre_recommendations,
        total_recommendations=len(naukri_recommendations) + len(instahyre_recommendations),
        generation_metadata={
            'expanded_roles': expanded_roles,
            'top_roles': top_roles,
            'experience_bands': experience_bands,
            'normalized_locations': locations
        }
    )
    
    logger.info(f"Generated {response.total_recommendations} total search recommendations")
    
    return response
