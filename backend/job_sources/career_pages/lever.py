"""
Lever Job Collector
Collects jobs from Lever public APIs
"""

from typing import List, Dict, Any
import logging
from backend.job_sources.base_collector import BaseJobCollector

logger = logging.getLogger(__name__)


# List of companies with public Lever boards
LEVER_COMPANIES = [
    # US Tech
    'netflix', 'shopify', 'grammarly', 'canva', 'elastic',
    'hubspot', 'twilio', 'segment', 'miro', 'zapier',
    'asana', 'atlassian', 'zendesk', 'dropbox', 'square',
    
    # India (V2 Priority)
    'ola', 'flipkart', 'paytm',
]


class LeverCollector(BaseJobCollector):
    """Collects jobs from Lever career pages"""
    
    def __init__(self):
        super().__init__('lever', rate_limit=60)
    
    async def collect_jobs(self, max_jobs: int = 100) -> List[Dict[str, Any]]:
        """
        Collect jobs from Lever boards
        
        Args:
            max_jobs: Maximum number of jobs to collect
            
        Returns:
            List of raw job dictionaries
        """
        all_jobs = []
        
        for company in LEVER_COMPANIES:
            if len(all_jobs) >= max_jobs:
                break
            
            try:
                jobs = await self._fetch_company_jobs(company)
                all_jobs.extend(jobs)
                logger.info(f"Collected {len(jobs)} jobs from {company} (Lever)")
            except Exception as e:
                logger.error(f"Failed to collect jobs from {company}: {e}")
                continue
        
        return all_jobs[:max_jobs]
    
    async def _fetch_company_jobs(self, company: str) -> List[Dict[str, Any]]:
        """Fetch jobs for a specific company"""
        url = f"https://api.lever.co/v0/postings/{company}"
        
        data = await self.fetch_url(url)
        if not data or not isinstance(data, list):
            return []
        
        jobs = []
        for job in data:
            normalized = self._normalize_lever_job(job, company)
            if normalized:
                jobs.append(normalized)
        
        return jobs
    
    def _normalize_lever_job(self, job: Dict[str, Any], company: str) -> Dict[str, Any]:
        """Normalize Lever job format"""
        try:
            # Extract location
            categories = job.get('categories', {})
            location = categories.get('location', 'Not specified') if isinstance(categories, dict) else 'Not specified'
            
            # Extract commitment (employment type)
            commitment = categories.get('commitment', 'Full-time') if isinstance(categories, dict) else 'Full-time'
            
            return {
                'source': self.source_name,
                'source_id': job.get('id', ''),
                'title': job.get('text', 'Unknown'),
                'company': company.title(),
                'location_raw': location,
                'description': job.get('description', '') + '\n' + job.get('descriptionPlain', ''),
                'apply_url': job.get('hostedUrl', ''),
                'departments': [categories.get('team', '')] if categories.get('team') else [],
                'employment_type': commitment.lower(),
                'raw_data': job,
            }
        except Exception as e:
            logger.warning(f"Failed to normalize Lever job: {e}")
            return None
