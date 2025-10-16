"""
Main banner detection logic with pattern recognition.
"""

import re
from typing import List, Optional, Dict, Tuple
from bs4 import BeautifulSoup, Tag

from ..models import PageData, BannerInfo, BannerType, ButtonType
from ..extractors import BannerExtractor, ButtonExtractor, SelectorExtractor


class BannerDetector:
    """Main detector for consent banners using pattern recognition."""
    
    def __init__(self):
        """Initialize the banner detector."""
        self.banner_extractor = BannerExtractor()
        self.button_extractor = ButtonExtractor()
        self.selector_extractor = SelectorExtractor()
        
        # Detection patterns and weights
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, Dict]:
        """Initialize detection patterns with weights."""
        return {
            'text_patterns': {
                'weight': 0.3,
                'patterns': [
                    r'\bcookie\b', r'\bconsent\b', r'\bgdpr\b', r'\bprivacy\b',
                    r'\btracking\b', r'\banalytics\b', r'\badvertising\b',
                    r'\bpersonalization\b', r'\bpreferences\b', r'\bsettings\b'
                ]
            },
            'button_patterns': {
                'weight': 0.4,
                'patterns': [
                    r'\baccept\b', r'\bagree\b', r'\bdecline\b', r'\breject\b',
                    r'\bmanage\b', r'\bpreferences\b', r'\bsettings\b', r'\bok\b',
                    r'\bcontinue\b', r'\bproceed\b', r'\bgot it\b'
                ]
            },
            'structural_patterns': {
                'weight': 0.2,
                'patterns': [
                    'modal', 'popup', 'overlay', 'banner', 'notice', 'dialog',
                    'fixed', 'absolute', 'z-index', 'position'
                ]
            },
            'attribute_patterns': {
                'weight': 0.1,
                'patterns': [
                    'data-consent', 'data-cookie', 'data-gdpr', 'data-privacy',
                    'aria-label', 'role', 'data-testid', 'data-cy'
                ]
            }
        }
    
    def detect_banner(self, page_data: PageData) -> Optional[BannerInfo]:
        """
        Detect consent banner in page data.
        
        Args:
            page_data: PageData object containing HTML and metadata
            
        Returns:
            BannerInfo object if banner detected, None otherwise
        """
        try:
            # Extract banner information
            banner_info = self.banner_extractor.extract_banner_info(
                page_data.html_content, 
                page_data.url
            )
            
            if not banner_info:
                return None
            
            # Enhance detection with additional analysis
            enhanced_info = self._enhance_detection(banner_info, page_data)
            
            # Calculate final confidence score
            final_confidence = self._calculate_final_confidence(enhanced_info, page_data)
            enhanced_info.detection_confidence = final_confidence
            
            # Only return if confidence is above threshold
            if final_confidence >= 0.6:
                return enhanced_info
            
            return None
            
        except Exception as e:
            print(f"Error detecting banner: {e}")
            return None
    
    def _enhance_detection(self, banner_info: BannerInfo, page_data: PageData) -> BannerInfo:
        """Enhance banner detection with additional analysis."""
        try:
            soup = BeautifulSoup(page_data.html_content, 'html.parser')
            
            # Find banner container
            banner_container = soup.select_one(banner_info.container_selector)
            if not banner_container:
                return banner_info
            
            # Analyze JavaScript for consent-related functionality
            js_analysis = self._analyze_javascript(page_data.javascript_content)
            
            # Analyze CSS for styling patterns
            css_analysis = self._analyze_css(page_data.css_content)
            
            # Update additional selectors based on analysis
            additional_selectors = banner_info.additional_selectors.copy()
            additional_selectors.update(js_analysis.get('selectors', {}))
            additional_selectors.update(css_analysis.get('selectors', {}))
            
            banner_info.additional_selectors = additional_selectors
            
            return banner_info
            
        except Exception as e:
            print(f"Error enhancing detection: {e}")
            return banner_info
    
    def _analyze_javascript(self, js_content: List[str]) -> Dict:
        """Analyze JavaScript content for consent-related patterns."""
        analysis = {'selectors': {}, 'confidence': 0.0}
        
        # Common consent-related JavaScript patterns
        consent_patterns = [
            r'cookie.*consent', r'consent.*cookie', r'gdpr.*consent',
            r'privacy.*notice', r'tracking.*consent', r'analytics.*consent'
        ]
        
        pattern_matches = 0
        total_patterns = len(consent_patterns)
        
        for js in js_content:
            js_lower = js.lower()
            
            for pattern in consent_patterns:
                if re.search(pattern, js_lower):
                    pattern_matches += 1
            
            # Look for specific consent library patterns
            if any(lib in js_lower for lib in ['cookiebot', 'onetrust', 'trustarc', 'quantcast']):
                analysis['confidence'] += 0.3
        
        analysis['confidence'] += (pattern_matches / total_patterns) * 0.7
        
        return analysis
    
    def _analyze_css(self, css_content: List[str]) -> Dict:
        """Analyze CSS content for consent-related styling patterns."""
        analysis = {'selectors': {}, 'confidence': 0.0}
        
        # Common consent-related CSS patterns
        consent_patterns = [
            r'cookie.*banner', r'consent.*banner', r'gdpr.*banner',
            r'privacy.*notice', r'cc-banner', r'cookie-notice'
        ]
        
        pattern_matches = 0
        total_patterns = len(consent_patterns)
        
        for css in css_content:
            css_lower = css.lower()
            
            for pattern in consent_patterns:
                if re.search(pattern, css_lower):
                    pattern_matches += 1
        
        analysis['confidence'] = (pattern_matches / total_patterns) * 0.5
        
        return analysis
    
    def _calculate_final_confidence(self, banner_info: BannerInfo, page_data: PageData) -> float:
        """Calculate final confidence score for banner detection."""
        confidence = banner_info.detection_confidence
        
        # Boost confidence based on banner type
        if banner_info.banner_type in [BannerType.MODAL, BannerType.BOTTOM_BAR]:
            confidence += 0.1
        
        # Boost confidence based on button variety
        button_types = {button.button_type for button in banner_info.buttons}
        if len(button_types) >= 3:
            confidence += 0.1
        
        # Boost confidence for accept/reject pair
        if ButtonType.ACCEPT in button_types and ButtonType.REJECT in button_types:
            confidence += 0.15
        
        # Boost confidence based on overlay detection
        if banner_info.overlay_selectors:
            confidence += 0.05
        
        # Boost confidence for stable selectors
        if self._has_stable_selectors(banner_info):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _has_stable_selectors(self, banner_info: BannerInfo) -> bool:
        """Check if banner has stable, reliable selectors."""
        # Check banner selector
        banner_selector = banner_info.container_selector
        if not banner_selector:
            return False
        
        # Stable selector indicators
        stable_indicators = [
            'id=', 'data-consent', 'data-cookie', 'data-gdpr',
            'aria-label', 'role=', 'data-testid'
        ]
        
        return any(indicator in banner_selector for indicator in stable_indicators)
    
    def detect_multiple_banners(self, page_data: PageData) -> List[BannerInfo]:
        """Detect multiple potential consent banners on a page."""
        banners = []
        
        try:
            soup = BeautifulSoup(page_data.html_content, 'html.parser')
            
            # Find all potential banner containers
            potential_banners = self._find_all_banner_containers(soup)
            
            for container in potential_banners:
                try:
                    # Extract banner info for this container
                    container_html = str(container)
                    banner_info = self.banner_extractor.extract_banner_info(
                        container_html, 
                        page_data.url
                    )
                    
                    if banner_info and banner_info.detection_confidence >= 0.5:
                        banners.append(banner_info)
                        
                except Exception as e:
                    print(f"Error processing banner container: {e}")
                    continue
            
            # Sort by confidence score
            banners.sort(key=lambda x: x.detection_confidence, reverse=True)
            
        except Exception as e:
            print(f"Error detecting multiple banners: {e}")
        
        return banners
    
    def _find_all_banner_containers(self, soup: BeautifulSoup) -> List[Tag]:
        """Find all potential banner containers on the page."""
        containers = []
        
        # Extended list of banner selectors
        selectors = [
            "[id*='cookie']", "[class*='cookie']", "[id*='consent']", "[class*='consent']",
            "[id*='gdpr']", "[class*='gdpr']", "[id*='privacy']", "[class*='privacy']",
            ".cc-banner", ".cookie-banner", ".consent-banner", ".gdpr-banner",
            ".privacy-notice", "#cookie-notice", "#consent-notice", "#gdpr-notice",
            "[data-testid*='cookie']", "[data-testid*='consent']",
            "[aria-label*='cookie']", "[aria-label*='consent']",
            "[role='dialog']", "[role='banner']", "[role='alertdialog']"
        ]
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    if self._is_likely_banner(element) and element not in containers:
                        containers.append(element)
            except Exception:
                continue
        
        return containers
    
    def _is_likely_banner(self, element: Tag) -> bool:
        """Check if an element is likely a consent banner."""
        text = element.get_text().lower()
        
        # Must contain consent-related keywords
        consent_keywords = ['cookie', 'consent', 'gdpr', 'privacy', 'tracking']
        keyword_count = sum(1 for keyword in consent_keywords if keyword in text)
        
        if keyword_count < 1:
            return False
        
        # Check for button-like elements
        buttons = element.find_all(['button', 'a', 'input'])
        if not buttons:
            return False
        
        # Check for common banner attributes
        attrs = str(element.attrs).lower()
        if any(keyword in attrs for keyword in consent_keywords):
            return True
        
        return True
    
    def get_detection_summary(self, page_data: PageData) -> Dict:
        """Get a summary of detection results for a page."""
        summary = {
            'url': page_data.url,
            'banner_detected': False,
            'banner_count': 0,
            'confidence_scores': [],
            'banner_types': [],
            'button_counts': {},
            'detection_methods': []
        }
        
        try:
            banners = self.detect_multiple_banners(page_data)
            
            if banners:
                summary['banner_detected'] = True
                summary['banner_count'] = len(banners)
                summary['confidence_scores'] = [b.detection_confidence for b in banners]
                summary['banner_types'] = [b.banner_type.value for b in banners]
                
                # Count button types across all banners
                for banner in banners:
                    for button in banner.buttons:
                        button_type = button.button_type.value
                        summary['button_counts'][button_type] = summary['button_counts'].get(button_type, 0) + 1
                
                # Detection methods used
                summary['detection_methods'] = ['pattern_matching', 'structural_analysis', 'text_analysis']
            
        except Exception as e:
            print(f"Error generating detection summary: {e}")
        
        return summary
