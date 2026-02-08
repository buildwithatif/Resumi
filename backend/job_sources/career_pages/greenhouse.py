"""
Greenhouse Job Collector
Collects jobs from Greenhouse public APIs
"""

from typing import List, Dict, Any
import logging
from backend.job_sources.base_collector import BaseJobCollector

logger = logging.getLogger(__name__)


# List of companies with public Greenhouse boards
GREENHOUSE_COMPANIES = [
    # US Tech
    'airbnb', 'stripe', 'doordash', 'robinhood', 'coinbase',
    'gitlab', 'databricks', 'figma', 'notion', 'airtable',
    'plaid', 'checkr', 'gusto', 'lattice', 'verkada',
    
    # India (V2 Priority - Non-tech friendly)
    'razorpay', 'swiggy', 'zomato', 'cred', 'meesho',
    
    # UAE (V2 Priority)
    'careem', 'noon',
]


class GreenhouseCollector(BaseJobCollector):
    """Collects jobs from Greenhouse career pages"""
    
    def __init__(self):
        super().__init__('greenhouse', rate_limit=60)
    
    async def collect_jobs(self, max_jobs: int = 100) -> List[Dict[str, Any]]:
        """
        Collect jobs from Greenhouse boards
        
        Args:
            max_jobs: Maximum number of jobs to collect
            
        Returns:
            List of raw job dictionaries
        """
        all_jobs = []
        
        for company in GREENHOUSE_COMPANIES:
            if len(all_jobs) >= max_jobs:
                break
            
            try:
                jobs = await self._fetch_company_jobs(company)
                all_jobs.extend(jobs)
                logger.info(f"Collected {len(jobs)} jobs from {company} (Greenhouse)")
            except Exception as e:
                logger.error(f"Failed to collect jobs from {company}: {e}")
                continue
        
        return all_jobs[:max_jobs]
    
    async def _fetch_company_jobs(self, company: str) -> List[Dict[str, Any]]:
        """Fetch jobs for a specific company"""
        url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
        
        data = await self.fetch_url(url)
        if not data or 'jobs' not in data:
            return []
        
        jobs = []
        for job in data['jobs']:
            normalized = self._normalize_greenhouse_job(job, company)
            if normalized:
                jobs.append(normalized)
        
        return jobs
    
    def _normalize_greenhouse_job(self, job: Dict[str, Any], company: str) -> Dict[str, Any]:
        """Normalize Greenhouse job format"""
        try:
            # Extract location
            location = job.get('location', {})
            location_name = location.get('name', 'Not specified') if isinstance(location, dict) else str(location)
            
            return {
                'source': self.source_name,
                'source_id': str(job.get('id', '')),
                'title': job.get('title', 'Unknown'),
                'company': company.title(),
                'location_raw': location_name,
                'description': job.get('content', ''),
                'apply_url': job.get('absolute_url', ''),
                'departments': [dept.get('name', '') for dept in job.get('departments', [])],
                'employment_type': 'full-time',  # Greenhouse doesn't always specify
                'raw_data': job,
            }
        except Exception as e:
            logger.warning(f"Failed to normalize Greenhouse job: {e}")
            return None
