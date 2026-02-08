"""
RSS Scrapers for Reliable Job Discovery
Uses public RSS feeds which are not blocked like HTML scrapers
"""

import logging
import httpx
import xml.etree.ElementTree as ET
from typing import List
from datetime import datetime
import re
import html

from backend.unified_discovery.schemas import UnifiedJob, JobSource, JobType

logger = logging.getLogger(__name__)

class RSSJobScraper:
    """Base class for RSS scraping"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def _clean_html(self, raw_html: str) -> str:
        """Remove HTML tags"""
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return html.unescape(cleantext).strip()

    def _parse_date(self, date_str: str) -> str:
        """Parse RSS date format"""
        try:
            # Common RSS date format: "Mon, 06 Sep 2021 16:45:00 +0000"
            dt = datetime.strptime(date_str.replace("GMT", "+0000").strip(), "%a, %d %b %Y %H:%M:%S %z")
            return dt.strftime("%Y-%m-%d")
        except:
            return datetime.now().strftime("%Y-%m-%d")


class RemoteOKRSS(RSSJobScraper):
    """RemoteOK RSS Feed"""
    feed_url = "https://remoteok.com/rss"
    
    def scrape(self, limit: int = 50) -> List[UnifiedJob]:
        try:
            response = httpx.get(self.feed_url, headers=self.headers, timeout=20.0)
            root = ET.fromstring(response.content)
            
            jobs = []
            for item in root.findall(".//item"):
                if len(jobs) >= limit: break
                
                try:
                    title = item.find("title").text if item.find("title") is not None else "Remote Role"
                    description = self._clean_html(item.find("description").text) if item.find("description") is not None else ""
                    link = item.find("link").text if item.find("link") is not None else ""
                    pub_date = self._parse_date(item.find("pubDate").text) if item.find("pubDate") is not None else ""
                    guid = item.find("guid").text if item.find("guid") is not None else link
                    
                    # Extract Company and Location if possible (RemoteOK usually puts it in title "Role at Company")
                    company = "Remote Company"
                    if " at " in title:
                        parts = title.split(" at ")
                        title = parts[0].strip()
                        company = parts[1].strip()
                    
                    jobs.append(UnifiedJob(
                        job_id=f"rok-{abs(hash(guid))}",
                        title=title,
                        company=company,
                        location="Remote",
                        source=JobSource.API,
                        source_platform="RemoteOK",
                        job_type=JobType.DIRECT,
                        description=description[:500] + "...",
                        posted_date=pub_date,
                        salary_range=None, # RSS rarely has salary
                        experience_required="Not specified",
                        action_url=link,
                        action_label="Apply on RemoteOK",
                        match_score=85, # Base score
                        match_reason="Verified remote opportunity",
                        is_remote=True,
                        is_verified=True
                    ))
                except Exception as e:
                    continue
            
            logger.info(f"✓ RemoteOK RSS: {len(jobs)} jobs")
            return jobs
        except Exception as e:
            logger.error(f"RemoteOK RSS failed: {e}")
            return []


class WeWorkRemotelyRSS(RSSJobScraper):
    """WeWorkRemotely RSS Feeds"""
    feeds = [
        "https://weworkremotely.com/categories/remote-programming-jobs.rss",
        "https://weworkremotely.com/categories/remote-design-jobs.rss",
        "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
        "https://weworkremotely.com/categories/remote-management-and-finance-jobs.rss",
        "https://weworkremotely.com/categories/remote-product-jobs.rss"
    ]
    
    def scrape(self, limit: int = 50) -> List[UnifiedJob]:
        jobs = []
        jobs_per_feed = limit // len(self.feeds) + 2
        
        for feed in self.feeds:
            try:
                if len(jobs) >= limit: break
                
                response = httpx.get(feed, headers=self.headers, timeout=10.0)
                root = ET.fromstring(response.content)
                
                for item in root.findall(".//item"):
                    if len(jobs) >= limit: break
                    
                    try:
                        title_full = item.find("title").text
                        # WWR Title format: "Company: Role"
                        company = "WeWorkRemotely"
                        title = title_full
                        if ":" in title_full:
                            parts = title_full.split(":", 1)
                            company = parts[0].strip()
                            title = parts[1].strip()

                        description = self._clean_html(item.find("description").text)
                        link = item.find("link").text
                        pub_date = self._parse_date(item.find("pubDate").text)
                        guid = item.find("guid").text
                        
                        jobs.append(UnifiedJob(
                            job_id=f"wwr-{abs(hash(guid))}",
                            title=title,
                            company=company,
                            location="Remote",
                            source=JobSource.API,
                            source_platform="WeWorkRemotely",
                            job_type=JobType.DIRECT,
                            description=description[:500] + "...",
                            posted_date=pub_date,
                            salary_range=None,
                            experience_required="Not specified",
                            action_url=link,
                            action_label="Apply on WWR",
                            match_score=88,
                            match_reason="Premium remote job",
                            is_remote=True,
                            is_verified=True
                        ))
                    except:
                        continue
            except Exception:
                continue
                
        logger.info(f"✓ WeWorkRemotely RSS: {len(jobs)} jobs")
        return jobs


class RemotiveRSS(RSSJobScraper):
    """Remotive RSS Feed"""
    feed_url = "https://remotive.com/remote-jobs/feed"
    
    def scrape(self, limit: int = 50) -> List[UnifiedJob]:
        try:
            response = httpx.get(self.feed_url, headers=self.headers, timeout=20.0)
            root = ET.fromstring(response.content)
            
            jobs = []
            for item in root.findall(".//item"):
                if len(jobs) >= limit: break
                
                try:
                    title_full = item.find("title").text
                    # Remotive sometimes works usually just Role
                    title = title_full
                    
                    description = self._clean_html(item.find("description").text)
                    link = item.find("link").text
                    pub_date = self._parse_date(item.find("pubDate").text)
                    guid = item.find("guid").text
                    
                    # Try to find company in description or title
                    company = "Remotive Company"
                    
                    jobs.append(UnifiedJob(
                        job_id=f"rem-{abs(hash(guid))}",
                        title=title,
                        company=company,
                        location="Remote",
                        source=JobSource.API,
                        source_platform="Remotive",
                        job_type=JobType.DIRECT,
                        description=description[:500] + "...",
                        posted_date=pub_date,
                        salary_range=None,
                        experience_required="Not specified",
                        action_url=link,
                        action_label="Apply on Remotive",
                        match_score=82,
                        match_reason="Verified remote job",
                        is_remote=True,
                        is_verified=True
                    ))
                except:
                    continue
            
            logger.info(f"✓ Remotive RSS: {len(jobs)} jobs")
            return jobs
        except Exception as e:
            logger.error(f"Remotive RSS failed: {e}")
            return []
