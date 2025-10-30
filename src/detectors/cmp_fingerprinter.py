"""
CMP Fingerprinter - Identifies Cookie Consent Management Platforms
by analyzing script signatures, DOM patterns, and behavioral indicators.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from bs4 import BeautifulSoup


@dataclass
class CMPSignature:
    """Represents a CMP signature with confidence score."""
    name: str
    confidence: float
    indicators: List[str]
    script_patterns: List[str]
    dom_patterns: List[str]


class CMPFingerprinter:
    """Identifies CMP types by analyzing page content and scripts."""
    
    def __init__(self):
        self.cmp_signatures = self._initialize_cmp_signatures()
    
    def _initialize_cmp_signatures(self) -> Dict[str, CMPSignature]:
        """Initialize known CMP signatures and patterns."""
        return {
            'cookieyes': CMPSignature(
                name='CookieYes',
                confidence=0.0,
                indicators=['cky-consent-container', 'cky-modal', 'cky-notice'],
                script_patterns=['cookieyes', 'cky-', 'cookieyes.com'],
                dom_patterns=['[class*="cky-"]', '[id*="cky-"]', '.cky-btn']
            ),
            'onetrust': CMPSignature(
                name='OneTrust',
                confidence=0.0,
                indicators=['ot-sdk-container', 'onetrust', 'optanon'],
                script_patterns=['onetrust', 'optanon', 'cookiepro'],
                dom_patterns=['[class*="ot-"]', '[id*="onetrust"]', '.optanon']
            ),
            'cookiebot': CMPSignature(
                name='Cookiebot',
                confidence=0.0,
                indicators=['CybotCookiebotDialog', 'Cookiebot'],
                script_patterns=['cookiebot', 'cybot'],
                dom_patterns=['[class*="CybotCookiebotDialog"]', '[id*="Cookiebot"]']
            ),
            'consentmanager': CMPSignature(
                name='ConsentManager',
                confidence=0.0,
                indicators=['consentmanager', 'cm-consent'],
                script_patterns=['consentmanager', 'cm-consent'],
                dom_patterns=['[class*="cm-"]', '[id*="consentmanager"]']
            ),
            'tarteaucitron': CMPSignature(
                name='TarteAuCitron',
                confidence=0.0,
                indicators=['tarteaucitron', 'tac'],
                script_patterns=['tarteaucitron', 'tac.js'],
                dom_patterns=['[class*="tarteaucitron"]', '[id*="tarteaucitron"]']
            ),
            'cookieinformation': CMPSignature(
                name='Cookie Information',
                confidence=0.0,
                indicators=['cookieinformation', 'ci-consent'],
                script_patterns=['cookieinformation', 'ci-consent'],
                dom_patterns=['[class*="ci-"]', '[id*="cookieinformation"]']
            ),
            'custom_wordpress': CMPSignature(
                name='Custom WordPress',
                confidence=0.0,
                indicators=['gdpr-cookie-consent', 'cookie-notice', 'wp-gdpr'],
                script_patterns=['wp-content/plugins', 'gdpr-cookie'],
                dom_patterns=['[class*="gdpr-"]', '[class*="cookie-notice"]']
            ),
            'shopify': CMPSignature(
                name='Shopify Cookie Banner',
                confidence=0.0,
                indicators=['shopify-cookie-banner', 'shopify-privacy'],
                script_patterns=['shopify', 'cdn.shopify.com'],
                dom_patterns=['[class*="shopify-"]', '[data-shopify]']
            ),
            'custom_generic': CMPSignature(
                name='Custom Generic',
                confidence=0.0,
                indicators=['cookie-banner', 'consent-banner', 'privacy-banner'],
                script_patterns=[],
                dom_patterns=['[class*="cookie"]', '[class*="consent"]', '[class*="privacy"]']
            )
        }
    
    def identify_cmp_type(self, page_data) -> Tuple[str, float, List[str]]:
        """
        Identify CMP type from page data.
        
        Args:
            page_data: PageData object containing HTML content and metadata
            
        Returns:
            Tuple of (CMP name, confidence score, detected indicators)
        """
        if not page_data or not page_data.html_content:
            return "Unknown", 0.0, []
        
        soup = BeautifulSoup(page_data.html_content, 'html.parser')
        script_content = self._extract_script_content(soup)
        dom_elements = self._extract_dom_elements(soup)
        
        best_match = None
        best_confidence = 0.0
        detected_indicators = []
        
        for cmp_name, signature in self.cmp_signatures.items():
            confidence, indicators = self._calculate_confidence(
                signature, script_content, dom_elements, soup
            )
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = cmp_name
                detected_indicators = indicators
        
        # If no specific CMP detected, check for generic patterns
        if best_confidence < 0.3:
            generic_confidence, generic_indicators = self._detect_generic_patterns(soup)
            if generic_confidence > best_confidence:
                return "Custom Generic", generic_confidence, generic_indicators
        
        return best_match or "Unknown", best_confidence, detected_indicators
    
    def _extract_script_content(self, soup: BeautifulSoup) -> str:
        """Extract all script content from the page."""
        scripts = soup.find_all('script')
        content = []
        
        for script in scripts:
            if script.string:
                content.append(script.string)
            if script.get('src'):
                content.append(script.get('src', ''))
        
        return ' '.join(content).lower()
    
    def _extract_dom_elements(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract relevant DOM elements and their attributes."""
        elements = {
            'classes': [],
            'ids': [],
            'data_attrs': [],
            'text_content': []
        }
        
        # Find all elements with consent-related classes/IDs
        for element in soup.find_all():
            # Classes
            if element.get('class'):
                elements['classes'].extend(element.get('class'))
            
            # IDs
            if element.get('id'):
                elements['ids'].append(element.get('id'))
            
            # Data attributes
            for attr, value in element.attrs.items():
                if attr.startswith('data-'):
                    elements['data_attrs'].append(f"{attr}={value}")
            
            # Text content (for buttons and links)
            if element.name in ['button', 'a', 'span', 'div']:
                text = element.get_text(strip=True).lower()
                if any(keyword in text for keyword in ['accept', 'decline', 'cookie', 'consent', 'privacy']):
                    elements['text_content'].append(text)
        
        return elements
    
    def _calculate_confidence(self, signature: CMPSignature, script_content: str, 
                           dom_elements: Dict, soup: BeautifulSoup) -> Tuple[float, List[str]]:
        """Calculate confidence score for a CMP signature."""
        confidence = 0.0
        detected_indicators = []
        
        # Check script patterns
        for pattern in signature.script_patterns:
            if pattern.lower() in script_content:
                confidence += 0.3
                detected_indicators.append(f"Script: {pattern}")
        
        # Check DOM patterns
        for pattern in signature.dom_patterns:
            try:
                elements = soup.select(pattern)
                if elements:
                    confidence += 0.2
                    detected_indicators.append(f"DOM: {pattern}")
            except:
                pass
        
        # Check specific indicators
        for indicator in signature.indicators:
            if indicator.lower() in str(dom_elements).lower():
                confidence += 0.4
                detected_indicators.append(f"Indicator: {indicator}")
        
        # Check for CMP-specific button patterns
        button_patterns = self._get_cmp_button_patterns(signature.name)
        for pattern in button_patterns:
            if soup.select(pattern):
                confidence += 0.1
                detected_indicators.append(f"Button: {pattern}")
        
        return min(confidence, 1.0), detected_indicators
    
    def _get_cmp_button_patterns(self, cmp_name: str) -> List[str]:
        """Get CMP-specific button patterns."""
        button_patterns = {
            'cookieyes': ['.cky-btn', '.cky-btn-accept', '.cky-btn-decline'],
            'onetrust': ['.ot-pc-refuse-all-handler', '.ot-pc-accept-all-handler'],
            'cookiebot': ['.CybotCookiebotDialogBodyButton', '.CybotCookiebotDialogBodyLevelButtonLevel3'],
            'consentmanager': ['.cm-btn', '.cm-accept-all', '.cm-decline-all'],
            'tarteaucitron': ['.tarteaucitronAllow', '.tarteaucitronDeny'],
            'custom_generic': ['button[class*="accept"]', 'button[class*="decline"]', 'a[class*="cookie"]']
        }
        return button_patterns.get(cmp_name, [])
    
    def _detect_generic_patterns(self, soup: BeautifulSoup) -> Tuple[float, List[str]]:
        """Detect generic consent banner patterns."""
        confidence = 0.0
        indicators = []
        
        # Look for common consent-related text
        consent_texts = [
            'cookie policy', 'privacy policy', 'accept cookies', 'decline cookies',
            'manage cookies', 'cookie preferences', 'gdpr', 'consent'
        ]
        
        page_text = soup.get_text().lower()
        for text in consent_texts:
            if text in page_text:
                confidence += 0.1
                indicators.append(f"Text: {text}")
        
        # Look for common banner structures
        banner_selectors = [
            '[class*="cookie"]', '[class*="consent"]', '[class*="privacy"]',
            '[id*="cookie"]', '[id*="consent"]', '[id*="privacy"]'
        ]
        
        for selector in banner_selectors:
            if soup.select(selector):
                confidence += 0.05
                indicators.append(f"Structure: {selector}")
        
        # Look for overlay/modal patterns
        overlay_selectors = [
            '[style*="z-index"]', '[style*="position: fixed"]', '[style*="position: absolute"]'
        ]
        
        for selector in overlay_selectors:
            elements = soup.select(selector)
            for element in elements:
                if any(keyword in element.get_text().lower() for keyword in ['cookie', 'consent', 'privacy']):
                    confidence += 0.1
                    indicators.append(f"Overlay: {selector}")
                    break
        
        return min(confidence, 1.0), indicators
    
    def get_cmp_characteristics(self, cmp_name: str) -> Dict:
        """Get characteristics of a specific CMP."""
        characteristics = {
            'cookieyes': {
                'common_selectors': ['.cky-consent-container', '.cky-modal', '.cky-btn'],
                'button_patterns': ['.cky-btn-accept', '.cky-btn-decline'],
                'typical_behavior': 'Modal overlay with accept/decline buttons',
                'detection_tips': 'Look for cky- prefixed classes and CookieYes script'
            },
            'onetrust': {
                'common_selectors': ['.ot-sdk-container', '#onetrust-consent-sdk'],
                'button_patterns': ['.ot-pc-accept-all-handler', '.ot-pc-refuse-all-handler'],
                'typical_behavior': 'Comprehensive consent management with categories',
                'detection_tips': 'Look for ot- prefixed classes and OneTrust script'
            },
            'cookiebot': {
                'common_selectors': ['.CybotCookiebotDialog', '#CybotCookiebotDialogBody'],
                'button_patterns': ['.CybotCookiebotDialogBodyButton'],
                'typical_behavior': 'Simple accept/decline dialog',
                'detection_tips': 'Look for CybotCookiebotDialog classes'
            },
            'custom_generic': {
                'common_selectors': ['[class*="cookie"]', '[class*="consent"]'],
                'button_patterns': ['button[class*="accept"]', 'button[class*="decline"]'],
                'typical_behavior': 'Varies widely, often simple banner',
                'detection_tips': 'Look for generic cookie/consent related classes and text'
            }
        }
        return characteristics.get(cmp_name, {})
