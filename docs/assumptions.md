# ResumiV1 - Technical Assumptions & Constraints

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Resume Parsing**: 
  - PyPDF2 for PDF files
  - python-docx for DOCX files
- **NLP**: spaCy (en_core_web_md model) for skill extraction and semantic similarity
- **HTTP Client**: httpx for async job collection
- **Data Storage**: JSON files (no database for V1)

### Frontend
- **Stack**: Vanilla HTML/CSS/JavaScript
- **Styling**: Modern CSS with gradients, animations, glassmorphism
- **No Framework**: Keep V1 simple and dependency-free

## Constraints & Assumptions

### Legal & Ethical
1. **Robots.txt Compliance**: All scrapers will check and respect robots.txt
2. **Rate Limiting**: Maximum 1 request per second per domain
3. **Public Data Only**: No authentication bypass or private API usage
4. **Attribution**: All job sources will be clearly attributed

### Job Sources (V1)
1. **Career Pages**:
   - Greenhouse: Public API available
   - Lever: Public postings API
   - Workday: Public job feeds only
2. **Public Boards**:
   - RemoteOK: Public API
   - We Work Remotely: RSS feed
3. **Social Signals**:
   - X/Twitter: Public keyword search (limited to avoid rate limits)
4. **LinkedIn**:
   - Public job URLs only (no scraping of logged-in content)

### Performance Assumptions
- **Job Collection**: Target 100-500 jobs per run
- **Processing Time**: < 30 seconds for full pipeline
- **Resume Size**: Max 5MB file size
- **Concurrent Requests**: Max 5 concurrent job source requests

### Matching Logic Assumptions
1. **Skill Extraction**: Use spaCy NER + custom skill dictionary
2. **Similarity Threshold**: Minimum 0.3 similarity score to be considered
3. **Location Scoring**:
   - Exact city match: 1.0
   - Same country: 0.7
   - Same region: 0.4
   - Remote role: 1.0 (overrides location mismatch)
4. **Career Logic**:
   - Junior → Mid: +0.2 bonus
   - Mid → Senior: +0.2 bonus
   - Senior → Senior: 0.0 (neutral)
   - Downgrade: -0.3 penalty

### Data Retention
- **Resumes**: Deleted after session ends (not persisted)
- **Jobs**: Cached for 24 hours, then refreshed
- **User Preferences**: Session-only (no persistence)

### Error Handling
- **Failed Job Sources**: Log and continue (don't block pipeline)
- **Resume Parsing Errors**: Return user-friendly error message
- **Empty Results**: Show helpful message with suggestions
- **Rate Limit Exceeded**: Skip source and log warning

## V1 Exclusions (Explicit)
- ❌ User authentication or accounts
- ❌ Resume storage or history
- ❌ Salary prediction or ranges
- ❌ Resume rewriting or optimization
- ❌ Email notifications
- ❌ One-click apply
- ❌ Multi-language support (English only)
- ❌ Advanced analytics or dashboards
- ❌ API for third-party integrations

## Environment Requirements

### Python Dependencies
```
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
PyPDF2==3.0.1
python-docx==1.1.0
spacy==3.7.2
httpx==0.25.1
pydantic==2.5.0
pytest==7.4.3
```

### spaCy Model
```bash
python -m spacy download en_core_web_md
```

### Development Server
- Local development only (no production deployment for V1)
- Port: 8000 (FastAPI default)
- Frontend served via FastAPI static files

## File Size Limits
- Resume upload: 5MB max
- Job description: 10KB max (truncate if longer)

## Rate Limits (Per Source)
- Greenhouse: 60 requests/minute
- Lever: 60 requests/minute
- Workday: 30 requests/minute
- RemoteOK: 10 requests/minute
- X/Twitter: 15 requests/15 minutes
- LinkedIn: Manual URLs only (no automated scraping)
