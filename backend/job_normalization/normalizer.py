"""
Job Normalizer
Standardizes and deduplicates job data
"""

import hashlib
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import json
from pathlib import Path
from datetime import datetime

from backend.location_logic.normalizer import normalize_location, NormalizedLocation
from backend.profile_extraction.extractor import extract_skills

logger = logging.getLogger(__name__)


@dataclass
class NormalizedJob:
    """Standardized job schema"""
    id: str
    title: str
    company: str
    location: Dict[str, Any]  # NormalizedLocation as dict
    source: str
    apply_url: str
    description: str
    required_skills: List[str]
    preferred_skills: List[str]
    employment_type: str
    departments: List[str]
    raw_data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


def normalize_job(raw_job: Dict[str, Any]) -> Optional[NormalizedJob]:
    """
    Normalize raw job data to standard schema
    
    Args:
        raw_job: Raw job dictionary from collector
        
    Returns:
        NormalizedJob or None if normalization fails
    """
    try:
        # Generate unique ID
        job_id = _generate_job_id(
            raw_job.get('title', ''),
            raw_job.get('company', ''),
            raw_job.get('location_raw', '')
        )
        
        # Normalize location
        location_raw = raw_job.get('location_raw', '')
        location = normalize_location(location_raw)
        
        # Extract skills from description
        description = raw_job.get('description', '')
        skills = extract_skills(description)
        
        # Split into required and preferred (for V1, just put all in required)
        required_skills = skills[:10]  # Limit to top 10
        preferred_skills = []
        
        return NormalizedJob(
            id=job_id,
            title=raw_job.get('title', 'Unknown'),
            company=raw_job.get('company', 'Unknown'),
            location={
                'city': location.city,
                'country': location.country,
                'type': location.location_type,
                'raw': location.raw
            },
            source=raw_job.get('source', 'unknown'),
            apply_url=raw_job.get('apply_url', ''),
            description=description[:1000],  # Truncate long descriptions
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            employment_type=raw_job.get('employment_type', 'full-time'),
            departments=raw_job.get('departments', []),
            raw_data=raw_job
        )
        
    except Exception as e:
        logger.warning(f"Failed to normalize job: {e}")
        return None


def _generate_job_id(title: str, company: str, location: str) -> str:
    """Generate unique job ID from key fields"""
    combined = f"{title}|{company}|{location}".lower()
    return hashlib.md5(combined.encode()).hexdigest()[:16]


def deduplicate_jobs(jobs: List[NormalizedJob]) -> List[NormalizedJob]:
    """
    Remove duplicate jobs based on ID
    
    Args:
        jobs: List of normalized jobs
        
    Returns:
        Deduplicated list
    """
    seen_ids = set()
    unique_jobs = []
    
    for job in jobs:
        if job.id not in seen_ids:
            seen_ids.add(job.id)
            unique_jobs.append(job)
        else:
            logger.debug(f"Duplicate job found: {job.title} at {job.company}")
    
    logger.info(f"Deduplicated {len(jobs)} jobs to {len(unique_jobs)} unique jobs")
    return unique_jobs


def save_normalized_jobs(jobs: List[NormalizedJob], data_dir: Path):
    """Save normalized jobs to JSON file"""
    normalized_dir = Path(data_dir) / 'jobs_normalized'
    normalized_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = normalized_dir / f"jobs_normalized_{timestamp}.json"
    
    jobs_data = [job.to_dict() for job in jobs]
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(jobs_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved {len(jobs)} normalized jobs to {filename}")


def load_latest_normalized_jobs(data_dir: Path) -> List[NormalizedJob]:
    """Load most recent normalized jobs file"""
    normalized_dir = Path(data_dir) / 'jobs_normalized'
    
    if not normalized_dir.exists():
        return []
    
    job_files = sorted(normalized_dir.glob('jobs_normalized_*.json'), reverse=True)
    
    if not job_files:
        logger.warning("No normalized job files found")
        return []
    
    latest_file = job_files[0]
    with open(latest_file, 'r', encoding='utf-8') as f:
        jobs_data = json.load(f)
    
    jobs = []
    for job_dict in jobs_data:
        # Reconstruct NormalizedJob from dict
        jobs.append(NormalizedJob(**job_dict))
    
    logger.info(f"Loaded {len(jobs)} normalized jobs from {latest_file}")
    return jobs
