"""Feature extraction logic for consent banners."""

from .banner_extractor import BannerExtractor
from .button_extractor import ButtonExtractor
from .selector_extractor import SelectorExtractor

__all__ = ["BannerExtractor", "ButtonExtractor", "SelectorExtractor"]
