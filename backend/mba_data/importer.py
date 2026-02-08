"""
Campus Data Importer
Imports campus JSON data, maps to ResumiMBAJob schema, and stores for analysis
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from backend.mba_data.campus_mapper import map_campus_job
from backend.mba_data.schemas import ResumiMBAJob

logger = logging.getLogger(__name__)


class CampusDataImporter:
    """Imports and processes campus placement data"""
    
    def __init__(self, data_dir: Path = None):
        """
        Initialize importer
        
        Args:
            data_dir: Base data directory (defaults to project data/)
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / 'data'
        
        self.data_dir = data_dir
        self.mba_data_dir = data_dir / 'mba_campus_jobs'
        self.raw_dir = self.mba_data_dir / 'raw'
        self.mapped_dir = self.mba_data_dir / 'mapped'
        self.patterns_dir = self.mba_data_dir / 'patterns'
        
        # Create directories
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.mapped_dir.mkdir(parents=True, exist_ok=True)
        self.patterns_dir.mkdir(parents=True, exist_ok=True)
    
    def import_campus_json(self, json_file_path: str) -> Dict[str, Any]:
        """
        Import campus jobs from JSON file
        
        Args:
            json_file_path: Path to campus JSON file
            
        Returns:
            Import statistics
        """
        logger.info(f"Importing campus data from: {json_file_path}")
        
        try:
            # Load JSON
            with open(json_file_path, 'r', encoding='utf-8') as f:
                campus_data = json.load(f)
            
            # Handle both single job and array of jobs
            if isinstance(campus_data, dict):
                campus_jobs = [campus_data]
            else:
                campus_jobs = campus_data
            
            # Map jobs
            mapped_jobs = []
            failed_jobs = []
            
            for campus_job in campus_jobs:
                mapped_job = map_campus_job(campus_job)
                if mapped_job:
                    mapped_jobs.append(mapped_job)
                else:
                    failed_jobs.append(campus_job.get('_id', 'unknown'))
            
            # Save raw data (NEVER EXPOSE)
            raw_filename = f"campus_raw_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            raw_path = self.raw_dir / raw_filename
            with open(raw_path, 'w', encoding='utf-8') as f:
                json.dump(campus_jobs, f, indent=2)
            
            # Save mapped data
            mapped_filename = f"campus_mapped_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            mapped_path = self.mapped_dir / mapped_filename
            mapped_dicts = [job.dict() for job in mapped_jobs]
            with open(mapped_path, 'w', encoding='utf-8') as f:
                json.dump(mapped_dicts, f, indent=2)
            
            stats = {
                'total_jobs': len(campus_jobs),
                'mapped_successfully': len(mapped_jobs),
                'mapping_failed': len(failed_jobs),
                'failed_job_ids': failed_jobs,
                'raw_file': str(raw_path),
                'mapped_file': str(mapped_path)
            }
            
            logger.info(f"Import complete: {stats['mapped_successfully']}/{stats['total_jobs']} jobs mapped")
            
            return stats
            
        except Exception as e:
            logger.error(f"Import failed: {e}")
            raise
    
    def load_all_mapped_jobs(self) -> List[ResumiMBAJob]:
        """
        Load all mapped jobs from storage
        
        Returns:
            List of ResumiMBAJob objects
        """
        all_jobs = []
        
        for mapped_file in self.mapped_dir.glob('campus_mapped_*.json'):
            try:
                with open(mapped_file, 'r', encoding='utf-8') as f:
                    jobs_data = json.load(f)
                
                for job_data in jobs_data:
                    all_jobs.append(ResumiMBAJob(**job_data))
            
            except Exception as e:
                logger.error(f"Failed to load {mapped_file}: {e}")
        
        logger.info(f"Loaded {len(all_jobs)} mapped jobs from storage")
        return all_jobs
    
    def get_import_stats(self) -> Dict[str, Any]:
        """Get statistics about imported data"""
        raw_files = list(self.raw_dir.glob('campus_raw_*.json'))
        mapped_files = list(self.mapped_dir.glob('campus_mapped_*.json'))
        
        total_jobs = 0
        for mapped_file in mapped_files:
            with open(mapped_file, 'r', encoding='utf-8') as f:
                jobs = json.load(f)
                total_jobs += len(jobs)
        
        return {
            'raw_files_count': len(raw_files),
            'mapped_files_count': len(mapped_files),
            'total_mapped_jobs': total_jobs,
            'last_import': max([f.stat().st_mtime for f in mapped_files]) if mapped_files else None
        }
