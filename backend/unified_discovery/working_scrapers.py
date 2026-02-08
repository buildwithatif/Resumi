"""
Working Job Scrapers - ONLY APIs that actually work
Tested and verified sources only
"""

import logging
import httpx
from typing import List
from datetime import datetime

from backend.unified_discovery.schemas import UnifiedJob, JobSource, JobType

logger = logging.getLogger(__name__)


class RemoteOKScraper:
    """RemoteOK - Public API, works reliably"""
    
    def __init__(self):
        self.base_url = "https://remoteok.com/api"
    
    def scrape_jobs(self, keywords: str = "", max_results: int = 20) -> List[UnifiedJob]:
        """Fetch jobs from RemoteOK"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = httpx.get(self.base_url, headers=headers, timeout=15.0)
            response.raise_for_status()
            
            jobs_data = response.json()[1:]  # Skip metadata
            unified_jobs = []
            
            for job in jobs_data:
                if len(unified_jobs) >= max_results:
                    break
                
                # Filter by keywords
                if keywords:
                    title = job.get('position', '').lower()
                    tags = ' '.join(job.get('tags', [])).lower()
                    if keywords.lower() not in title and keywords.lower() not in tags:
                        continue
                
                unified_jobs.append(UnifiedJob(
                    job_id=f"remoteok-{job.get('id', '')}",
                    title=job.get('position', 'Remote Position'),
                    company=job.get('company', 'Company'),
                    location='Remote',
                    source=JobSource.API,
                    source_platform='RemoteOK',
                    job_type=JobType.DIRECT,
                    description=job.get('description', '')[:500],
                    posted_date=self._format_date(job.get('date')),
                    salary_range=self._format_salary(job.get('salary_min'), job.get('salary_max')),
                    experience_required='Not specified',
                    action_url=job.get('url', f"https://remoteok.com/remote-jobs/{job.get('id')}"),
                    action_label='Apply on RemoteOK',
                    match_score=85,
                    match_reason='Remote opportunity',
                    is_remote=True,
                    is_verified=True
                ))
            
            logger.info(f"✓ RemoteOK: {len(unified_jobs)} jobs")
            return unified_jobs
            
        except Exception as e:
            logger.error(f"✗ RemoteOK FAILED: {e}")
            return []
    
    def _format_date(self, timestamp):
        if not timestamp:
            return 'Recently'
        try:
            dt = datetime.fromtimestamp(int(timestamp))
            days = (datetime.now() - dt).days
            if days == 0: return 'Today'
            if days == 1: return 'Yesterday'
            if days < 7: return f'{days} days ago'
            if days < 30: return f'{days // 7} weeks ago'
            return f'{days // 30} months ago'
        except:
            return 'Recently'
    
    def _format_salary(self, min_sal, max_sal):
        if min_sal and max_sal:
            return f"${min_sal//1000}k-${max_sal//1000}k"
        return None


class TheMuseScraper:
    """The Muse - Free API, no auth required"""
    
    def __init__(self):
        self.base_url = "https://www.themuse.com/api/public/jobs"
    
    def scrape_jobs(self, keywords: str = "", location: str = "", max_results: int = 50) -> List[UnifiedJob]:
        """Fetch jobs from The Muse"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            params = {
                'page': 0,
                'descending': 'true',
                'api_key': 'public'
            }
            
            if keywords:
                params['category'] = 'Business & Strategy'
            
            response = httpx.get(self.base_url, params=params, headers=headers, timeout=15.0)
            response.raise_for_status()
            
            data = response.json()
            jobs = data.get('results', [])
            
            unified_jobs = []
            
            for job in jobs[:max_results]:
                # Filter by keywords
                if keywords:
                    title = job.get('name', '').lower()
                    if keywords.lower() not in title:
                        continue
                
                locations = job.get('locations', [])
                location_str = locations[0].get('name', 'Remote') if locations else 'Remote'
                
                unified_jobs.append(UnifiedJob(
                    job_id=f"themuse-{job.get('id', '')}",
                    title=job.get('name', 'Position'),
                    company=job.get('company', {}).get('name', 'Company'),
                    location=location_str,
                    source=JobSource.API,
                    source_platform='The Muse',
                    job_type=JobType.DIRECT,
                    description=job.get('contents', '')[:500],
                    posted_date=job.get('publication_date', 'Recently')[:10],
                    salary_range=None,
                    experience_required=job.get('levels', [{}])[0].get('name', 'Not specified') if job.get('levels') else 'Not specified',
                    action_url=job.get('refs', {}).get('landing_page', ''),
                    action_label='Apply on The Muse',
                    match_score=88,
                    match_reason='Curated opportunity from The Muse',
                    is_remote='remote' in location_str.lower(),
                    is_verified=True
                ))
            
            logger.info(f"✓ The Muse: {len(unified_jobs)} jobs")
            return unified_jobs
            
        except Exception as e:
            logger.error(f"✗ The Muse FAILED: {e}")
            return []


class ArbeitnowScraper:
    """Arbeitnow - Free API for remote jobs"""
    
    def __init__(self):
        self.base_url = "https://www.arbeitnow.com/api/job-board-api"
    
    def scrape_jobs(self, keywords: str = "", max_results: int = 20) -> List[UnifiedJob]:
        """Fetch jobs from Arbeitnow"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = httpx.get(self.base_url, headers=headers, timeout=15.0)
            response.raise_for_status()
            
            data = response.json()
            jobs = data.get('data', [])
            
            unified_jobs = []
            
            for job in jobs:
                if len(unified_jobs) >= max_results:
                    break
                
                # Filter by keywords
                if keywords:
                    title = job.get('title', '').lower()
                    tags = ' '.join(job.get('tags', [])).lower()
                    if keywords.lower() not in title and keywords.lower() not in tags:
                        continue
                
                unified_jobs.append(UnifiedJob(
                    job_id=f"arbeitnow-{job.get('slug', '')}",
                    title=job.get('title', 'Remote Position'),
                    company=job.get('company_name', 'Company'),
                    location=job.get('location', 'Remote'),
                    source=JobSource.API,
                    source_platform='Arbeitnow',
                    job_type=JobType.DIRECT,
                    description=job.get('description', '')[:500],
                    posted_date=job.get('created_at', 'Recently')[:10],
                    salary_range=None,
                    experience_required='Not specified',
                    action_url=job.get('url', ''),
                    action_label='Apply Now',
                    match_score=82,
                    match_reason='Remote opportunity',
                    is_remote=True,
                    is_verified=True
                ))
            
            logger.info(f"✓ Arbeitnow: {len(unified_jobs)} jobs")
            return unified_jobs
            
        except Exception as e:
            logger.error(f"✗ Arbeitnow FAILED: {e}")
            return []


class RemotiveScraper:
    """Remotive - Free API for remote jobs"""
    
    def __init__(self):
        self.base_url = "https://remotive.com/api/remote-jobs"
    
    def scrape_jobs(self, keywords: str = "", max_results: int = 20) -> List[UnifiedJob]:
        """Fetch jobs from Remotive"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            params = {}
            if keywords:
                params['search'] = keywords
            
            response = httpx.get(self.base_url, params=params, headers=headers, timeout=15.0)
            response.raise_for_status()
            
            data = response.json()
            jobs = data.get('jobs', [])
            
            unified_jobs = []
            
            for job in jobs[:max_results]:
                unified_jobs.append(UnifiedJob(
                    job_id=f"remotive-{job.get('id', '')}",
                    title=job.get('title', 'Remote Position'),
                    company=job.get('company_name', 'Company'),
                    location=job.get('candidate_required_location', 'Remote'),
                    source=JobSource.API,
                    source_platform='Remotive',
                    job_type=JobType.DIRECT,
                    description=job.get('description', '')[:500],
                    posted_date=job.get('publication_date', 'Recently')[:10],
                    salary=job.get('salary', ''),
                    experience_required='Not specified',
                    action_url=job.get('url', ''),
                    action_label='Apply on Remotive',
                    match_score=86,
                    match_reason='Remote opportunity from Remotive',
                    is_remote=True,
                    is_verified=True
                ))
            
            logger.info(f"✓ Remotive: {len(unified_jobs)} jobs")
            return unified_jobs
            
        except Exception as e:
            logger.error(f"✗ Remotive FAILED: {e}")
            return []


class GreenhouseScraper:
    """Greenhouse - Public company boards"""
    
    def __init__(self):
        self.companies = [
            {'name': 'Airbnb', 'board_token': 'airbnb'},
            {'name': 'Stripe', 'board_token': 'stripe'},
            {'name': 'Coinbase', 'board_token': 'coinbase'},
            {'name': 'Dropbox', 'board_token': 'dropbox'},
        ]
    
    def scrape_jobs(self, keywords: str = "", max_results: int = 15) -> List[UnifiedJob]:
        """Fetch jobs from Greenhouse boards"""
        unified_jobs = []
        
        for company in self.companies:
            if len(unified_jobs) >= max_results:
                break
            
            try:
                url = f"https://boards-api.greenhouse.io/v1/boards/{company['board_token']}/jobs"
                headers = {'User-Agent': 'Mozilla/5.0'}
                
                response = httpx.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                jobs = data.get('jobs', [])
                
                for job in jobs[:3]:  # Max 3 per company
                    if len(unified_jobs) >= max_results:
                        break
                    
                    title = job.get('title', '')
                    
                    # Filter by keywords
                    if keywords and keywords.lower() not in title.lower():
                        continue
                    
                    # Skip pure tech roles
                    if any(kw in title.lower() for kw in ['engineer', 'developer', 'programmer']):
                        continue
                    
                    location = job.get('location', {}).get('name', 'Not specified')
                    
                    unified_jobs.append(UnifiedJob(
                        job_id=f"greenhouse-{job.get('id')}",
                        title=title,
                        company=company['name'],
                        location=location,
                        source=JobSource.API,
                        source_platform='Greenhouse',
                        job_type=JobType.DIRECT,
                        description=job.get('content', '')[:500],
                        posted_date='Recently',
                        salary_range=None,
                        experience_required='Not specified',
                        action_url=job.get('absolute_url', ''),
                        action_label=f'Apply at {company["name"]}',
                        match_score=90,
                        match_reason=f'Top company opportunity at {company["name"]}',
                        is_remote='remote' in location.lower(),
                        is_verified=True
                    ))
                    
            except Exception as e:
                logger.warning(f"✗ {company['name']} failed: {e}")
                continue
        
        logger.info(f"✓ Greenhouse: {len(unified_jobs)} jobs")
        return unified_jobs
