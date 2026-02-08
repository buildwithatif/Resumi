"""
ResumiV1 FastAPI Application
Main orchestration layer
"""

import sys
from pathlib import Path

# Add parent directory to Python path for backend imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import asyncio
from typing import Optional
import uuid
from datetime import datetime, timedelta

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Backend imports
from backend.resume_ingestion.parser import parse_resume, validate_resume_content, ResumeParsingError
from backend.profile_extraction.extractor import extract_profile
from backend.profile_extraction.schemas import ProfileSchema, UserPreferences
from backend.job_sources.orchestrator import JobOrchestrator
from backend.job_normalization.normalizer import normalize_job, deduplicate_jobs, NormalizedJob
from backend.matching.matcher import match_jobs
from backend.explanations.generator import generate_explanation
from backend.external_search.generator import generate_external_searches
from backend.external_search.schemas import SearchGenerationRequest
from backend.unified_discovery.orchestrator import discover_all_jobs
from backend.unified_discovery.schemas import JobDiscoveryRequest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/resumi.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ResumiV1",
    description="Resume-first job recommendation engine",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session storage (in-memory for V1)
sessions = {}

# Data directory
DATA_DIR = Path(__file__).parent.parent / 'data'
RESUMES_DIR = DATA_DIR / 'resumes'
RESUMES_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files for frontend with proper precedence
frontend_dir = Path(__file__).parent.parent / 'frontend'

if frontend_dir.exists():
    # 1. Mount /frontend for direct access to any file
    app.mount("/frontend", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
    
    # 2. Mount /dashboard specifically
    dashboard_dir = frontend_dir / 'dashboard'
    if dashboard_dir.exists():
        app.mount("/dashboard", StaticFiles(directory=str(dashboard_dir), html=True), name="dashboard")
    
    # 3. Mount /static for general assets
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


class PreferencesRequest(BaseModel):
    """Request model for preferences"""
    session_id: str
    career_goals: Optional[str] = None
    preferred_locations: list[str] = []
    open_to_relocation: bool = False
    open_to_international: bool = False
    remote_only: bool = False


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve V2 Dashboard (Dynamic with API Integration)"""
    # Serve the newly created dynamic.html
    html_path = Path(__file__).parent.parent / 'frontend' / 'dashboard' / 'dynamic.html'
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding='utf-8'), status_code=200)
    return HTMLResponse(content="<h1>ResumiV2</h1><p>Dashboard not found. Please check frontend/dashboard/dynamic.html</p>", status_code=404)


@app.get("/upload", response_class=HTMLResponse)
async def upload_page():
    """Serve upload page"""
    html_path = Path(__file__).parent.parent / 'frontend' / 'upload' / 'index.html'
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding='utf-8'), status_code=200)
    return HTMLResponse(content="<h1>ResumiV2</h1><p>Upload page not found</p>", status_code=200)


@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and parse resume
    
    Returns profile and session ID
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.pdf', '.docx')):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Only PDF and DOCX are supported."
            )
        
        # Save file temporarily
        session_id = str(uuid.uuid4())
        file_path = RESUMES_DIR / f"{session_id}_{file.filename}"
        
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # Parse resume
        try:
            text, file_type = parse_resume(file_path)
            
            # Validate content
            if not validate_resume_content(text):
                raise HTTPException(
                    status_code=422,
                    detail="Resume content appears invalid. Please upload a proper resume."
                )
            
            # Extract profile
            profile_dict = extract_profile(text)
            profile = ProfileSchema(**profile_dict)
            
            # Store in session
            sessions[session_id] = {
                'profile': profile,
                'preferences': None,
                'created_at': datetime.utcnow(),
                'file_path': file_path
            }
            
            logger.info(f"Successfully processed resume for session {session_id}")
            
            return {
                'success': True,
                'profile': profile.dict(),
                'session_id': session_id
            }
            
        except ResumeParsingError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(f"Profile extraction failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to extract profile from resume"
            )
        finally:
            # Clean up file
            if file_path.exists():
                file_path.unlink()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume upload failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/set-preferences")
async def set_preferences(request: PreferencesRequest):
    """
    Store user preferences
    """
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    preferences = UserPreferences(
        career_goals=request.career_goals,
        preferred_locations=request.preferred_locations,
        open_to_relocation=request.open_to_relocation,
        open_to_international=request.open_to_international,
        remote_only=request.remote_only
    )
    
    sessions[request.session_id]['preferences'] = preferences
    
    logger.info(f"Preferences set for session {request.session_id}")
    
    return {'success': True, 'message': 'Preferences saved'}


@app.get("/api/recommendations")
async def get_recommendations(session_id: str):
    """
    Get job recommendations
    
    Triggers job collection, normalization, matching, and explanation generation
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    profile = session['profile']
    preferences = session.get('preferences')
    
    if not preferences:
        # Use default preferences
        preferences = UserPreferences()
    
    try:
        logger.info(f"Starting recommendation pipeline for session {session_id}")
        
        # 1. Collect jobs
        orchestrator = JobOrchestrator(DATA_DIR)
        raw_jobs = await orchestrator.collect_all_jobs(max_jobs_per_source=100)
        
        if not raw_jobs:
            return {
                'success': False,
                'error': 'No jobs found',
                'suggestions': [
                    'Try again later as job sources may be temporarily unavailable',
                    'Check your internet connection'
                ]
            }
        
        # 2. Normalize jobs
        normalized_jobs = []
        for raw_job in raw_jobs:
            normalized = normalize_job(raw_job)
            if normalized:
                normalized_jobs.append(normalized)
        
        # 3. Deduplicate
        unique_jobs = deduplicate_jobs(normalized_jobs)
        
        if not unique_jobs:
            return {
                'success': False,
                'error': 'No valid jobs after processing',
                'suggestions': ['Try again later']
            }
        
        # 4. Match and rank
        matches = match_jobs(unique_jobs, profile, preferences, max_results=20)
        
        if not matches:
            return {
                'success': False,
                'error': 'No jobs found matching your profile',
                'suggestions': [
                    'Try broadening your location preferences',
                    'Consider remote-only roles',
                    'Adjust your career goals'
                ]
            }
        
        # 5. Generate explanations
        recommendations = []
        for match in matches:
            explanation = generate_explanation(match, profile)
            if explanation:
                recommendations.append({
                    'id': match.job.id,
                    'title': match.job.title,
                    'company': match.job.company,
                    'location': match.job.location,
                    'source': match.job.source,
                    'apply_url': match.job.apply_url,
                    'match_score': round(match.total_score, 2),
                    'explanation': explanation
                })
        
        logger.info(f"Returning {len(recommendations)} recommendations")
        
        return {
            'success': True,
            'total_jobs_collected': len(raw_jobs),
            'total_jobs_matched': len(matches),
            'recommendations': recommendations
        }
    
    except Exception as e:
        logger.error(f"Recommendation pipeline failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate recommendations"
        )


@app.post("/api/external-searches")
async def get_external_searches(request: SearchGenerationRequest):
    """
    Generate external search URLs for Naukri and Instahyre
    
    Returns optimized search URLs based on resume intelligence
    """
    try:
        logger.info(f"Generating external searches for roles: {request.primary_roles}")
        
        response = generate_external_searches(request)
        
        logger.info(f"Generated {response.total_recommendations} search URLs")
        
        return {
            'success': True,
            'naukri_searches': [search.dict() for search in response.naukri_searches],
            'instahyre_searches': [search.dict() for search in response.instahyre_searches],
            'total_recommendations': response.total_recommendations,
            'metadata': response.generation_metadata
        }
    
    except Exception as e:
        logger.error(f"External search generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate external searches"
        )


@app.post("/api/discover-jobs")
async def discover_jobs_unified(request: JobDiscoveryRequest):
    """
    Unified job discovery across all platforms
    
    Returns:
    - Actual job listings from LinkedIn, Indeed APIs
    - Smart search URLs for Naukri, Instahyre
    """
    try:
        logger.info(f"Starting unified job discovery for: {request.primary_roles}")
        
        response = discover_all_jobs(request)
        
        logger.info(f"Discovery complete: {response.total_results} total results")
        
        return {
            'success': True,
            'api_jobs': [job.dict() for job in response.api_jobs],
            'search_recommendations': [job.dict() for job in response.search_recommendations],
            'total_api_jobs': response.total_api_jobs,
            'total_search_urls': response.total_search_urls,
            'total_results': response.total_results,
            'metadata': response.search_metadata
        }
    
    except Exception as e:
        logger.error(f"Unified job discovery failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to discover jobs"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {'status': 'healthy', 'version': '1.0.0'}


# Mount static files for frontend
frontend_dir = Path(__file__).parent.parent / 'frontend'
if frontend_dir.exists():
    # Mount dashboard static files
    dashboard_dir = frontend_dir / 'dashboard'
    if dashboard_dir.exists():
        app.mount("/dashboard", StaticFiles(directory=str(dashboard_dir), html=True), name="dashboard")
    
    # Mount general static files
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
