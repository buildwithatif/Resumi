import re
import logging
from typing import Dict, List, Optional, Any
from collections import Counter

logger = logging.getLogger(__name__)

# spaCy is STRONGLY RECOMMENDED
try:
    import spacy
    # Attempt to load small model, user says they have it
    nlp = spacy.load("en_core_web_sm") 
    SPACY_AVAILABLE = True
except (ImportError, OSError):
    logger.warning("spaCy not available/model not found. Falling back to regex.")
    nlp = None
    SPACY_AVAILABLE = False


# Skill dictionaries for matching (Expanded)
TECHNICAL_SKILLS = {
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
    'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css',
    
    # Frameworks & Libraries
    'react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'spring', 'express',
    'node.js', 'nodejs', '.net', 'rails', 'laravel', 'tensorflow', 'pytorch', 'keras',
    'pandas', 'numpy', 'scipy', 'scikit-learn', 'matplotlib', 'seaborn',
    
    # Databases
    'postgresql', 'postgres', 'mysql', 'mongodb', 'mongo', 'redis', 'elasticsearch', 'cassandra',
    'dynamodb', 'oracle', 'sql server', 'sqlite', 'snowflake', 'redshift', 'bigquery',
    
    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s', 'terraform', 'ansible',
    'jenkins', 'gitlab', 'github actions', 'circleci', 'ci/cd', 'linux', 'bash', 'shell',
    
    # Data & Analytics
    'spark', 'hadoop', 'kafka', 'airflow', 'tableau', 'power bi', 'looker', 'dbt',
    'data analysis', 'machine learning', 'deep learning', 'nlp', 'computer vision',
    
    # Other
    'git', 'agile', 'scrum', 'rest api', 'graphql', 'microservices', 'oauth', 'jwt',
    'testing', 'unit testing', 'selenium', 'cypress', 'jest', 'pytest'
}

BUSINESS_SKILLS = {
    # Finance & Accounting
    'financial modeling', 'financial analysis', 'valuation', 'dcf', 'lbo', 'excel',
    'bloomberg', 'capital iq', 'accounting', 'gaap', 'ifrs', 'budgeting', 'forecasting', 
    'fp&a', 'investment banking', 'private equity', 'venture capital',
    
    # Marketing & Sales
    'market research', 'brand strategy', 'digital marketing', 'seo', 'sem', 'social media',
    'content marketing', 'email marketing', 'crm', 'salesforce', 'hubspot', 'google analytics',
    'marketing automation', 'growth hacking', 'copywriting', 'b2b', 'b2c', 'saas sales',
    
    # Operations & Strategy
    'supply chain', 'logistics', 'operations management', 'process improvement',
    'six sigma', 'lean', 'kaizen', 'project management', 'program management',
    'business strategy', 'corporate strategy', 'consulting', 'management consulting',
    
    # Product
    'product management', 'product strategy', 'roadmap', 'user stories', 'agile',
    'scrum', 'kanban', 'user research', 'a/b testing', 'wireframing', 'figma',
    
    # General
    'powerpoint', 'presentation', 'communication', 'leadership', 'team management',
    'problem solving', 'analytical skills', 'negotiation', 'stakeholder management'
}

ALL_SKILLS = TECHNICAL_SKILLS | BUSINESS_SKILLS

def extract_skills(text: str) -> List[str]:
    """Extract skills using hybrid approach (spaCy NOUN/PROPN + Dictionary Match)"""
    text_lower = text.lower()
    found_skills = set()
    
    # 1. Exact dictionary match (High precision)
    for skill in ALL_SKILLS:
        # Use simple inclusion check but with word boundaries
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill)
            
    # 2. spaCy Noun Chunk Analysis (if available) - finds unknown tech skills
    if SPACY_AVAILABLE and nlp:
        doc = nlp(text)
        # Look for entities that might be skills (e.g., ORG, PRODUCT)
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'WORK_OF_ART', 'LANGUAGE']:
                if ent.text.lower() in ALL_SKILLS:
                    found_skills.add(ent.text.lower())
    
    return sorted(list(found_skills))


def extract_role_family(text: str, job_titles: List[str]) -> str:
    """Determine role family based on text and titles"""
    text_lower = text.lower()
    combined_text = text_lower + ' ' + ' '.join(job_titles).lower()
    
    # Keyword counting for families
    families = {
        'software engineer': ['software', 'developer', 'engineer', 'stack', 'coding'],
        'data scientist': ['data', 'scientist', 'analyst', 'machine learning', 'analytics'],
        'product manager': ['product', 'manager', 'owner', 'roadmap', 'strategy'],
        'designer': ['design', 'ui', 'ux', 'creative', 'graphic'],
        'marketing': ['marketing', 'brand', 'social', 'content', 'growth'],
        'sales': ['sales', 'business development', 'account', 'client'],
        'finance': ['finance', 'accounting', 'investment', 'analyst', 'banking'],
        'hr': ['hr', 'human resources', 'recruiter', 'talent', 'people'],
        'consulting': ['consultant', 'strategy', 'advisory', 'client'],
        'operations': ['operations', 'logistics', 'supply chain', 'process']
    }
    
    scores = {k: 0 for k in families}
    for family, keywords in families.items():
        for kw in keywords:
            if kw in combined_text:
                scores[family] += 1
                
    # Return highest scoring family
    best_family = max(scores, key=scores.get)
    if scores[best_family] == 0:
        return "general"
    return best_family


def extract_experience_years(text: str) -> int:
    """Extract experience years using regex (spaCy dependency parsing is overkill/slow here)"""
    # Look for "X years experience"
    patterns = [
        r'(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?',
    ]
    
    candidates = []
    # Limit search to first 1000 chars (usually summary) or look for surrounding "experience"
    text_lower = text.lower()
    
    # 1. Look specifically in phrases like "5 years of experience"
    strict_matches = re.findall(r'(\d+)\+?\s*years?\s+(?:of\s+)?experience', text_lower)
    if strict_matches:
        candidates.extend([int(x) for x in strict_matches])
        
    # 2. Look for dates (2018 - Present)
    years = re.findall(r'\b(19\d{2}|20\d{2})\b', text)
    if len(years) >= 2:
        years = sorted([int(y) for y in years])
        # Calculate range
        span = years[-1] - years[0]
        # Cap at 30 to avoid parsing birth years etc.
        if 0 < span < 40:
             # Basic heuristic: range of dates mentioned suggests career span (minus typical graduation age etc not accounted for, but rough proxy)
             # Better: just return the span as a *candidate*
             pass # Date logic is brittle without complex parsing, stick to explicit text first
             
    if candidates:
        return max(candidates)
        
    return 1 # Default 1 year if undetected matches "Junior"


def extract_seniority(text: str, experience_years: int) -> str:
    """Determine seniority level from text and experience"""
    text_lower = text.lower()
    
    # Check for explicit seniority keywords
    seniority_keywords = {
        'junior': ['junior', 'entry', 'associate', 'graduate', 'intern'],
        'mid': ['mid-level', 'intermediate', 'engineer ii', 'developer ii'],
        'senior': ['senior', 'sr', 'lead', 'principal', 'staff', 'expert'],
        'lead': ['lead', 'team lead', 'tech lead', 'engineering manager'],
        'principal': ['principal', 'distinguished', 'fellow', 'architect'],
    }
    
    for level, keywords in seniority_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return level
    
    # Fallback to experience-based estimation
    if experience_years < 2:
        return 'junior'
    elif experience_years < 5:
        return 'mid'
    elif experience_years < 8:
        return 'senior'
    else:
        return 'lead'


def extract_profile(text: str) -> Dict[str, Any]:
    """Extract full profile"""
    if not text or len(text) < 10:
        return {}
        
    # 1. Skills
    all_skills = extract_skills(text)
    
    # Separate tools from skills (basic heuristic)
    tool_keywords = {'git', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'jira', 'trello', 'asana', 'slack', 'zoom', 'teams'}
    tools = [s for s in all_skills if s.lower() in tool_keywords]
    skills = [s for s in all_skills if s.lower() not in tool_keywords]
    
    # 2. Titles 
    title_pattern = r'([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,2})\s(?:Manager|Engineer|Developer|Analyst|Consultant|Director|Lead)'
    titles = re.findall(title_pattern, text)
    titles = list(set(titles))[:3]
    
    # 3. Role Family
    primary_role = extract_role_family(text, titles)
    
    # 4. Experience
    exp_years = extract_experience_years(text)
    
    # 5. Education
    education = []
    if 'bachelor' in text.lower() or 'bs ' in text.lower() or 'b.s.' in text.lower(): education.append("Bachelor's")
    if 'master' in text.lower() or 'ms ' in text.lower() or 'm.s.' in text.lower() or 'mba' in text.lower(): education.append("Master's/MBA")
    if 'phd' in text.lower() or 'doctorate' in text.lower(): education.append("PhD")
    
    # 6. Locations
    locations = extract_locations(text)
    
    # 7. Clusters and Seniority
    skill_clusters = cluster_skills(all_skills)
    seniority = extract_seniority(text, exp_years)

    return {
        'primary_role': primary_role,
        'seniority': seniority,
        'skills': skills,
        'tools': tools,
        'experience_years': exp_years,
        'education': education,
        'location_mentions': locations,
        'skill_clusters': skill_clusters,
        'job_titles': titles
    }

def extract_locations(text: str) -> List[str]:
    """Extract locations using spaCy or fallback"""
    locations = set()
    
    if SPACY_AVAILABLE and nlp:
        try:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['GPE', 'LOC']:
                    locations.add(ent.text)
        except Exception as e:
            logger.warning(f"spaCy location extraction failed: {e}")
            
    # Fallback to regex for major cities if spaCy fails or missed them
    common_places = ['Remote', 'Bangalore', 'Bengaluru', 'Mumbai', 'Delhi', 'Hyderabad', 
                    'Chennai', 'Pune', 'New York', 'London', 'San Francisco']
    
    for place in common_places:
        if place.lower() in text.lower():
            locations.add(place)
            
    return sorted(list(locations))

def cluster_skills(skills: List[str]) -> List[str]:
    """Group skills into high-level clusters"""
    clusters = set()
    skill_set = set(s.lower() for s in skills)
    
    cluster_mappings = {
        'backend': {'python', 'java', 'node.js', 'django', 'flask', 'fastapi', 'spring'},
        'frontend': {'react', 'angular', 'vue', 'javascript', 'typescript', 'html', 'css'},
        'cloud': {'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform'},
        'data': {'sql', 'postgresql', 'mysql', 'mongodb', 'data analysis', 'spark'},
        'ml': {'machine learning', 'tensorflow', 'pytorch', 'scikit-learn'},
    }
    
    for cluster, cluster_skills in cluster_mappings.items():
        if skill_set & cluster_skills:
            clusters.add(cluster)
    
    return sorted(list(clusters))
