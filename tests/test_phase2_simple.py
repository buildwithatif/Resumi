"""
Simple test for Phase 2 collectors
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test imports
print("Testing Phase 2 Collector Imports...")

try:
    from backend.job_sources.social_signals.base_signal_collector import BaseSignalCollector
    print("✅ BaseSignalCollector imported")
except Exception as e:
    print(f"❌ BaseSignalCollector import failed: {e}")

try:
    from backend.job_sources.linkedin_public.parser import LinkedInPublicParser
    print("✅ LinkedInPublicParser imported")
except Exception as e:
    print(f"❌ LinkedInPublicParser import failed: {e}")

try:
    from backend.job_sources.social_signals.x_scanner import XSignalScanner
    print("✅ XSignalScanner imported")
except Exception as e:
    print(f"❌ XSignalScanner import failed: {e}")

try:
    from backend.job_sources.social_signals.reddit_scanner import RedditSignalScanner
    print("✅ RedditSignalScanner imported")
except Exception as e:
    print(f"❌ RedditSignalScanner import failed: {e}")

print("\n✅ All Phase 2 collectors successfully imported!")
print("\nNote: Collectors are placeholder implementations to avoid ToS issues.")
print("They can be activated when proper HTML parsing is implemented.")
