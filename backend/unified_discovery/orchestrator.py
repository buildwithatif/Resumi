"""
Unified Job Discovery Orchestrator
Uses Reliable RSS Feeds
"""

import logging
from typing import List
import random

from backend.unified_discovery.schemas import (
    JobDiscoveryRequest,
    UnifiedJobResponse,
    UnifiedJob,
    JobSource,
    JobType
)
from backend.unified_discovery.rss_scrapers import (
    RemoteOKRSS,
    WeWorkRemotelyRSS,
    RemotiveRSS
)
from backend.external_search.generator import generate_external_searches
from backend.external_search.schemas import SearchGenerationRequest

logger = logging.getLogger(__name__)


def discover_all_jobs(request: JobDiscoveryRequest) -> UnifiedJobResponse:
    """
    Unified job discovery using RSS Feeds (Reliable, Real Data)
    """
    logger.info(f"Starting job discovery for roles: {request.primary_roles}")
    
    api_jobs = []
    search_recommendations = []
    
    # Get search parameters
    primary_role = request.primary_roles[0] if request.primary_roles else "Business Analyst"
    primary_location = request.preferred_locations[0] if request.preferred_locations else "Bangalore"
    
    logger.info(f"Searching for: {primary_role} in {primary_location}")
    
    # FETCH REAL RSS JOBS
    logger.info("=" * 50)
    logger.info("FETCHING REAL JOBS FROM RSS FEEDS")
    logger.info("=" * 50)
    
    try:
        # 1. RemoteOK
        r_jobs = RemoteOKRSS().scrape(limit=30)
        api_jobs.extend(r_jobs)
        
        # 2. WeWorkRemotely
        w_jobs = WeWorkRemotelyRSS().scrape(limit=40)
        api_jobs.extend(w_jobs)
        
        # 3. Remotive
        rm_jobs = RemotiveRSS().scrape(limit=30)
        api_jobs.extend(rm_jobs)
        
    except Exception as e:
        logger.error(f"RSS Scraping error: {e}")
        # Graceful degradation - empty list, relying on search URLs
    
    # Shuffle to mix sources
    random.shuffle(api_jobs)
    
    logger.info("=" * 50)
    logger.info(f"TOTAL RSS JOBS FETCHED: {len(api_jobs)}")
    logger.info("=" * 50)
    
    # Generate smart search URLs for Naukri/Instahyre
    logger.info("Generating smart search URLs...")
    search_request = SearchGenerationRequest(
        primary_roles=request.primary_roles,
        role_family=request.role_family,
        years_of_experience=request.years_of_experience,
        top_skills=request.top_skills,
        preferred_locations=request.preferred_locations,
        location_flexibility=request.location_flexibility
    )
    
    search_response = generate_external_searches(search_request)
    
    # Convert search URLs to UnifiedJob format
    for naukri_search in search_response.naukri_searches:
        search_recommendations.append(UnifiedJob(
            job_id=f"naukri_search_{naukri_search.role_focus}_{naukri_search.location_focus}".replace(" ", "_"),
            title=f"{naukri_search.role_focus} Jobs",
            company="Multiple Companies",
            location=naukri_search.location_focus,
            source=JobSource.SEARCH_URL,
            source_platform="Naukri",
            job_type=JobType.EXTERNAL,
            description=f"Search for {naukri_search.role_focus} positions on Naukri",
            experience_required=naukri_search.experience_band,
            action_url=naukri_search.search_url,
            action_label="Search on Naukri",
            match_score=naukri_search.relevance_score * 10,
            match_reason=naukri_search.why_this_search,
            is_verified=False
        ))
    
    for instahyre_search in search_response.instahyre_searches:
        search_recommendations.append(UnifiedJob(
            job_id=f"instahyre_search_{instahyre_search.role_focus}_{instahyre_search.location_focus}".replace(" ", "_"),
            title=f"{instahyre_search.role_focus} Jobs",
            company="Multiple Companies",
            location=instahyre_search.location_focus,
            source=JobSource.SEARCH_URL,
            source_platform="Instahyre",
            job_type=JobType.EXTERNAL,
            description=f"Search for {instahyre_search.role_focus} positions on Instahyre",
            experience_required=instahyre_search.experience_band,
            action_url=instahyre_search.search_url,
            action_label="Search on Instahyre",
            match_score=instahyre_search.relevance_score * 10,
            match_reason=instahyre_search.why_this_search,
            is_verified=False
        ))
    
    logger.info(f"Generated {len(search_recommendations)} search URLs")
    
    # Create unified response
    response = UnifiedJobResponse(
        api_jobs=api_jobs,
        search_recommendations=search_recommendations,
        total_api_jobs=len(api_jobs),
        total_search_urls=len(search_recommendations),
        total_results=len(api_jobs) + len(search_recommendations),
        search_metadata={
            'primary_role': primary_role,
            'primary_location': primary_location,
            'sources_used': ['RemoteOK(RSS)', 'WWR(RSS)', 'Remotive(RSS)', 'Naukri', 'Instahyre']
        }
    )
    
    logger.info(f"✓ Discovery complete: {response.total_results} total results")
    logger.info(f"  - API Jobs: {response.total_api_jobs}")
    logger.info(f"  - Search URLs: {response.total_search_urls}")
    
    return response
