"""
Tests for Resume Parser
"""

import pytest
from pathlib import Path
from backend.resume_ingestion.parser import (
    parse_resume,
    validate_resume_content,
    ResumeParsingError
)


def test_validate_resume_content_valid():
    """Test validation with valid resume content"""
    valid_text = """
    John Doe
    Software Engineer
    
    Experience:
    - Senior Developer at TechCorp (2020-2023)
    - Junior Developer at StartupXYZ (2018-2020)
    
    Education:
    BS Computer Science, University of California
    
    Skills: Python, JavaScript, React, AWS
    """
    
    assert validate_resume_content(valid_text) is True


def test_validate_resume_content_too_short():
    """Test validation with too short content"""
    short_text = "John Doe"
    assert validate_resume_content(short_text) is False


def test_validate_resume_content_missing_indicators():
    """Test validation with content missing resume indicators"""
    invalid_text = "This is a long text but it doesn't contain any resume-related keywords. " * 10
    assert validate_resume_content(invalid_text) is False


def test_parse_resume_unsupported_format():
    """Test parsing with unsupported file format"""
    fake_path = Path("resume.txt")
    
    with pytest.raises(ResumeParsingError, match="Unsupported file format"):
        # Create a mock file
        fake_path.touch()
        try:
            parse_resume(fake_path)
        finally:
            fake_path.unlink()


def test_parse_resume_file_not_found():
    """Test parsing with non-existent file"""
    with pytest.raises(ResumeParsingError, match="File not found"):
        parse_resume(Path("nonexistent.pdf"))
