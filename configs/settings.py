"""
ResumiV1 Configuration Settings
"""

from typing import Dict, List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Application
    APP_NAME: str = "ResumiV1"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # File Upload
    MAX_RESUME_SIZE_MB: int = 5
    ALLOWED_RESUME_EXTENSIONS: List[str] = [".pdf", ".docx"]
    
    # Job Collection
    MAX_JOBS_PER_SOURCE: int = 100
    TOTAL_JOB_LIMIT: int = 500
    JOB_CACHE_HOURS: int = 24
    
    # Rate Limiting (requests per minute)
    RATE_LIMITS: Dict[str, int] = {
        "greenhouse": 60,
        "lever": 60,
        "workday": 30,
        "remoteok": 10,
        "twitter": 1,  # 15 per 15 minutes = 1 per minute average
    }
    
    # Matching Weights
    LOCATION_WEIGHT: float = 0.5
    SKILL_WEIGHT: float = 0.4
    CAREER_WEIGHT: float = 0.1
    
    # Matching Thresholds
    MIN_SIMILARITY_SCORE: float = 0.3
    MAX_RECOMMENDATIONS: int = 20
    
    # Location Scoring
    LOCATION_SCORES: Dict[str, float] = {
        "exact_city": 1.0,
        "same_country": 0.7,
        "same_region": 0.4,
        "remote": 1.0,
    }
    
    # Career Logic Bonuses/Penalties
    CAREER_ADJUSTMENTS: Dict[str, float] = {
        "lateral": 0.0,
        "promotion": 0.2,
        "downgrade": -0.3,
    }
    
    # Seniority Levels
    SENIORITY_LEVELS: List[str] = ["junior", "mid", "senior", "lead", "principal"]
    
    # Job Sources Configuration
    JOB_SOURCES: Dict[str, Dict] = {
        "greenhouse": {
            "enabled": True,
            "base_url": "https://boards-api.greenhouse.io/v1/boards/{company}/jobs",
            "rate_limit": 60,
        },
        "lever": {
            "enabled": True,
            "base_url": "https://api.lever.co/v0/postings/{company}",
            "rate_limit": 60,
        },
        "remoteok": {
            "enabled": True,
            "base_url": "https://remoteok.com/api",
            "rate_limit": 10,
        },
    }
    
    # Data Directories
    DATA_DIR: str = "data"
    RESUMES_DIR: str = "data/resumes"
    JOBS_RAW_DIR: str = "data/jobs_raw"
    JOBS_NORMALIZED_DIR: str = "data/jobs_normalized"
    
    # spaCy Model
    SPACY_MODEL: str = "en_core_web_md"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/resumi.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
