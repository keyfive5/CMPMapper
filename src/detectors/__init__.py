"""Auto-detection logic for consent banners."""

from .banner_detector import BannerDetector
from .pattern_matcher import PatternMatcher
from .confidence_calculator import ConfidenceCalculator

__all__ = ["BannerDetector", "PatternMatcher", "ConfidenceCalculator"]
