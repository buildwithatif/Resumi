"""
Test script for Phase 0 enhancements
Tests business skills extraction, non-tech roles, and India/UAE location support
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.profile_extraction.extractor import extract_skills, extract_role_family, extract_profile
from backend.location_logic.normalizer import normalize_location, score_location_match

def test_business_skills():
    """Test business skills extraction"""
    print("=" * 60)
    print("TEST 1: Business Skills Extraction")
    print("=" * 60)
    
    mba_resume = """
    MBA Graduate from IIM Bangalore
    
    Skills: Financial Modeling, Excel, PowerPoint, Market Research, 
    Business Strategy, Stakeholder Management, Project Management,
    Salesforce, Google Analytics, Supply Chain Management
    
    Experience:
    - Strategy Consultant at McKinsey & Company
    - Operations Manager at Flipkart
    - Marketing Analyst at Unilever
    """
    
    skills = extract_skills(mba_resume)
    print(f"\n✅ Extracted {len(skills)} skills:")
    print(f"   {', '.join(skills[:10])}...")
    
    expected_business_skills = ['excel', 'powerpoint', 'market research', 'business strategy', 
                                'stakeholder management', 'project management', 'salesforce']
    found = [s for s in expected_business_skills if s in skills]
    print(f"\n✅ Found {len(found)}/{len(expected_business_skills)} expected business skills")
    
    return len(found) >= 5  # Pass if at least 5 business skills found

def test_non_tech_roles():
    """Test non-tech role family detection"""
    print("\n" + "=" * 60)
    print("TEST 2: Non-Tech Role Detection")
    print("=" * 60)
    
    test_cases = [
        ("Strategy Consultant at McKinsey", "strategy"),
        ("Operations Manager at Swiggy", "operations"),
        ("Marketing Manager at Zomato", "marketing"),
        ("Financial Analyst at Goldman Sachs", "finance"),
        ("HR Manager at Google", "hr"),
    ]
    
    passed = 0
    for text, expected_role in test_cases:
        detected = extract_role_family(text, [text])
        match = "✅" if expected_role in detected.lower() else "❌"
        print(f"{match} '{text}' → {detected} (expected: {expected_role})")
        if expected_role in detected.lower():
            passed += 1
    
    print(f"\n✅ Passed {passed}/{len(test_cases)} role detection tests")
    return passed >= 3  # Pass if at least 3 correct

def test_india_uae_locations():
    """Test India/UAE location normalization"""
    print("\n" + "=" * 60)
    print("TEST 3: India/UAE Location Support")
    print("=" * 60)
    
    test_locations = [
        "Mumbai, India",
        "Bangalore, India",
        "Dubai, UAE",
        "Abu Dhabi, UAE",
        "Gurgaon, India",
    ]
    
    passed = 0
    for loc_str in test_locations:
        normalized = normalize_location(loc_str)
        expected_country = "India" if "India" in loc_str else "UAE"
        match = "✅" if normalized.country == expected_country else "❌"
        print(f"{match} '{loc_str}' → City: {normalized.city}, Country: {normalized.country}")
        if normalized.country == expected_country:
            passed += 1
    
    print(f"\n✅ Passed {passed}/{len(test_locations)} location tests")
    return passed >= 4  # Pass if at least 4 correct

def test_full_profile_extraction():
    """Test full profile extraction with MBA resume"""
    print("\n" + "=" * 60)
    print("TEST 4: Full MBA Profile Extraction")
    print("=" * 60)
    
    mba_resume = """
    Rahul Sharma
    Mumbai, India
    
    EDUCATION
    MBA from IIM Ahmedabad (2020-2022)
    B.Tech in Computer Science from IIT Delhi (2015-2019)
    
    EXPERIENCE
    Strategy Consultant | McKinsey & Company | Mumbai | 2022-Present
    - Led market entry strategy for Fortune 500 client in UAE
    - Conducted competitive analysis and financial modeling
    - Managed cross-functional teams of 5-7 consultants
    
    Operations Intern | Flipkart | Bangalore | Summer 2021
    - Optimized supply chain processes using Six Sigma
    - Reduced logistics costs by 15% through process improvement
    
    SKILLS
    Business Strategy, Financial Modeling, Excel, PowerPoint, Market Research,
    Stakeholder Management, Project Management, Data Analysis, SQL, Python
    """
    
    try:
        profile = extract_profile(mba_resume)
        
        print(f"\n✅ Profile extracted successfully!")
        print(f"   Primary Role: {profile['primary_role']}")
        print(f"   Seniority: {profile['seniority']}")
        print(f"   Skills: {len(profile['skills'])} found")
        print(f"   Locations: {', '.join(profile['location_mentions'])}")
        print(f"   Skill Clusters: {', '.join(profile['skill_clusters'])}")
        
        # Check if business skills were detected
        business_skills_found = any(skill in ['excel', 'powerpoint', 'market research', 
                                               'business strategy', 'financial modeling'] 
                                   for skill in profile['skills'])
        
        # Check if non-tech role detected
        is_business_role = profile['primary_role'] in ['strategy', 'consulting', 'operations']
        
        print(f"\n   Business skills detected: {'✅' if business_skills_found else '❌'}")
        print(f"   Business role detected: {'✅' if is_business_role else '❌'}")
        
        return business_skills_found or is_business_role
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n🧪 PHASE 0 ENHANCEMENT TESTS\n")
    
    results = {
        "Business Skills": test_business_skills(),
        "Non-Tech Roles": test_non_tech_roles(),
        "India/UAE Locations": test_india_uae_locations(),
        "Full Profile": test_full_profile_extraction(),
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
        print("\n🎉 All Phase 0 enhancements working correctly!")
    else:
        print("\n⚠️ Some tests failed. Review the output above.")

if __name__ == "__main__":
    main()
