"""
Test script for MBA data integration
Demonstrates how to import campus data and analyze patterns
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.mba_data.importer import CampusDataImporter
from backend.mba_data.pattern_analyzer import PatternAnalyzer


def test_import_and_analyze(json_file_path: str):
    """
    Test import and pattern analysis
    
    Args:
        json_file_path: Path to campus JSON file
    """
    print("=" * 60)
    print("MBA CAMPUS DATA INTEGRATION TEST")
    print("=" * 60)
    
    # Initialize importer
    importer = CampusDataImporter()
    
    # Import data
    print(f"\n1. Importing data from: {json_file_path}")
    stats = importer.import_campus_json(json_file_path)
    
    print(f"\n   Import Statistics:")
    print(f"   - Total jobs: {stats['total_jobs']}")
    print(f"   - Mapped successfully: {stats['mapped_successfully']}")
    print(f"   - Mapping failed: {stats['mapping_failed']}")
    print(f"   - Raw file: {stats['raw_file']}")
    print(f"   - Mapped file: {stats['mapped_file']}")
    
    # Load mapped jobs
    print(f"\n2. Loading all mapped jobs...")
    jobs = importer.load_all_mapped_jobs()
    print(f"   Loaded {len(jobs)} jobs")
    
    # Analyze patterns
    print(f"\n3. Analyzing patterns...")
    analyzer = PatternAnalyzer()
    summary = analyzer.analyze_all_patterns(jobs)
    
    print(f"\n   Pattern Analysis Summary:")
    print(f"   - Total jobs analyzed: {summary['total_jobs_analyzed']}")
    print(f"   - Role families found: {summary['role_families_found']}")
    print(f"   - Patterns generated: {', '.join(summary['patterns_generated'])}")
    print(f"   - Output directory: {summary['output_directory']}")
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETE")
    print("=" * 60)
    
    return stats, summary


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_mba_integration.py <path_to_campus_json>")
        print("\nExample:")
        print("  python test_mba_integration.py data/campus_sample.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    test_import_and_analyze(json_file)
