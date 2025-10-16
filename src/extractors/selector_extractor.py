"""
CSS selector extraction utilities for consent banners.
"""

import re
from typing import List, Dict, Optional, Set
from bs4 import BeautifulSoup, Tag

from ..models import BannerInfo


class SelectorExtractor:
    """Extracts and generates CSS selectors for consent banner elements."""
    
    def __init__(self):
        """Initialize the selector extractor."""
        self.common_attributes = {
            'data-testid', 'data-cy', 'data-qa', 'data-automation', 'data-consent',
            'data-cookie', 'data-gdpr', 'data-privacy', 'aria-label', 'aria-labelledby'
        }
    
    def extract_selectors(self, banner_info: BannerInfo) -> Dict[str, str]:
        """
        Extract CSS selectors for all banner elements.
        
        Args:
            banner_info: BannerInfo object containing banner data
            
        Returns:
            Dictionary of selector types and their CSS selectors
        """
        selectors = {}
        
        # Banner container selector
        selectors['banner'] = banner_info.container_selector
        
        # Button selectors
        for button in banner_info.buttons:
            button_type = button.button_type.value
            if button_type not in selectors:
                selectors[button_type] = []
            
            if isinstance(selectors[button_type], list):
                selectors[button_type] = []
            
            selectors[button_type].append(button.selector)
        
        # Overlay selectors
        if banner_info.overlay_selectors:
            selectors['overlay'] = banner_info.overlay_selectors
        
        # Additional selectors
        selectors.update(banner_info.additional_selectors)
        
        return selectors
    
    def generate_robust_selectors(self, html_content: str, banner_info: BannerInfo) -> Dict[str, str]:
        """
        Generate more robust selectors by analyzing the HTML structure.
        
        Args:
            html_content: Full HTML content
            banner_info: BannerInfo object
            
        Returns:
            Dictionary of improved selectors
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find banner container
            banner_container = self._find_element_by_selector(soup, banner_info.container_selector)
            if not banner_container:
                return self.extract_selectors(banner_info)
            
            improved_selectors = {}
            
            # Generate improved banner selector
            improved_selectors['banner'] = self._generate_robust_selector(banner_container)
            
            # Generate improved button selectors
            for button in banner_info.buttons:
                button_element = self._find_element_by_selector(banner_container, button.selector)
                if button_element:
                    button_type = button.button_type.value
                    if button_type not in improved_selectors:
                        improved_selectors[button_type] = []
                    
                    if isinstance(improved_selectors[button_type], list):
                        improved_selectors[button_type] = []
                    
                    improved_selectors[button_type].append(
                        self._generate_robust_selector(button_element)
                    )
            
            # Generate overlay selectors
            improved_selectors['overlay'] = self._generate_overlay_selectors(soup, banner_container)
            
            return improved_selectors
            
        except Exception as e:
            print(f"Error generating robust selectors: {e}")
            return self.extract_selectors(banner_info)
    
    def _find_element_by_selector(self, soup: BeautifulSoup, selector: str) -> Optional[Tag]:
        """Find an element using a CSS selector."""
        try:
            elements = soup.select(selector)
            return elements[0] if elements else None
        except Exception:
            return None
    
    def _generate_robust_selector(self, element: Tag) -> str:
        """Generate a robust CSS selector for an element."""
        selectors = []
        
        # Try ID first (most reliable)
        if element.get('id'):
            selectors.append(f"#{element['id']}")
        
        # Try data attributes (often more stable than classes)
        for attr, value in element.attrs.items():
            if attr in self.common_attributes:
                selectors.append(f"[{attr}='{value}']")
        
        # Try classes (be selective about which ones to use)
        if element.get('class'):
            classes = element['class']
            # Filter out dynamic classes (containing numbers, timestamps, etc.)
            stable_classes = [cls for cls in classes if self._is_stable_class(cls)]
            if stable_classes:
                class_selector = '.' + '.'.join(stable_classes)
                selectors.append(class_selector)
        
        # Try aria attributes
        if element.get('aria-label'):
            selectors.append(f"[aria-label='{element['aria-label']}']")
        
        # Try role attribute
        if element.get('role'):
            selectors.append(f"[role='{element['role']}']")
        
        # Fallback to tag with parent context
        if not selectors:
            selectors.append(self._generate_contextual_selector(element))
        
        return ', '.join(selectors)
    
    def _is_stable_class(self, class_name: str) -> bool:
        """Check if a CSS class name is likely to be stable."""
        # Avoid classes that look dynamic
        dynamic_patterns = [
            r'\d+',  # Contains numbers
            r'timestamp', r'time', r'date',
            r'random', r'uuid', r'hash',
            r'generated', r'auto'
        ]
        
        for pattern in dynamic_patterns:
            if re.search(pattern, class_name, re.IGNORECASE):
                return False
        
        return True
    
    def _generate_contextual_selector(self, element: Tag) -> str:
        """Generate a selector using element context."""
        # Try to find a unique parent-child relationship
        parent = element.parent
        if parent:
            # Use parent tag and element tag
            parent_tag = parent.name
            element_tag = element.name
            
            # Add parent class if available
            parent_classes = parent.get('class', [])
            if parent_classes:
                parent_class = '.' + '.'.join(parent_classes[:2])  # Limit to first 2 classes
                return f"{parent_tag}{parent_class} > {element_tag}"
            else:
                return f"{parent_tag} > {element_tag}"
        
        return element.name
    
    def _generate_overlay_selectors(self, soup: BeautifulSoup, banner_container: Tag) -> List[str]:
        """Generate selectors for overlay elements."""
        overlay_selectors = []
        
        # Common overlay patterns
        overlay_patterns = [
            '.overlay',
            '.backdrop',
            '.modal-backdrop',
            '.cookie-overlay',
            '.consent-overlay',
            '.gdpr-overlay',
            '.privacy-overlay',
            '[class*="overlay"]',
            '[class*="backdrop"]',
            '[class*="modal"]'
        ]
        
        for pattern in overlay_patterns:
            try:
                elements = soup.select(pattern)
                for element in elements:
                    if element != banner_container:
                        selector = self._generate_robust_selector(element)
                        if selector not in overlay_selectors:
                            overlay_selectors.append(selector)
            except Exception:
                continue
        
        return overlay_selectors
    
    def validate_selectors(self, selectors: Dict[str, str], html_content: str) -> Dict[str, bool]:
        """
        Validate that selectors work with the HTML content.
        
        Args:
            selectors: Dictionary of selectors to validate
            html_content: HTML content to test against
            
        Returns:
            Dictionary indicating which selectors are valid
        """
        validation_results = {}
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for selector_type, selector_value in selectors.items():
                if isinstance(selector_value, list):
                    # Handle list of selectors
                    valid_count = 0
                    for selector in selector_value:
                        try:
                            elements = soup.select(selector)
                            if elements:
                                valid_count += 1
                        except Exception:
                            continue
                    validation_results[selector_type] = valid_count > 0
                else:
                    # Handle single selector
                    try:
                        elements = soup.select(selector_value)
                        validation_results[selector_type] = len(elements) > 0
                    except Exception:
                        validation_results[selector_type] = False
            
        except Exception as e:
            print(f"Error validating selectors: {e}")
            return {selector_type: False for selector_type in selectors.keys()}
        
        return validation_results
    
    def generate_fallback_selectors(self, banner_info: BannerInfo) -> Dict[str, List[str]]:
        """
        Generate fallback selectors for common banner patterns.
        
        Args:
            banner_info: BannerInfo object
            
        Returns:
            Dictionary of fallback selectors
        """
        fallbacks = {}
        
        # Banner fallbacks
        banner_fallbacks = [
            "[id*='cookie']",
            "[class*='cookie']",
            "[id*='consent']",
            "[class*='consent']",
            "[id*='gdpr']",
            "[class*='gdpr']",
            ".cc-banner",
            ".cookie-banner",
            ".consent-banner"
        ]
        fallbacks['banner'] = banner_fallbacks
        
        # Accept button fallbacks
        accept_fallbacks = [
            "button:contains('Accept')",
            "button:contains('Agree')",
            "button:contains('OK')",
            "button:contains('Yes')",
            "[data-action='accept']",
            "[data-consent='accept']",
            ".accept-btn",
            ".agree-btn"
        ]
        fallbacks['accept'] = accept_fallbacks
        
        # Reject button fallbacks
        reject_fallbacks = [
            "button:contains('Reject')",
            "button:contains('Decline')",
            "button:contains('No')",
            "[data-action='reject']",
            "[data-consent='reject']",
            ".reject-btn",
            ".decline-btn"
        ]
        fallbacks['reject'] = reject_fallbacks
        
        # Manage button fallbacks
        manage_fallbacks = [
            "button:contains('Manage')",
            "button:contains('Settings')",
            "button:contains('Preferences')",
            "[data-action='manage']",
            "[data-consent='manage']",
            ".manage-btn",
            ".settings-btn"
        ]
        fallbacks['manage'] = manage_fallbacks
        
        return fallbacks
    
    def optimize_selectors(self, selectors: Dict[str, str], html_content: str) -> Dict[str, str]:
        """
        Optimize selectors for better performance and reliability.
        
        Args:
            selectors: Dictionary of selectors to optimize
            html_content: HTML content for testing
            
        Returns:
            Dictionary of optimized selectors
        """
        optimized = {}
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for selector_type, selector_value in selectors.items():
                if isinstance(selector_value, list):
                    # Optimize list of selectors
                    optimized_list = []
                    for selector in selector_value:
                        optimized_selector = self._optimize_single_selector(selector, soup)
                        if optimized_selector:
                            optimized_list.append(optimized_selector)
                    optimized[selector_type] = optimized_list
                else:
                    # Optimize single selector
                    optimized_selector = self._optimize_single_selector(selector_value, soup)
                    if optimized_selector:
                        optimized[selector_type] = optimized_selector
            
        except Exception as e:
            print(f"Error optimizing selectors: {e}")
            return selectors
        
        return optimized
    
    def _optimize_single_selector(self, selector: str, soup: BeautifulSoup) -> Optional[str]:
        """Optimize a single CSS selector."""
        try:
            # Test if selector works
            elements = soup.select(selector)
            if not elements:
                return None
            
            # If selector works and is specific enough, return as-is
            if len(elements) == 1:
                return selector
            
            # Try to make selector more specific
            if len(elements) > 1:
                # Add parent context to make it more specific
                element = elements[0]
                parent = element.parent
                if parent and parent.name != 'body':
                    parent_selector = self._generate_robust_selector(parent)
                    return f"{parent_selector} > {selector}"
            
            return selector
            
        except Exception:
            return None
