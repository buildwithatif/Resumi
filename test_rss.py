import httpx
import xml.etree.ElementTree as ET

feeds = [
    "https://remoteok.com/rss",
    "https://weworkremotely.com/categories/remote-programming-jobs.rss",
    "https://weworkremotely.com/categories/remote-design-jobs.rss",
    "https://remotive.com/remote-jobs/feed"
]

print("Testing RSS Feeds...")
print("=" * 50)

for url in feeds:
    try:
        print(f"\nChecking {url}...")
        response = httpx.get(url, timeout=15.0)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # Parse XML to see if we get items
            root = ET.fromstring(response.content)
            # RSS 2.0 uses 'channel/item'
            items = root.findall(".//item")
            print(f"Found {len(items)} items")
            if items:
                print(f"Sample: {items[0].find('title').text}")
        else:
            print("Failed")
            
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 50)
