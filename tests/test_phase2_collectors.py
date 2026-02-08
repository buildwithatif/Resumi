"""
Test Phase 2: Signal Collectors
Tests for LinkedIn, X, and Reddit signal collectors
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.job_sources.social_signals.base_signal_collector import BaseSignalCollector
from backend.job_sources.linkedin_public.parser import LinkedInPublicParser
from backend.job_sources.social_signals.x_scanner import XSignalScanner
from backend.job_sources.social_signals.reddit_scanner import RedditSignalScanner


def test_base_signal_collector():
    """Test base signal collector utilities"""
    print("=" * 60)
    print("TEST 1: Base Signal Collector Utilities")
    print("=" * 60)
    
    # Create a dummy collector
    class DummyCollector(BaseSignalCollector):
        async def collect_signals(self, max_signals=50):
            return []
    
    collector = DummyCollector('test', rate_limit=60)
    
    # Test company extraction
    text = "We're hiring at Razorpay in Mumbai! Also check out Swiggy and Zomato."
    companies = collector.extract_company_mentions(text)
    print(f"\n✅ Company extraction:")
    print(f"   Text: '{text}'")
    print(f"   Found: {companies}")
    
    # Test role extraction
    text2 = "Looking for a Strategy Consultant and Operations Manager"
    roles = collector.extract_role_hints(text2)
    print(f"\n✅ Role extraction:")
    print(f"   Text: '{text2}'")
    print(f"   Found: {roles}")
    
    # Test location extraction
    text3 = "Positions available in Mumbai, Bangalore, and Dubai"
    locations = collector.extract_location_hints(text3)
    print(f"\n✅ Location extraction:")
    print(f"   Text: '{text3}'")
    print(f"   Found: {locations}")
    
    # Test URL extraction
    text4 = "Apply here: https://razorpay.com/careers or https://swiggy.com/jobs"
    urls = collector.extract_urls(text4)
    print(f"\n✅ URL extraction:")
    print(f"   Text: '{text4}'")
    print(f"   Found: {urls}")
    
    # Test confidence calculation
    signal = {
        'company_mention': 'Razorpay',
        'potential_role': 'Strategy Manager',
        'location_hints': ['Mumbai'],
        'external_link': 'https://razorpay.com/careers',
    }
    confidence = collector.calculate_confidence(signal)
    print(f"\n✅ Confidence calculation:")
    print(f"   Signal: {signal}")
    print(f"   Confidence: {confidence}")
    
    return len(companies) >= 2 and len(roles) >= 2 and len(locations) >= 3


def test_linkedin_parser():
    """Test LinkedIn public URL parser"""
    print("\n" + "=" * 60)
    print("TEST 2: LinkedIn Public URL Parser")
    print("=" * 60)
    
    parser = LinkedInPublicParser()
    
    # Test URL validation
    valid_url = "https://www.linkedin.com/jobs/view/123456789"
    invalid_url = "https://example.com/job"
    
    is_valid = parser._is_valid_linkedin_url(valid_url)
    is_invalid = parser._is_valid_linkedin_url(invalid_url)
    
    print(f"\n✅ URL validation:")
    print(f"   Valid URL: {valid_url} → {is_valid}")
    print(f"   Invalid URL: {invalid_url} → {is_invalid}")
    
    # Test job ID extraction
    job_id = parser._extract_job_id(valid_url)
    print(f"\n✅ Job ID extraction:")
    print(f"   URL: {valid_url}")
    print(f"   Job ID: {job_id}")
    
    return is_valid and not is_invalid and job_id == "123456789"


def test_x_scanner():
    """Test X/Twitter signal scanner"""
    print("\n" + "=" * 60)
    print("TEST 3: X/Twitter Signal Scanner")
    print("=" * 60)
    
    scanner = XSignalScanner()
    
    print(f"\n✅ Scanner initialized:")
    print(f"   Source: {scanner.source_name}")
    print(f"   Rate limit: {scanner.rate_limiter.requests_per_minute} req/min")
    
    # Test search queries
    from backend.job_sources.social_signals.x_scanner import SEARCH_QUERIES
    print(f"\n✅ Search queries configured:")
    for query in SEARCH_QUERIES[:3]:
        print(f"   - {query}")
    
    return scanner.source_name == 'x_signal' and len(SEARCH_QUERIES) >= 5


def test_reddit_scanner():
    """Test Reddit signal scanner"""
    print("\n" + "=" * 60)
    print("TEST 4: Reddit Signal Scanner")
    print("=" * 60)
    
    scanner = RedditSignalScanner()
    
    print(f"\n✅ Scanner initialized:")
    print(f"   Source: {scanner.source_name}")
    print(f"   Rate limit: {scanner.rate_limiter.requests_per_minute} req/min")
    
    # Test subreddits
    from backend.job_sources.social_signals.reddit_scanner import SUBREDDITS
    print(f"\n✅ Target subreddits:")
    for sub in SUBREDDITS:
        print(f"   - r/{sub}")
    
    # Test job detection
    job_title = "Hiring: Strategy Manager at McKinsey (Mumbai)"
    job_body = "We're looking for an experienced strategy consultant..."
    is_job = scanner._is_job_related(job_title, job_body)
    
    non_job_title = "What's your favorite food?"
    non_job_body = "Just curious..."
    is_not_job = scanner._is_job_related(non_job_title, non_job_body)
    
    print(f"\n✅ Job detection:")
    print(f"   Job post: '{job_title}' → {is_job}")
    print(f"   Non-job post: '{non_job_title}' → {is_not_job}")
    
    return is_job and not is_not_job


def main():
    """Run all Phase 2 tests"""
    print("\n🧪 PHASE 2: SIGNAL COLLECTORS TESTS\n")
    
    results = {
        "Base Signal Collector": test_base_signal_collector(),
        "LinkedIn Parser": test_linkedin_parser(),
        "X Scanner": test_x_scanner(),
        "Reddit Scanner": test_reddit_scanner(),
    }
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\n{'✅' if total_passed == total_tests else '⚠️'} {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All Phase 2 collectors working correctly!")
        print("\nNote: X and Reddit scanners are placeholders to avoid ToS issues.")
        print("LinkedIn parser is ready for URL parsing when URLs are provided.")
    else:
        print("\n⚠️ Some tests failed. Review the output above.")


if __name__ == "__main__":
    main()
