"""
Explanation Generator
Generates human-readable explanations for job matches
"""

import logging
from typing import Dict, Any, List

from backend.matching.matcher import JobMatch
from backend.profile_extraction.schemas import ProfileSchema

logger = logging.getLogger(__name__)


def generate_explanation(
    match: JobMatch,
    profile: ProfileSchema
) -> Dict[str, Any]:
    """
    Generate explanation for why a job matches the profile
    
    Args:
        match: JobMatch object with scores
        profile: User profile
        
    Returns:
        Dictionary with explanation components
    """
    job = match.job
    
    # Why it matches
    why_match = _generate_why_match(match, profile)
    
    # Skill matches
    skill_matches = _find_skill_matches(profile.skills + profile.tools, job.required_skills)
    
    # Skill gaps
    skill_gaps = _find_skill_gaps(profile.skills + profile.tools, job.required_skills)
    
    # Location reasoning
    location_reasoning = _generate_location_reasoning(match, job)
    
    # Only return if we have meaningful content
    if not why_match or not skill_matches:
        return None
    
    return {
        'why_match': why_match,
        'skill_matches': skill_matches[:8],  # Top 8
        'skill_gaps': skill_gaps[:5],  # Top 5 gaps
        'location_reasoning': location_reasoning
    }


def _generate_why_match(match: JobMatch, profile: ProfileSchema) -> str:
    """Generate high-level match reasoning"""
    job = match.job
    
    reasons = []
    
    # Skill-based reasoning
    if match.skill_score >= 0.6:
        reasons.append(f"Strong alignment with your {profile.primary_role} background")
    elif match.skill_score >= 0.4:
        reasons.append(f"Good fit for your {profile.primary_role} experience")
    
    # Career progression
    if match.career_score >= 0.8:
        reasons.append("Excellent career progression opportunity")
    elif match.career_score >= 0.6:
        reasons.append("Aligns with your career level")
    
    # Location
    if match.location_score >= 0.9:
        reasons.append("Perfect location match")
    elif match.location_score >= 0.7:
        reasons.append("Good location fit")
    
    # Skill clusters
    if profile.skill_clusters:
        cluster_match = any(cluster in job.title.lower() or cluster in job.description.lower() 
                          for cluster in profile.skill_clusters)
        if cluster_match:
            reasons.append(f"Matches your expertise in {', '.join(profile.skill_clusters[:2])}")
    
    if not reasons:
        reasons.append("Potential fit based on your background")
    
    return '. '.join(reasons) + '.'


def _find_skill_matches(user_skills: List[str], job_skills: List[str]) -> List[str]:
    """Find overlapping skills"""
    user_set = set(s.lower() for s in user_skills)
    job_set = set(s.lower() for s in job_skills)
    
    matches = user_set & job_set
    
    # Return in original case from user skills
    result = []
    for skill in user_skills:
        if skill.lower() in matches:
            result.append(skill)
    
    return result


def _find_skill_gaps(user_skills: List[str], job_skills: List[str]) -> List[str]:
    """Find skills required by job but not in user profile"""
    user_set = set(s.lower() for s in user_skills)
    job_set = set(s.lower() for s in job_skills)
    
    gaps = job_set - user_set
    
    # Return in original case from job skills
    result = []
    for skill in job_skills:
        if skill.lower() in gaps:
            result.append(skill)
    
    return result


def _generate_location_reasoning(match: JobMatch, job) -> str:
    """Generate location-specific reasoning"""
    location = job.location
    
    if location['type'] == 'remote':
        return "Remote position - work from anywhere"
    
    if match.location_score >= 0.9:
        return f"Located in your preferred area: {location['raw']}"
    elif match.location_score >= 0.7:
        return f"Same country as your preference: {location['country']}"
    elif match.location_score >= 0.5:
        return f"Relocation opportunity to {location['raw']}"
    else:
        return f"Location: {location['raw']}"
