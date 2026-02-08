"""
RemoteOK Job Collector
Collects remote jobs from RemoteOK public API
"""

from typing import List, Dict, Any
import logging
from backend.job_sources.base_collector import BaseJobCollector

logger = logging.getLogger(__name__)


class RemoteOKCollector(BaseJobCollector):
    """Collects jobs from RemoteOK"""
    
    def __init__(self):
        super().__init__('remoteok', rate_limit=10)  # Lower rate limit
    
    async def collect_jobs(self, max_jobs: int = 100) -> List[Dict[str, Any]]:
        """
        Collect jobs from RemoteOK
        
        Args:
            max_jobs: Maximum number of jobs to collect
            
        Returns:
            List of raw job dictionaries
        """
        url = "https://remoteok.com/api"
        
        try:
            data = await self.fetch_url(url)
            if not data or not isinstance(data, list):
                logger.warning("No data returned from RemoteOK")
                return []
            
            # First item is metadata, skip it
            jobs_data = data[1:] if len(data) > 1 else []
            
            jobs = []
            for job in jobs_data[:max_jobs]:
                normalized = self._normalize_remoteok_job(job)
                if normalized:
                    jobs.append(normalized)
            
            logger.info(f"Collected {len(jobs)} jobs from RemoteOK")
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to collect jobs from RemoteOK: {e}")
            return []
    
    def _normalize_remoteok_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize RemoteOK job format"""
        try:
            return {
                'source': self.source_name,
                'source_id': str(job.get('id', '')),
                'title': job.get('position', 'Unknown'),
                'company': job.get('company', 'Unknown'),
                'location_raw': job.get('location', 'Remote'),
                'description': job.get('description', ''),
                'apply_url': job.get('url', ''),
                'departments': [job.get('tags', [''])[0]] if job.get('tags') else [],
                'employment_type': 'full-time',
                'tags': job.get('tags', []),
                'raw_data': job,
            }
        except Exception as e:
            logger.warning(f"Failed to normalize RemoteOK job: {e}")
            return None
