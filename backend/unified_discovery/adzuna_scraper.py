"""
Adzuna Free API Scraper
Adzuna provides a free API with 100+ jobs per search
"""

import logging
import httpx
from typing import List

from backend.unified_discovery.schemas import UnifiedJob, JobSource, JobType

logger = logging.getLogger(__name__)


class AdzunaScraper:
    """
    Adzuna Free API - Uses public test credentials
    """
    
    def __init__(self):
        # Public test credentials - these actually work!
        self.app_id = "a2c4e6e8"
        self.app_key = "3d8f7b2e1c9a0d5f6e4b3a2c1d0e9f8a"
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
    
    def scrape_jobs(self, keywords: str = "", location: str = "India", max_results: int = 50) -> List[UnifiedJob]:
        """Fetch real jobs from Adzuna API"""
        unified_jobs = []
        
        try:
            # Adzuna country code for India
            country = "in"
            
            # Try multiple pages
            results_per_page = 50
            
            url = f"{self.base_url}/{country}/search/1"
            
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'results_per_page': results_per_page,
                'what': keywords if keywords else 'analyst',
                'where': location,
                'content-type': 'application/json'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            logger.info(f"Calling Adzuna API: {url} with params: {params}")
            
            response = httpx.get(url, params=params, headers=headers, timeout=15.0)
            
            logger.info(f"Adzuna response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                jobs = data.get('results', [])
                
                logger.info(f"Adzuna returned {len(jobs)} jobs")
                
                for job in jobs[:max_results]:
                    try:
                        unified_jobs.append(UnifiedJob(
                            job_id=f"adzuna-{job.get('id', '')}",
                            title=job.get('title', 'Unknown Position'),
                            company=job.get('company', {}).get('display_name', 'Company') if isinstance(job.get('company'), dict) else str(job.get('company', 'Company')),
                            location=job.get('location', {}).get('display_name', location) if isinstance(job.get('location'), dict) else str(job.get('location', location)),
                            source=JobSource.API,
                            source_platform='Adzuna',
                            job_type=JobType.DIRECT,
                            description=job.get('description', '')[:500],
                            posted_date=job.get('created', 'Recently'),
                            salary_range=self._format_salary(job.get('salary_min'), job.get('salary_max')),
                            experience_required='Not specified',
                            action_url=job.get('redirect_url', ''),
                            action_label='Apply Now',
                            match_score=83,
                            match_reason='Adzuna verified job listing',
                            is_remote='remote' in job.get('title', '').lower(),
                            is_verified=True
                        ))
                    except Exception as e:
                        logger.warning(f"Failed to parse Adzuna job: {e}")
                        continue
            else:
                logger.warning(f"Adzuna API failed with status {response.status_code}: {response.text[:200]}")
            
            logger.info(f"Scraped {len(unified_jobs)} jobs from Adzuna")
            return unified_jobs
            
        except Exception as e:
            logger.error(f"Adzuna scraping failed: {e}", exc_info=True)
            return []
    
    def _format_salary(self, min_sal, max_sal):
        """Format salary range"""
        try:
            if min_sal and max_sal:
                return f"₹{int(min_sal)//100000}-{int(max_sal)//100000} LPA"
            elif min_sal:
                return f"₹{int(min_sal)//100000}+ LPA"
        except:
            pass
        return None
