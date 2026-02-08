"""
API Key Configuration
Load API keys from environment variables
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# API Keys
LINKEDIN_API_KEY = os.getenv('LINKEDIN_API_KEY', '')
INDEED_API_KEY = os.getenv('INDEED_API_KEY', '')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', '')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', '')

def has_linkedin_api():
    """Check if LinkedIn API key is configured"""
    return bool(LINKEDIN_API_KEY)

def has_indeed_api():
    """Check if Indeed API key is configured"""
    return bool(INDEED_API_KEY)

def get_api_status():
    """Get status of all API integrations"""
    return {
        'linkedin': has_linkedin_api(),
        'indeed': has_indeed_api(),
        'twitter': bool(TWITTER_API_KEY and TWITTER_API_SECRET)
    }
