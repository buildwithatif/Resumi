# ResumiV1 API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Upload Resume
**POST** `/api/upload-resume`

Upload a resume file (PDF or DOCX) and extract profile.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `file`: Resume file (PDF or DOCX, max 5MB)

**Response:**
```json
{
  "success": true,
  "profile": {
    "primary_role": "Software Engineer",
    "seniority": "senior",
    "skills": ["Python", "FastAPI", "React"],
    "tools": ["Git", "Docker", "AWS"],
    "experience_years": 5,
    "education": ["BS Computer Science"],
    "location_mentions": ["San Francisco"],
    "skill_clusters": ["backend", "cloud"]
  },
  "session_id": "abc123"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Failed to parse resume",
  "details": "Unsupported file format"
}
```

---

### 2. Set Preferences
**POST** `/api/set-preferences`

Store user preferences for job matching.

**Request:**
```json
{
  "session_id": "abc123",
  "career_goals": "Looking for senior backend roles in cloud infrastructure",
  "preferred_locations": ["San Francisco", "Remote"],
  "open_to_relocation": false,
  "open_to_international": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Preferences saved"
}
```

---

### 3. Get Recommendations
**GET** `/api/recommendations?session_id=abc123`

Trigger job collection, matching, and return top recommendations.

**Query Parameters:**
- `session_id`: Session identifier from upload response

**Response:**
```json
{
  "success": true,
  "total_jobs_collected": 342,
  "total_jobs_matched": 87,
  "recommendations": [
    {
      "id": "job_hash_123",
      "title": "Senior Software Engineer",
      "company": "TechCorp",
      "location": {
        "city": "San Francisco",
        "country": "USA",
        "type": "hybrid"
      },
      "source": "greenhouse",
      "apply_url": "https://...",
      "match_score": 0.89,
      "explanation": {
        "why_match": "Strong alignment with your backend and cloud infrastructure experience",
        "skill_matches": ["Python", "AWS", "Docker", "Kubernetes"],
        "skill_gaps": ["Terraform"],
        "location_reasoning": "Exact city match with your preferred location"
      }
    }
  ]
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "No jobs found matching your profile",
  "suggestions": [
    "Try broadening your location preferences",
    "Consider remote-only roles"
  ]
}
```

---

## Status Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid input or missing parameters
- `413 Payload Too Large`: Resume file exceeds 5MB
- `422 Unprocessable Entity`: Resume parsing failed
- `500 Internal Server Error`: Server error

## Rate Limits

No rate limits for V1 (single-user, local deployment).

## Session Management

Sessions are temporary and stored in memory. They expire after 1 hour of inactivity.
