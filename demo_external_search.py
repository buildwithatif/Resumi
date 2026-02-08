"""
Quick demo of external search URL generation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.external_search.generator import generate_external_searches
from backend.external_search.schemas import SearchGenerationRequest

# Sample MBA Operations profile
request = SearchGenerationRequest(
    primary_roles=["Operations Analyst"],
    role_family="Operations",
    years_of_experience=2.5,
    top_skills=["Excel", "PowerPoint", "Process Improvement"],
    preferred_locations=["Bangalore", "Mumbai"],
    location_flexibility="flexible"
)

# Generate searches
response = generate_external_searches(request)

print("\n🎯 GENERATED SEARCH URLs FOR MBA OPERATIONS PROFILE\n")
print(f"Profile: {request.primary_roles[0]}, {request.years_of_experience} years")
print(f"Locations: {', '.join(request.preferred_locations)}\n")

print("=" * 80)
print("NAUKRI SEARCH URLs")
print("=" * 80)

for i, search in enumerate(response.naukri_searches, 1):
    print(f"\n{i}. {search.role_focus} in {search.location_focus}")
    print(f"   📊 Relevance: {search.relevance_score}/10")
    print(f"   💡 Why: {search.why_this_search}")
    print(f"   🔗 URL: {search.search_url}\n")

print("=" * 80)
print("INSTAHYRE SEARCH URLs")
print("=" * 80)

for i, search in enumerate(response.instahyre_searches, 1):
    print(f"\n{i}. {search.role_focus} in {search.location_focus}")
    print(f"   📊 Relevance: {search.relevance_score}/10")
    print(f"   💡 Why: {search.why_this_search}")
    print(f"   🔗 URL: {search.search_url}\n")

print("=" * 80)
print(f"✅ Total: {response.total_recommendations} optimized search URLs generated")
print("=" * 80)
