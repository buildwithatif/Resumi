"""
Base Job Collector
Abstract base class for all job source collectors
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging
import asyncio
import httpx
from datetime import datetime
from urllib.parse import urlparse

try:
    from robotexclusionrulesparser import RobotExclusionRulesParser
    ROBOTS_AVAILABLE = True
except ImportError:
    ROBOTS_AVAILABLE = False
    
logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for API requests"""
    
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute
        self.last_request_time = 0.0
    
    async def wait(self):
        """Wait if necessary to respect rate limit"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            wait_time = self.min_interval - time_since_last
            await asyncio.sleep(wait_time)
        
        self.last_request_time = asyncio.get_event_loop().time()


class BaseJobCollector(ABC):
    """Abstract base class for job collectors"""
    
    def __init__(self, source_name: str, rate_limit: int = 60):
        self.source_name = source_name
        self.rate_limiter = RateLimiter(rate_limit)
        self.client: Optional[httpx.AsyncClient] = None
        self.robots_parsers: Dict[str, Any] = {}  # Cache robots.txt parsers by domain
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                'User-Agent': 'ResumiV1/1.0 (Job Recommendation Engine; +https://github.com/resumi)'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.client:
            await self.client.aclose()
    
    async def fetch_url(self, url: str, check_robots: bool = True) -> Optional[Dict[str, Any]]:
        """
        Fetch URL with rate limiting, robots.txt checking, and error handling
        
        Args:
            url: URL to fetch
            check_robots: Whether to check robots.txt before fetching
            
        Returns:
            JSON response or None if failed
        """
        # Check robots.txt if enabled
        if check_robots and ROBOTS_AVAILABLE:
            if not await self._check_robots_allowed(url):
                logger.warning(f"Robots.txt disallows fetching {url}")
                return None
        
        await self.rate_limiter.wait()
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP error fetching {url}: {e.response.status_code}")
            return None
        except httpx.RequestError as e:
            logger.warning(f"Request error fetching {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None
    
    async def _check_robots_allowed(self, url: str) -> bool:
        """
        Check if robots.txt allows fetching this URL
        
        Args:
            url: URL to check
            
        Returns:
            True if allowed, False otherwise
        """
        if not ROBOTS_AVAILABLE:
            return True
        
        try:
            parsed = urlparse(url)
            domain = f"{parsed.scheme}://{parsed.netloc}"
            
            # Check cache first
            if domain not in self.robots_parsers:
                robots_url = f"{domain}/robots.txt"
                try:
                    response = await self.client.get(robots_url, timeout=5.0)
                    if response.status_code == 200:
                        parser = RobotExclusionRulesParser()
                        parser.parse(response.text)
                        self.robots_parsers[domain] = parser
                    else:
                        # No robots.txt or error - allow by default
                        self.robots_parsers[domain] = None
                except Exception:
                    # Error fetching robots.txt - allow by default
                    self.robots_parsers[domain] = None
            
            parser = self.robots_parsers.get(domain)
            if parser is None:
                return True
            
            user_agent = 'ResumiV1/1.0'
            return parser.is_allowed(user_agent, url)
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {e}")
            return True  # Allow by default on error
    
    @abstractmethod
    async def collect_jobs(self, max_jobs: int = 100) -> List[Dict[str, Any]]:
        """
        Collect jobs from source
        
        Args:
            max_jobs: Maximum number of jobs to collect
            
        Returns:
            List of raw job dictionaries
        """
        pass
    
    def normalize_raw_job(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert source-specific format to standard raw format
        
        Args:
            raw_job: Raw job data from source
            
        Returns:
            Standardized raw job dictionary
        """
        return {
            'source': self.source_name,
            'collected_at': datetime.utcnow().isoformat(),
            'raw_data': raw_job,
        }
