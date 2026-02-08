"""
Pattern Analyzer
Analyzes MBA job data to learn role patterns, skill expectations, and hiring trends
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from collections import Counter, defaultdict

from backend.mba_data.schemas import ResumiMBAJob, RoleFamily, MBAJobPattern

logger = logging.getLogger(__name__)


class PatternAnalyzer:
    """Analyzes MBA job patterns"""
    
    def __init__(self, patterns_dir: Path = None):
        """
        Initialize analyzer
        
        Args:
            patterns_dir: Directory to save learned patterns
        """
        if patterns_dir is None:
            data_dir = Path(__file__).parent.parent.parent / 'data'
            patterns_dir = data_dir / 'mba_campus_jobs' / 'patterns'
        
        self.patterns_dir = patterns_dir
        self.patterns_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_role_patterns(self, jobs: List[ResumiMBAJob]) -> Dict[str, Any]:
        """
        Analyze role family patterns
        
        Learns:
        - Distribution of role families
        - Common titles per family
        - Team functions per family
        - Tech requirement levels
        """
        logger.info(f"Analyzing role patterns from {len(jobs)} jobs")
        
        role_data = defaultdict(lambda: {
            'count': 0,
            'titles': Counter(),
            'teams': Counter(),
            'employment_types': Counter(),
            'work_modes': Counter()
        })
        
        for job in jobs:
            family = job.role_family
            role_data[family]['count'] += 1
            
            if job.job_title:
                role_data[family]['titles'][job.job_title] += 1
            
            if job.team_function:
                role_data[family]['teams'][job.team_function] += 1
            
            role_data[family]['employment_types'][job.employment_type] += 1
            role_data[family]['work_modes'][job.work_mode] += 1
        
        # Convert to serializable format
        patterns = {}
        for family, data in role_data.items():
            patterns[family] = {
                'count': data['count'],
                'percentage': round(data['count'] / len(jobs) * 100, 1),
                'common_titles': dict(data['titles'].most_common(10)),
                'typical_teams': dict(data['teams'].most_common(5)),
                'employment_types': dict(data['employment_types']),
                'work_modes': dict(data['work_modes'])
            }
        
        # Save patterns
        output_file = self.patterns_dir / 'mba_role_patterns.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(patterns, f, indent=2)
        
        logger.info(f"Role patterns saved to {output_file}")
        return patterns
    
    def analyze_location_patterns(self, jobs: List[ResumiMBAJob]) -> Dict[str, Any]:
        """
        Analyze location patterns by role family
        
        Learns:
        - India cities per role family
        - UAE cities per role family
        - PAN-India roles
        """
        logger.info(f"Analyzing location patterns from {len(jobs)} jobs")
        
        location_data = defaultdict(lambda: {
            'india_cities': Counter(),
            'uae_cities': Counter(),
            'other_locations': Counter(),
            'total_jobs': 0
        })
        
        india_cities = {'mumbai', 'bangalore', 'bengaluru', 'delhi', 'gurgaon', 'gurugram', 
                       'hyderabad', 'pune', 'chennai', 'kolkata', 'ahmedabad', 'noida'}
        uae_cities = {'dubai', 'abu dhabi', 'sharjah', 'ajman'}
        
        for job in jobs:
            family = job.role_family
            location_data[family]['total_jobs'] += 1
            
            for location in job.job_locations:
                location_lower = location.lower()
                
                if any(city in location_lower for city in india_cities):
                    location_data[family]['india_cities'][location] += 1
                elif any(city in location_lower for city in uae_cities):
                    location_data[family]['uae_cities'][location] += 1
                else:
                    location_data[family]['other_locations'][location] += 1
        
        # Convert to serializable format
        patterns = {}
        for family, data in location_data.items():
            india_count = sum(data['india_cities'].values())
            uae_count = sum(data['uae_cities'].values())
            
            patterns[family] = {
                'total_jobs': data['total_jobs'],
                'india_cities': dict(data['india_cities'].most_common(10)),
                'uae_cities': dict(data['uae_cities'].most_common(5)),
                'other_locations': dict(data['other_locations'].most_common(5)),
                'india_percentage': round(india_count / data['total_jobs'] * 100, 1) if data['total_jobs'] > 0 else 0,
                'uae_percentage': round(uae_count / data['total_jobs'] * 100, 1) if data['total_jobs'] > 0 else 0,
                'pan_india': india_count > data['total_jobs'] * 0.5  # More than 50% have India locations
            }
        
        # Save patterns
        output_file = self.patterns_dir / 'mba_location_patterns.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(patterns, f, indent=2)
        
        logger.info(f"Location patterns saved to {output_file}")
        return patterns
    
    def analyze_ctc_patterns(self, jobs: List[ResumiMBAJob]) -> Dict[str, Any]:
        """
        Analyze CTC patterns by role family
        
        Learns:
        - CTC ranges per role family
        - CTC band distribution
        """
        logger.info(f"Analyzing CTC patterns from {len(jobs)} jobs")
        
        ctc_data = defaultdict(lambda: {
            'ctc_values': [],
            'ctc_bands': Counter(),
            'total_jobs': 0
        })
        
        for job in jobs:
            family = job.role_family
            ctc_data[family]['total_jobs'] += 1
            ctc_data[family]['ctc_bands'][job.ctc_band] += 1
            
            if job.ctc_max:
                ctc_data[family]['ctc_values'].append(job.ctc_max)
            elif job.ctc_min:
                ctc_data[family]['ctc_values'].append(job.ctc_min)
        
        # Calculate statistics
        patterns = {}
        for family, data in ctc_data.items():
            ctc_values = data['ctc_values']
            
            patterns[family] = {
                'total_jobs': data['total_jobs'],
                'ctc_bands': dict(data['ctc_bands']),
                'ctc_stats': {
                    'min': min(ctc_values) if ctc_values else None,
                    'max': max(ctc_values) if ctc_values else None,
                    'median': sorted(ctc_values)[len(ctc_values)//2] if ctc_values else None,
                    'sample_count': len(ctc_values)
                }
            }
        
        # Save patterns
        output_file = self.patterns_dir / 'mba_ctc_patterns.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(patterns, f, indent=2)
        
        logger.info(f"CTC patterns saved to {output_file}")
        return patterns
    
    def analyze_all_patterns(self, jobs: List[ResumiMBAJob]) -> Dict[str, Any]:
        """
        Run all pattern analyses
        
        Returns:
            Summary of all analyses
        """
        logger.info(f"Running all pattern analyses on {len(jobs)} jobs")
        
        role_patterns = self.analyze_role_patterns(jobs)
        location_patterns = self.analyze_location_patterns(jobs)
        ctc_patterns = self.analyze_ctc_patterns(jobs)
        
        summary = {
            'total_jobs_analyzed': len(jobs),
            'role_families_found': len(role_patterns),
            'patterns_generated': ['role', 'location', 'ctc'],
            'output_directory': str(self.patterns_dir)
        }
        
        logger.info(f"Pattern analysis complete: {summary}")
        return summary
