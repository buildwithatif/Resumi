from backend.unified_discovery.working_scrapers import (
    RemoteOKScraper,
    TheMuseScraper,
    ArbeitnowScraper,
    RemotiveScraper,
    GreenhouseScraper
)

print("Testing individual scrapers...")
print("=" * 50)

# Test RemoteOK
print("\n1. RemoteOK:")
try:
    scraper = RemoteOKScraper()
    jobs = scraper.scrape_jobs(keywords="", max_results=20)  # No keyword filter
    print(f"   Result: {len(jobs)} jobs")
    if jobs:
        print(f"   Sample: {jobs[0].title}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test The Muse
print("\n2. The Muse:")
try:
    scraper = TheMuseScraper()
    jobs = scraper.scrape_jobs(keywords="", location="", max_results=20)
    print(f"   Result: {len(jobs)} jobs")
    if jobs:
        print(f"   Sample: {jobs[0].title}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test Arbeitnow
print("\n3. Arbeitnow:")
try:
    scraper = ArbeitnowScraper()
    jobs = scraper.scrape_jobs(keywords="", max_results=20)
    print(f"   Result: {len(jobs)} jobs")
    if jobs:
        print(f"   Sample: {jobs[0].title}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test Remotive
print("\n4. Remotive:")
try:
    scraper = RemotiveScraper()
    jobs = scraper.scrape_jobs(keywords="", max_results=20)
    print(f"   Result: {len(jobs)} jobs")
    if jobs:
        print(f"   Sample: {jobs[0].title}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test Greenhouse
print("\n5. Greenhouse:")
try:
    scraper = GreenhouseScraper()
    jobs = scraper.scrape_jobs(keywords="", max_results=15)
    print(f"   Result: {len(jobs)} jobs")
    if jobs:
        print(f"   Sample: {jobs[0].title}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 50)
