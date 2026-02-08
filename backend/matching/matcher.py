"""
Job Matcher
Filters, scores, and ranks jobs against user profile
"""

import logging
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

from backend.job_normalization.normalizer import NormalizedJob
from backend.profile_extraction.schemas import ProfileSchema, UserPreferences
from backend.location_logic.normalizer import score_location_match, NormalizedLocation

logger = logging.getLogger(__name__)


@dataclass
class JobMatch:
    """Job with match score and breakdown"""
    job: NormalizedJob
    total_score: float
    location_score: float
    skill_score: float
    career_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            'job': self.job.to_dict(),
            'match_score': round(self.total_score, 2),
            'score_breakdown': {
                'location': round(self.location_score, 2),
                'skill': round(self.skill_score, 2),
                'career': round(self.career_score, 2),
            }
        }


def match_jobs(
    jobs: List[NormalizedJob],
    profile: ProfileSchema,
    preferences: UserPreferences,
    max_results: int = 20
) -> List[JobMatch]:
    """
    Match and rank jobs against user profile
    
    Args:
        jobs: List of normalized jobs
        profile: User profile
        preferences: User preferences
        max_results: Maximum number of results to return
        
    Returns:
        List of top matched jobs with scores
    """
    logger.info(f"Matching {len(jobs)} jobs against profile...")
    
    # Apply hard filters
    filtered_jobs = _apply_hard_filters(jobs, preferences)
    logger.info(f"After hard filters: {len(filtered_jobs)} jobs")
    
    # Score each job
    scored_jobs = []
    for job in filtered_jobs:
        match = _score_job(job, profile, preferences)
        if match and match.total_score >= 0.3:  # Minimum threshold
            scored_jobs.append(match)
    
    # Sort by total score
    scored_jobs.sort(key=lambda x: x.total_score, reverse=True)
    
    logger.info(f"Matched {len(scored_jobs)} jobs above threshold")
    
    return scored_jobs[:max_results]


def _apply_hard_filters(
    jobs: List[NormalizedJob],
    preferences: UserPreferences
) -> List[NormalizedJob]:
    """Apply hard filters to jobs"""
    filtered = []
    
    for job in jobs:
        # Remote-only filter
        if preferences.remote_only and job.location['type'] != 'remote':
            continue
        
        # Add more hard filters here as needed
        
        filtered.append(job)
    
    return filtered


def _score_job(
    job: NormalizedJob,
    profile: ProfileSchema,
    preferences: UserPreferences
) -> JobMatch:
    """Score a single job against profile"""
    
    # Location score
    job_location = NormalizedLocation(
        city=job.location.get('city'),
        country=job.location.get('country'),
        location_type=job.location.get('type', 'onsite'),
        raw=job.location.get('raw', '')
    )
    
    location_score = score_location_match(
        job_location,
        preferences.preferred_locations,
        preferences.open_to_relocation,
        preferences.open_to_international,
        preferences.remote_only
    )
    
    # Skill score
    skill_score = _calculate_skill_similarity(
        profile.skills + profile.tools,
        job.required_skills
    )
    
    # Career score
    career_score = _calculate_career_fit(
        profile.seniority,
        profile.primary_role,
        job.title
    )
    
    # Domain fit score (NEW for V2 - prioritize MBA/non-tech roles)
    domain_score = _calculate_domain_fit(
        profile.primary_role,
        job.title,
        job.description
    )
    
    # Weighted total score
    # For non-tech roles, prioritize skill match and domain fit over location
    is_business_role = profile.primary_role in ['strategy', 'consulting', 'operations', 
                                                 'marketing', 'sales', 'finance', 'hr']
    
    if is_business_role:
        # Business roles: Skills and domain fit matter more
        total_score = (
            0.3 * location_score +
            0.4 * skill_score +
            0.2 * career_score +
            0.1 * domain_score
        )
    else:
        # Tech roles: Original weighting
        total_score = (
            0.5 * location_score +
            0.4 * skill_score +
            0.1 * career_score
        )
    
    return JobMatch(
        job=job,
        total_score=total_score,
        location_score=location_score,
        skill_score=skill_score,
        career_score=career_score
    )


def _calculate_skill_similarity(user_skills: List[str], job_skills: List[str]) -> float:
    """Calculate skill overlap using Jaccard similarity"""
    if not user_skills or not job_skills:
        return 0.0
    
    user_set = set(s.lower() for s in user_skills)
    job_set = set(s.lower() for s in job_skills)
    
    intersection = len(user_set & job_set)
    union = len(user_set | job_set)
    
    if union == 0:
        return 0.0
    
    jaccard = intersection / union
    
    # Boost score if many skills match
    if intersection >= 5:
        jaccard = min(1.0, jaccard * 1.2)
    
    return jaccard


def _calculate_career_fit(
    user_seniority: str,
    user_role: str,
    job_title: str
) -> float:
    """Calculate career progression fit"""
    job_title_lower = job_title.lower()
    
    # Seniority mapping
    seniority_levels = {
        'junior': 1,
        'mid': 2,
        'senior': 3,
        'lead': 4,
        'principal': 5
    }
    
    user_level = seniority_levels.get(user_seniority, 2)
    
    # Detect job seniority from title
    job_level = 2  # Default to mid
    if any(word in job_title_lower for word in ['junior', 'entry', 'associate']):
        job_level = 1
    elif any(word in job_title_lower for word in ['senior', 'sr']):
        job_level = 3
    elif any(word in job_title_lower for word in ['lead', 'staff', 'principal']):
        job_level = 4
    
    # Score based on career progression
    level_diff = job_level - user_level
    
    if level_diff == 0:
        # Lateral move
        return 0.7
    elif level_diff == 1:
        # Promotion
        return 0.9
    elif level_diff == -1:
        # Slight downgrade
        return 0.4
    elif level_diff >= 2:
        # Big jump (might be too ambitious)
        return 0.6
    else:
        # Downgrade
        return 0.2


def _calculate_domain_fit(
    user_role: str,
    job_title: str,
    job_description: str
) -> float:
    """
    Calculate domain fit score (V2 - prioritize MBA/non-tech roles)
    
    Args:
        user_role: User's primary role family
        job_title: Job title
        job_description: Job description
        
    Returns:
        Domain fit score (0.0 to 1.0)
    """
    job_text = (job_title + ' ' + job_description).lower()
    
    # Role family keywords
    role_keywords = {
        'strategy': ['strategy', 'strategic', 'business strategy', 'corporate strategy'],
        'consulting': ['consultant', 'consulting', 'advisory', 'advisory services'],
        'operations': ['operations', 'ops', 'supply chain', 'logistics', 'process'],
        'marketing': ['marketing', 'brand', 'digital marketing', 'growth', 'demand gen'],
        'sales': ['sales', 'business development', 'account', 'revenue'],
        'finance': ['finance', 'financial', 'fp&a', 'investment', 'accounting'],
        'hr': ['hr', 'human resources', 'talent', 'people', 'recruiting'],
    }
    
    # Check if job matches user's role family
    user_keywords = role_keywords.get(user_role, [])
    if not user_keywords:
        return 0.5  # Neutral if unknown role
    
    # Count keyword matches
    matches = sum(1 for keyword in user_keywords if keyword in job_text)
    
    if matches >= 2:
        return 1.0  # Strong domain fit
    elif matches == 1:
        return 0.7  # Moderate domain fit
    else:
        return 0.3  # Weak domain fit
