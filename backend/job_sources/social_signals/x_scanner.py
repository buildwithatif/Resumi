"""
X (Twitter) Signal Scanner
Scans public X/Twitter for hiring signals (no login required)
"""

from typing import List, Dict, Any
import logging
from datetime import datetime
from backend.job_sources.social_signals.base_signal_collector import BaseSignalCollector

logger = logging.getLogger(__name__)


# Search queries for MBA/non-tech roles in India/UAE
SEARCH_QUERIES = [
    "hiring MBA India",
    "strategy consultant hiring India",
    "operations manager hiring Dubai",
    "marketing manager hiring Bangalore",
    "consulting hiring UAE",
    "business analyst hiring Mumbai",
    "finance manager hiring India",
]


class XSignalScanner(BaseSignalCollector):
    """Scans X/Twitter for hiring signals"""
    
    def __init__(self):
        super().__init__('x_signal', rate_limit=1)  # Very conservative: 1/min
    
    async def collect_jobs(self, max_jobs: int = 100) -> List[Dict[str, Any]]:
        """
        Collect hiring signals from X/Twitter
        
        Note: This is a placeholder implementation.
        In production, we would:
        1. Check X's robots.txt
        2. Parse public search results (no login)
        3. Extract tweets with hiring keywords
        4. Tag as signals
        
        For V2 MVP, we're returning empty to avoid any ToS issues.
        This can be implemented later with proper HTML parsing.
        
        Args:
            max_jobs: Maximum number of signals to collect
            
        Returns:
            List of signal dictionaries
        """
        logger.info("X Signal Scanner: Placeholder - not implemented to avoid ToS issues")
        return []
    
    async def collect_signals(self, max_signals: int = 50) -> List[Dict[str, Any]]:
        """
        Collect hiring signals from X
        
        Args:
            max_signals: Maximum signals to collect
            
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        # Placeholder: In production, would parse public search results
        # For now, return empty to avoid any issues
        
        logger.info(f"X Scanner would search for: {', '.join(SEARCH_QUERIES[:3])}...")
        
        return signals
    
    def _parse_tweet(self, tweet_html: str) -> Dict[str, Any]:
        """
        Parse a tweet for hiring signals
        
        Args:
            tweet_html: HTML of tweet
            
        Returns:
            Signal dictionary
        """
        # Placeholder for tweet parsing logic
        # Would extract:
        # - Tweet text
        # - Company mentions
        # - Role hints
        # - Location hints
        # - Links
        
        signal = {
            'source': self.source_name,
            'source_type': 'signal',
            'signal_text': 'Placeholder',
            'company_mention': None,
            'potential_role': None,
            'location_hints': [],
            'external_link': None,
            'posted_date': datetime.utcnow().isoformat(),
            'confidence': 'low',
            'raw_data': {},
        }
        
        return signal
