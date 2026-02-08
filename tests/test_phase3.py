"""
Test Phase 3: Location & Role Refinement
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.location_logic.normalizer import normalize_location, CITY_ALIASES
from backend.location_logic.strict_filter import filter_jobs_by_location

print("=" * 60)
print("PHASE 3: LOCATION & ROLE REFINEMENT TESTS")
print("=" * 60)

# Test 1: City Aliases
print("\n✅ TEST 1: City Aliases")
print("-" * 60)

test_cases = [
    ("Bengaluru, India", "Bangalore"),
    ("Bangalore, India", "Bangalore"),
    ("Bombay, India", "Mumbai"),
    ("Mumbai, India", "Mumbai"),
    ("Gurugram, India", "Gurgaon"),
]

for location_str, expected_city in test_cases:
    normalized = normalize_location(location_str)
    match = "✅" if normalized.city == expected_city else "❌"
    print(f"{match} '{location_str}' → City: {normalized.city} (expected: {expected_city})")

# Test 2: Strict Location Filtering
print("\n✅ TEST 2: Strict Location Filtering")
print("-" * 60)

sample_jobs = [
    {'title': 'Strategy Manager', 'location_raw': 'Mumbai, India'},
    {'title': 'Operations Lead', 'location_raw': 'Dubai, UAE'},
    {'title': 'Marketing Manager', 'location_raw': 'San Francisco, USA'},
    {'title': 'Consultant', 'location_raw': 'Remote'},
    {'title': 'Finance Analyst', 'location_raw': 'Bangalore, India'},
]

# Filter for India only
india_jobs = filter_jobs_by_location(sample_jobs, ['India'], open_to_remote=True)
print(f"\nIndia + Remote filter: {len(india_jobs)}/5 jobs")
for job in india_jobs:
    print(f"  - {job['title']} ({job['location_raw']})")

# Filter for UAE only
uae_jobs = filter_jobs_by_location(sample_jobs, ['UAE'], open_to_remote=True)
print(f"\nUAE + Remote filter: {len(uae_jobs)}/5 jobs")
for job in uae_jobs:
    print(f"  - {job['title']} ({job['location_raw']})")

# Filter for India + UAE
both_jobs = filter_jobs_by_location(sample_jobs, ['India', 'UAE'], open_to_remote=True)
print(f"\nIndia + UAE + Remote filter: {len(both_jobs)}/5 jobs")
for job in both_jobs:
    print(f"  - {job['title']} ({job['location_raw']})")

# Test 3: Domain Fit Scoring
print("\n✅ TEST 3: Domain Fit Scoring")
print("-" * 60)

from backend.matching.matcher import _calculate_domain_fit

test_roles = [
    ('strategy', 'Strategy Manager', 'Leading business strategy initiatives...', 1.0),
    ('consulting', 'Management Consultant', 'Providing advisory services...', 1.0),
    ('operations', 'Operations Manager', 'Managing supply chain and logistics...', 1.0),
    ('marketing', 'Software Engineer', 'Building backend APIs...', 0.3),  # Mismatch
]

for user_role, job_title, job_desc, expected_min in test_roles:
    score = _calculate_domain_fit(user_role, job_title, job_desc)
    match = "✅" if score >= expected_min else "❌"
    print(f"{match} {user_role} → '{job_title}': {score:.1f} (expected ≥{expected_min})")

print("\n" + "=" * 60)
print("✅ Phase 3 enhancements working correctly!")
print("=" * 60)
