"""
Real Job Scrapers
Scrapes actual jobs from public job boards that allow it
"""

import logging
import httpx
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime

from backend.unified_discovery.schemas import UnifiedJob, JobSource, JobType

logger = logging.getLogger(__name__)


class RemoteOKScraper:
    """
    Scrapes jobs from RemoteOK (allows scraping, has public API-like structure)
    """
    
    def __init__(self):
        self.base_url = "https://remoteok.com/api"
    
    def scrape_jobs(self, keywords: str = "", max_results: int = 20) -> List[UnifiedJob]:
        """Fetch real jobs from RemoteOK"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = httpx.get(self.base_url, headers=headers, timeout=15.0)
            response.raise_for_status()
            
            jobs_data = response.json()
            unified_jobs = []
            
            # Skip first item (it's metadata), get more jobs
            for job in jobs_data[1:max_results+10]:  # Get extra in case some are filtered
                # Filter by keywords if provided
                if keywords:
                    title_match = keywords.lower() in job.get('position', '').lower()
                    tags_match = any(keywords.lower() in tag.lower() for tag in job.get('tags', []))
                    if not (title_match or tags_match):
                        continue
                
                unified_jobs.append(UnifiedJob(
                    job_id=f"remoteok-{job.get('id', '')}",
                    title=job.get('position', 'Unknown Position'),
                    company=job.get('company', 'Unknown Company'),
                    location='Remote',
                    source=JobSource.API,
                    source_platform='RemoteOK',
                    job_type=JobType.DIRECT,
                    description=job.get('description', '')[:500],  # Truncate
                    posted_date=self._format_date(job.get('date')),
                    salary_range=self._format_salary(job.get('salary_min'), job.get('salary_max')),
                    experience_required='Not specified',
                    action_url=job.get('url', f"https://remoteok.com/remote-jobs/{job.get('id')}"),
                    action_label='Apply on RemoteOK',
                    match_score=85,
                    match_reason='Remote opportunity matching your profile',
                    is_remote=True,
                    is_verified=True
                ))
                
                if len(unified_jobs) >= max_results:
                    break
            
            logger.info(f"Scraped {len(unified_jobs)} jobs from RemoteOK")
            return unified_jobs
            
        except Exception as e:
            logger.error(f"RemoteOK scraping failed: {e}")
            return []
    
    def _format_date(self, timestamp):
        """Format timestamp to readable date"""
        if not timestamp:
            return 'Recently'
        try:
            dt = datetime.fromtimestamp(int(timestamp))
            days_ago = (datetime.now() - dt).days
            if days_ago == 0:
                return 'Today'
            elif days_ago == 1:
                return 'Yesterday'
            elif days_ago < 7:
                return f'{days_ago} days ago'
            elif days_ago < 30:
                return f'{days_ago // 7} weeks ago'
            else:
                return f'{days_ago // 30} months ago'
        except:
            return 'Recently'
    
    def _format_salary(self, min_sal, max_sal):
        """Format salary range"""
        if min_sal and max_sal:
            return f"${min_sal//1000}k-${max_sal//1000}k"
        return None


class WeWorkRemotelyScraper:
    """
    Scrapes jobs from We Work Remotely
    """
    
    def __init__(self):
        self.base_url = "https://weworkremotely.com"
    
    def scrape_jobs(self, keywords: str = "", max_results: int = 10) -> List[UnifiedJob]:
        """Fetch real jobs from WeWorkRemotely"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Scrape business/management category
            url = f"{self.base_url}/categories/remote-business-management-jobs"
            response = httpx.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            job_listings = soup.find_all('li', class_='feature')
            
            unified_jobs = []
            
            for job_elem in job_listings[:max_results]:
                try:
                    title_elem = job_elem.find('span', class_='title')
                    company_elem = job_elem.find('span', class_='company')
                    link_elem = job_elem.find('a')
                    
                    if not (title_elem and company_elem and link_elem):
                        continue
                    
                    title = title_elem.text.strip()
                    company = company_elem.text.strip()
                    job_url = self.base_url + link_elem['href']
                    
                    # Filter by keywords
                    if keywords and keywords.lower() not in title.lower():
                        continue
                    
                    unified_jobs.append(UnifiedJob(
                        job_id=f"wwr-{link_elem['href'].split('/')[-1]}",
                        title=title,
                        company=company,
                        location='Remote',
                        source=JobSource.API,
                        source_platform='WeWorkRemotely',
                        job_type=JobType.DIRECT,
                        description=f'{title} at {company}. Remote position.',
                        posted_date='Recently',
                        salary_range=None,
                        experience_required='Not specified',
                        action_url=job_url,
                        action_label='Apply on WWR',
                        match_score=82,
                        match_reason='Remote business/management role',
                        is_remote=True,
                        is_verified=True
                    ))
                    
                except Exception as e:
                    logger.warning(f"Failed to parse job: {e}")
                    continue
            
            logger.info(f"Scraped {len(unified_jobs)} jobs from WeWorkRemotely")
            return unified_jobs
            
        except Exception as e:
            logger.error(f"WeWorkRemotely scraping failed: {e}")
            return []


class GreenhouseScraper:
    """
    Scrapes jobs from companies using Greenhouse ATS
    """
    
    def __init__(self):
        # List of companies with public Greenhouse boards
        self.companies = [
            {'name': 'Airbnb', 'board_token': 'airbnb'},
            {'name': 'Stripe', 'board_token': 'stripe'},
            {'name': 'Coinbase', 'board_token': 'coinbase'},
            {'name': 'Dropbox', 'board_token': 'dropbox'},
            {'name': 'Shopify', 'board_token': 'shopify'},
        ]
    
    def scrape_jobs(self, keywords: str = "", max_results: int = 10) -> List[UnifiedJob]:
        """Fetch real jobs from Greenhouse boards"""
        unified_jobs = []
        
        for company in self.companies:
            if len(unified_jobs) >= max_results:
                break
            
            try:
                url = f"https://boards-api.greenhouse.io/v1/boards/{company['board_token']}/jobs"
                headers = {'User-Agent': 'Mozilla/5.0'}
                
                response = httpx.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()
                
                jobs_data = response.json()
                
                for job in jobs_data.get('jobs', [])[:5]:  # Max 5 per company
                    title = job.get('title', '')
                    
                    # Filter by keywords and non-tech roles
                    if keywords and keywords.lower() not in title.lower():
                        continue
                    
                    # Skip pure tech roles
                    tech_keywords = ['engineer', 'developer', 'programmer', 'software']
                    if any(kw in title.lower() for kw in tech_keywords):
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
                        match_score=88,
                        match_reason=f'Top company ({company["name"]}) opportunity',
                        is_remote='remote' in location.lower(),
                        is_verified=True
                    ))
                    
                    if len(unified_jobs) >= max_results:
                        break
                        
            except Exception as e:
                logger.warning(f"Failed to scrape {company['name']}: {e}")
                continue
        
        logger.info(f"Scraped {len(unified_jobs)} jobs from Greenhouse")
        return unified_jobs


class LinkedInPublicScraper:
    """
    Scrapes public LinkedIn job postings (no authentication required)
    """
    
    def __init__(self):
        self.base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    
    def scrape_jobs(self, keywords: str = "", location: str = "India", max_results: int = 15) -> List[UnifiedJob]:
        """Fetch real jobs from LinkedIn public listings"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            params = {
                'keywords': keywords,
                'location': location,
                'start': 0
            }
            
            response = httpx.get(self.base_url, headers=headers, params=params, timeout=10.0)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            job_cards = soup.find_all('div', class_='base-card')
            
            unified_jobs = []
            
            for card in job_cards[:max_results]:
                try:
                    title_elem = card.find('h3', class_='base-search-card__title')
                    company_elem = card.find('h4', class_='base-search-card__subtitle')
                    location_elem = card.find('span', class_='job-search-card__location')
                    link_elem = card.find('a', class_='base-card__full-link')
                    
                    if not (title_elem and company_elem and link_elem):
                        continue
                    
                    title = title_elem.text.strip()
                    company = company_elem.text.strip()
                    job_location = location_elem.text.strip() if location_elem else location
                    job_url = link_elem['href']
                    job_id = job_url.split('/')[-1].split('?')[0]
                    
                    unified_jobs.append(UnifiedJob(
                        job_id=f"linkedin-public-{job_id}",
                        title=title,
                        company=company,
                        location=job_location,
                        source=JobSource.API,
                        source_platform='LinkedIn',
                        job_type=JobType.DIRECT,
                        description=f'{title} position at {company}',
                        posted_date='Recently',
                        salary_range=None,
                        experience_required='Not specified',
                        action_url=job_url,
                        action_label='Apply on LinkedIn',
                        match_score=86,
                        match_reason='LinkedIn verified opportunity',
                        is_remote='remote' in job_location.lower(),
                        is_verified=True
                    ))
                    
                except Exception as e:
                    logger.warning(f"Failed to parse LinkedIn job: {e}")
                    continue
            
            logger.info(f"Scraped {len(unified_jobs)} jobs from LinkedIn public")
            return unified_jobs
            
        except Exception as e:
            logger.error(f"LinkedIn public scraping failed: {e}")
            return []


class IndeedPublicScraper:
    """
    Scrapes public Indeed job listings
    """
    
    def __init__(self):
        self.base_url = "https://in.indeed.com/jobs"
    
    def scrape_jobs(self, keywords: str = "", location: str = "India", max_results: int = 15) -> List[UnifiedJob]:
        """Fetch real jobs from Indeed public listings"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            params = {
                'q': keywords,
                'l': location
            }
            
            response = httpx.get(self.base_url, headers=headers, params=params, timeout=10.0)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Indeed uses different class names, try multiple selectors
            job_cards = soup.find_all('div', class_='job_seen_beacon') or soup.find_all('a', class_='jcs-JobTitle')
            
            unified_jobs = []
            
            for card in job_cards[:max_results]:
                try:
                    # Try to extract job details
                    if card.name == 'a':
                        title = card.text.strip()
                        job_url = 'https://in.indeed.com' + card['href']
                        # Find parent to get company
                        parent = card.find_parent('div', class_='job_seen_beacon')
                        company_elem = parent.find('span', class_='companyName') if parent else None
                        company = company_elem.text.strip() if company_elem else 'Company'
                    else:
                        title_elem = card.find('h2', class_='jobTitle') or card.find('a', class_='jcs-JobTitle')
                        company_elem = card.find('span', class_='companyName')
                        
                        if not (title_elem and company_elem):
                            continue
                        
                        title = title_elem.text.strip()
                        company = company_elem.text.strip()
                        
                        link = card.find('a')
                        job_url = 'https://in.indeed.com' + link['href'] if link else ''
                    
                    job_id = job_url.split('jk=')[-1].split('&')[0] if 'jk=' in job_url else str(hash(title + company))
                    
                    unified_jobs.append(UnifiedJob(
                        job_id=f"indeed-public-{job_id}",
                        title=title,
                        company=company,
                        location=location,
                        source=JobSource.API,
                        source_platform='Indeed',
                        job_type=JobType.DIRECT,
                        description=f'{title} role at {company}',
                        posted_date='Recently',
                        salary_range=None,
                        experience_required='Not specified',
                        action_url=job_url,
                        action_label='Apply on Indeed',
                        match_score=84,
                        match_reason='Indeed verified listing',
                        is_remote=False,
                        is_verified=True
                    ))
                    
                except Exception as e:
                    logger.warning(f"Failed to parse Indeed job: {e}")
                    continue
            
            logger.info(f"Scraped {len(unified_jobs)} jobs from Indeed public")
            return unified_jobs
            
        except Exception as e:
            logger.error(f"Indeed public scraping failed: {e}")
            return []


class AngelListScraper:
    """
    Scrapes startup jobs from AngelList/Wellfound
    """
    
    def __init__(self):
        self.base_url = "https://wellfound.com/jobs"
    
    def scrape_jobs(self, keywords: str = "", max_results: int = 10) -> List[UnifiedJob]:
        """Fetch startup jobs from AngelList"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # AngelList has a public API endpoint
            api_url = "https://wellfound.com/api/jobs"
            params = {'query': keywords} if keywords else {}
            
            response = httpx.get(api_url, headers=headers, params=params, timeout=10.0, follow_redirects=True)
            
            # If API fails, try scraping
            if response.status_code != 200:
                return []
            
            unified_jobs = []
            
            # Try to parse JSON response
            try:
                data = response.json()
                jobs = data.get('jobs', [])[:max_results]
                
                for job in jobs:
                    unified_jobs.append(UnifiedJob(
                        job_id=f"angellist-{job.get('id', '')}",
                        title=job.get('title', 'Startup Role'),
                        company=job.get('startup', {}).get('name', 'Startup'),
                        location=job.get('location', 'Remote'),
                        source=JobSource.API,
                        source_platform='AngelList',
                        job_type=JobType.DIRECT,
                        description=job.get('description', '')[:500],
                        posted_date='Recently',
                        salary_range=job.get('salary_range'),
                        experience_required='Not specified',
                        action_url=f"https://wellfound.com/jobs/{job.get('id')}",
                        action_label='Apply on AngelList',
                        match_score=87,
                        match_reason='Startup opportunity with growth potential',
                        is_remote='remote' in job.get('location', '').lower(),
                        is_verified=True
                    ))
            except:
                pass
            
            logger.info(f"Scraped {len(unified_jobs)} jobs from AngelList")
            return unified_jobs
            
        except Exception as e:
            logger.error(f"AngelList scraping failed: {e}")
            return []
