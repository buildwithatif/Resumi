# Resumi Ethics & Compliance Policy

## Robots.txt Compliance

Resumi strictly respects `robots.txt` directives from all websites we collect data from.

### Implementation
- **Library**: `robotexclusionrulesparser` (Python)
- **User-Agent**: `ResumiV1/1.0 (Job Recommendation Engine; +https://github.com/resumi)`
- **Behavior**: 
  - Check `robots.txt` before first request to any domain
  - Cache robots.txt rules per domain
  - If disallowed, skip URL and log warning
  - If robots.txt unavailable or error, allow by default (conservative)

### Code Location
- `backend/job_sources/base_collector.py` - `_check_robots_allowed()` method

---

## Rate Limiting

All job sources are rate-limited to avoid overwhelming servers.

### Current Limits
- **Greenhouse**: 60 requests/minute
- **Lever**: 60 requests/minute  
- **RemoteOK**: 60 requests/minute
- **Future sources**: Will follow documented API limits or default to 60/min

### Implementation
- `RateLimiter` class in `base_collector.py`
- Enforces minimum interval between requests
- Async-safe (uses event loop time)

---

## Data Sources Policy

### Allowed Sources
1. **Public Career Pages** (Greenhouse, Lever, Workday)
   - Only public, non-gated job boards
   - No login required
   - Respects robots.txt

2. **Public Job Boards** (RemoteOK, etc.)
   - Public APIs or RSS feeds
   - No authentication required

3. **Social Signals** (V2 - Future)
   - **X (Twitter)**: Public posts only, no login
   - **Reddit**: Public subreddits, read-only
   - **LinkedIn**: Public URLs only (no logged-in scraping)

### Forbidden Practices
❌ **Never**:
- Scrape behind login walls
- Use private APIs without permission
- Automate with user accounts
- Violate Terms of Service
- Ignore robots.txt
- Overwhelm servers (no rate limiting)

---

## Data Privacy

### User Data
- **Resume Storage**: Stored locally in `data/resumes/` (V1) or encrypted DB (V2)
- **No Sharing**: User resumes are NEVER shared with third parties
- **No Tracking**: No analytics on user behavior (V1)

### Job Data
- **Public Only**: Only collect publicly available job postings
- **Attribution**: Always store source URL and company name
- **Caching**: Jobs cached for 24 hours, then refreshed

---

## Transparency

### Source Attribution
Every job recommendation includes:
- Source name (e.g., "Greenhouse", "RemoteOK")
- Original posting URL
- Company name

### Explanation
Every recommendation includes:
- Why it matched (skills, location, role)
- What's missing (skill gaps)
- Match score breakdown

---

## Compliance Checklist

Before adding any new job source:
- [ ] Check if source is public (no login required)
- [ ] Verify robots.txt allows our User-Agent
- [ ] Implement rate limiting (default: 60/min)
- [ ] Add source attribution to job schema
- [ ] Document in `docs/api.md`
- [ ] Test error handling (404, 500, timeout)

---

## Contact

For questions about our data collection practices:
- Email: ethics@resumi.com (placeholder)
- GitHub: https://github.com/resumi

---

**Last Updated**: 2026-01-20  
**Version**: V1.0
