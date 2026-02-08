"""
Test script for external search generator
Demonstrates how to generate Naukri and Instahyre search URLs
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.external_search.generator import generate_external_searches
from backend.external_search.schemas import SearchGenerationRequest


def test_external_search_generation():
    """Test external search URL generation"""
    
    print("=" * 70)
    print("EXTERNAL SEARCH URL GENERATOR TEST")
    print("=" * 70)
    
    # Sample request (MBA Operations profile)
    request = SearchGenerationRequest(
        primary_roles=["Operations Analyst"],
        role_family="Operations",
        years_of_experience=2.5,
        top_skills=["Excel", "PowerPoint", "Process Improvement", "Project Management"],
        preferred_locations=["Bangalore", "Mumbai"],
        location_flexibility="flexible",
        experience_flexibility=True,
        include_mba_tag=True
    )
    
    print("\n📥 INPUT:")
    print(f"   Primary Role: {request.primary_roles[0]}")
    print(f"   Role Family: {request.role_family}")
    print(f"   Experience: {request.years_of_experience} years")
    print(f"   Locations: {', '.join(request.preferred_locations)}")
    print(f"   Flexibility: {request.location_flexibility}")
    
    # Generate searches
    print("\n🔄 GENERATING SEARCH URLs...")
    response = generate_external_searches(request)
    
    # Display results
    print(f"\n📊 RESULTS: {response.total_recommendations} recommendations generated")
    
    print("\n" + "=" * 70)
    print("NAUKRI SEARCH URLs")
    print("=" * 70)
    
    for i, search in enumerate(response.naukri_searches, 1):
        print(f"\n{i}. {search.role_focus} in {search.location_focus}")
        print(f"   Experience: {search.experience_band}")
        print(f"   Relevance: {search.relevance_score}/10")
        print(f"   Why: {search.why_this_search}")
        print(f"   URL: {search.search_url}")
    
    print("\n" + "=" * 70)
    print("INSTAHYRE SEARCH URLs")
    print("=" * 70)
    
    for i, search in enumerate(response.instahyre_searches, 1):
        print(f"\n{i}. {search.role_focus} in {search.location_focus}")
        print(f"   Experience: {search.experience_band}")
        print(f"   Relevance: {search.relevance_score}/10")
        print(f"   Why: {search.why_this_search}")
        print(f"   URL: {search.search_url}")
    
    print("\n" + "=" * 70)
    print("GENERATION METADATA")
    print("=" * 70)
    
    metadata = response.generation_metadata
    print(f"\n   Expanded Roles: {', '.join(metadata['expanded_roles'])}")
    print(f"   Top Roles: {', '.join(metadata['top_roles'])}")
    print(f"   Experience Bands: {', '.join(metadata['experience_bands'])}")
    print(f"   Normalized Locations: {', '.join(metadata['normalized_locations'])}")
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)
    
    return response


if __name__ == "__main__":
    test_external_search_generation()
