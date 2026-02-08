"""
Job Orchestrator
Coordinates job collection from multiple sources
"""

import asyncio
import logging
from typing import List, Dict, Any
from pathlib import Path
import json
from datetime import datetime

from backend.job_sources.career_pages.greenhouse import GreenhouseCollector
from backend.job_sources.career_pages.lever import LeverCollector
from backend.job_sources.public_boards.remoteok import RemoteOKCollector

logger = logging.getLogger(__name__)


class JobOrchestrator:
    """Orchestrates job collection from multiple sources"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.jobs_raw_dir = self.data_dir / 'jobs_raw'
        self.jobs_raw_dir.mkdir(parents=True, exist_ok=True)
    
    async def collect_all_jobs(self, max_jobs_per_source: int = 100) -> List[Dict[str, Any]]:
        """
        Collect jobs from all sources concurrently
        
        Args:
            max_jobs_per_source: Maximum jobs to collect per source
            
        Returns:
            Combined list of all collected jobs
        """
        logger.info("Starting job collection from all sources...")
        
        # Create collection tasks
        tasks = [
            self._collect_from_source(GreenhouseCollector(), max_jobs_per_source),
            self._collect_from_source(LeverCollector(), max_jobs_per_source),
            self._collect_from_source(RemoteOKCollector(), max_jobs_per_source),
        ]
        
        # Run all collectors concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        all_jobs = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Collection failed: {result}")
                continue
            if isinstance(result, list):
                all_jobs.extend(result)
        
        logger.info(f"Total jobs collected: {len(all_jobs)}")
        
        # Save raw jobs
        self._save_raw_jobs(all_jobs)
        
        return all_jobs
    
    async def _collect_from_source(self, collector, max_jobs: int) -> List[Dict[str, Any]]:
        """Collect jobs from a single source"""
        async with collector:
            return await collector.collect_jobs(max_jobs)
    
    def _save_raw_jobs(self, jobs: List[Dict[str, Any]]):
        """Save raw jobs to JSON file"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = self.jobs_raw_dir / f"jobs_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(jobs)} raw jobs to {filename}")
    
    def load_latest_raw_jobs(self) -> List[Dict[str, Any]]:
        """Load most recent raw jobs file"""
        job_files = sorted(self.jobs_raw_dir.glob('jobs_*.json'), reverse=True)
        
        if not job_files:
            logger.warning("No raw job files found")
            return []
        
        latest_file = job_files[0]
        with open(latest_file, 'r', encoding='utf-8') as f:
            jobs = json.load(f)
        
        logger.info(f"Loaded {len(jobs)} jobs from {latest_file}")
        return jobs
