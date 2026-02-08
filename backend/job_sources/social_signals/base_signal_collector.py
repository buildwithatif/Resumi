"""
Base Signal Collector
Abstract base class for social signal collectors (X, Reddit)
"""

from abc import abstractmethod
from typing import List, Dict, Any, Optional
import re
import logging
from backend.job_sources.base_collector import BaseJobCollector

logger = logging.getLogger(__name__)


# Common company names to look for
KNOWN_COMPANIES = {
    # India
    'razorpay', 'swiggy', 'zomato', 'flipkart', 'ola', 'paytm', 'cred', 'meesho',
    'byju', 'unacademy', 'upgrad', 'phonepe', 'policybazaar', 'sharechat',
    
    # UAE
    'careem', 'noon', 'talabat', 'fetchr', 'namshi',
    
    # Consulting
    'mckinsey', 'bain', 'bcg', 'deloitte', 'pwc', 'ey', 'kpmg', 'accenture',
    
    # Tech (MBA-friendly)
    'google', 'microsoft', 'amazon', 'meta', 'apple', 'netflix', 'uber', 'airbnb',
}

# Role keywords for MBA/non-tech positions
ROLE_KEYWORDS = {
    'strategy', 'consultant', 'operations', 'marketing', 'finance', 'analyst',
    'manager', 'associate', 'director', 'business development', 'product manager',
    'hr', 'human resources', 'sales', 'account manager',
}


class BaseSignalCollector(BaseJobCollector):
    """Base class for social signal collectors"""
    
    def __init__(self, source_name: str, rate_limit: int = 30):
        super().__init__(source_name, rate_limit)
    
    def extract_company_mentions(self, text: str) -> List[str]:
        """
        Extract company names from text
        
        Args:
            text: Text to search
            
        Returns:
            List of company names found
        """
        text_lower = text.lower()
        companies = []
        
        for company in KNOWN_COMPANIES:
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(company) + r'\b'
            if re.search(pattern, text_lower):
                companies.append(company.title())
        
        return companies
    
    def extract_role_hints(self, text: str) -> List[str]:
        """
        Extract potential role titles from text
        
        Args:
            text: Text to search
            
        Returns:
            List of potential roles
        """
        text_lower = text.lower()
        roles = []
        
        for role in ROLE_KEYWORDS:
            pattern = r'\b' + re.escape(role) + r'\b'
            if re.search(pattern, text_lower):
                roles.append(role)
        
        return roles
    
    def extract_location_hints(self, text: str) -> List[str]:
        """
        Extract location mentions from text
        
        Args:
            text: Text to search
            
        Returns:
            List of locations found
        """
        locations = []
        
        # India cities
        india_cities = ['mumbai', 'bangalore', 'bengaluru', 'delhi', 'gurgaon', 
                       'gurugram', 'hyderabad', 'pune', 'chennai', 'kolkata']
        
        # UAE cities
        uae_cities = ['dubai', 'abu dhabi', 'sharjah']
        
        # Countries
        countries = ['india', 'uae', 'united arab emirates']
        
        text_lower = text.lower()
        
        for city in india_cities + uae_cities:
            if city in text_lower:
                locations.append(city.title())
        
        for country in countries:
            if country in text_lower:
                locations.append(country.upper() if country == 'uae' else country.title())
        
        return list(set(locations))  # Remove duplicates
    
    def extract_urls(self, text: str) -> List[str]:
        """
        Extract URLs from text
        
        Args:
            text: Text to search
            
        Returns:
            List of URLs found
        """
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        return urls
    
    def calculate_confidence(self, signal: Dict[str, Any]) -> str:
        """
        Calculate confidence level for a signal
        
        Args:
            signal: Signal data
            
        Returns:
            Confidence level: 'low', 'medium', or 'high'
        """
        score = 0
        
        # Has company mention
        if signal.get('company_mention'):
            score += 2
        
        # Has role hints
        if signal.get('potential_role'):
            score += 2
        
        # Has location
        if signal.get('location_hints'):
            score += 1
        
        # Has external link
        if signal.get('external_link'):
            score += 1
        
        # Determine confidence
        if score >= 5:
            return 'high'
        elif score >= 3:
            return 'medium'
        else:
            return 'low'
    
    @abstractmethod
    async def collect_signals(self, max_signals: int = 50) -> List[Dict[str, Any]]:
        """
        Collect signals from source
        
        Args:
            max_signals: Maximum number of signals to collect
            
        Returns:
            List of signal dictionaries
        """
        pass
