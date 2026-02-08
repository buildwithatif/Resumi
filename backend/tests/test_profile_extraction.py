"""
Tests for Profile Extraction
"""

import pytest
from backend.profile_extraction.extractor import (
    extract_skills,
    extract_experience_years,
    extract_seniority,
    extract_education,
    extract_role_family,
    cluster_skills,
)


def test_extract_skills():
    """Test skill extraction"""
    text = "Proficient in Python, JavaScript, React, and AWS. Experience with Docker and Kubernetes."
    skills = extract_skills(text)
    
    assert 'python' in skills
    assert 'javascript' in skills
    assert 'react' in skills
    assert 'aws' in skills
    assert 'docker' in skills
    assert 'kubernetes' in skills


def test_extract_experience_years():
    """Test experience years extraction"""
    text = "5+ years of experience in software development"
    years = extract_experience_years(text)
    assert years == 5


def test_extract_experience_years_from_dates():
    """Test experience extraction from date ranges"""
    text = """
    Software Engineer, TechCorp (2020 - 2023)
    Developer, StartupXYZ (2018 - 2020)
    """
    years = extract_experience_years(text)
    assert years >= 2  # At least 2 jobs


def test_extract_seniority_explicit():
    """Test seniority extraction with explicit keywords"""
    text = "Senior Software Engineer with 6 years of experience"
    seniority = extract_seniority(text, 6)
    assert seniority == 'senior'


def test_extract_seniority_from_experience():
    """Test seniority inference from experience years"""
    seniority = extract_seniority("Software Engineer", 1)
    assert seniority == 'junior'
    
    seniority = extract_seniority("Software Engineer", 4)
    assert seniority == 'mid'
    
    seniority = extract_seniority("Software Engineer", 7)
    assert seniority == 'senior'


def test_extract_education():
    """Test education extraction"""
    text = "Bachelor of Science in Computer Science from MIT. MBA from Harvard."
    education = extract_education(text)
    
    assert len(education) >= 1
    assert any('bachelor' in e.lower() or 'bs' in e.lower() for e in education)


def test_extract_role_family():
    """Test role family extraction"""
    text = "Backend developer with expertise in API development"
    job_titles = ["Backend Engineer", "Software Developer"]
    
    role = extract_role_family(text, job_titles)
    assert role in ['backend', 'software engineer']


def test_cluster_skills():
    """Test skill clustering"""
    skills = ['python', 'django', 'react', 'aws', 'docker', 'postgresql']
    clusters = cluster_skills(skills)
    
    assert 'backend' in clusters
    assert 'frontend' in clusters
    assert 'cloud' in clusters
    assert 'data' in clusters
