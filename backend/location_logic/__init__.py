"""
Location Logic Module
Handles location normalization and scoring
"""

from .normalizer import normalize_location, score_location_match

__all__ = ["normalize_location", "score_location_match"]
