import httpx
import json

# Test the API endpoint
url = "http://localhost:8000/api/discover-jobs"
payload = {
    "primary_roles": ["Business Analyst"],
    "role_family": "Operations",
    "years_of_experience": 3,
    "top_skills": ["Excel", "PowerPoint"],
    "preferred_locations": ["Bangalore"],
    "location_flexibility": "flexible"
}

print("Testing API endpoint...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("-" * 50)

try:
    response = httpx.post(url, json=payload, timeout=30.0)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nAPI Response:")
        print(f"  Success: {data.get('success', False)}")
        print(f"  Total API Jobs: {data.get('total_api_jobs', 0)}")
        print(f"  Total Search URLs: {data.get('total_search_urls', 0)}")
        print(f"  Total Results: {data.get('total_results', 0)}")
        
        if data.get('api_jobs'):
            print(f"\nFirst 3 API Jobs:")
            for i, job in enumerate(data['api_jobs'][:3], 1):
                print(f"  {i}. {job['title']} at {job['company']} ({job['source_platform']})")
        
        if data.get('search_recommendations'):
            print(f"\nFirst 2 Search URLs:")
            for i, job in enumerate(data['search_recommendations'][:2], 1):
                print(f"  {i}. {job['title']} - {job['source_platform']}")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"ERROR: {e}")
