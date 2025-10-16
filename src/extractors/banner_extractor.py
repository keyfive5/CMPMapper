"""
Banner feature extraction logic for analyzing consent banners.
"""

import re
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup, Tag

from ..models import BannerInfo, BannerType, ConsentButton, ButtonType


class BannerExtractor:
    """Extracts features from consent banners."""
    
    # Common consent-related keywords
    CONSENT_KEYWORDS = [
        'cookie', 'consent', 'gdpr', 'privacy', 'accept', 'agree', 'decline', 'reject',
        'preferences', 'settings', 'manage', 'opt-in', 'opt-out', 'tracking', 'analytics',
        'advertising', 'marketing', 'necessary', 'functional', 'performance', 'personalization'
    ]
    
    # Common button text patterns
    ACCEPT_PATTERNS = [
        r'\baccept\b', r'\bagree\b', r'\bok\b', r'\byes\b', r'\ballow\b', r'\bconsent\b',
        r'\bcontinue\b', r'\bproceed\b', r'\bi accept\b', r'\bi agree\b', r'\bgot it\b',
        r'\baccept all\b', r'\bagree all\b', r'\ballow all\b', r'\baccept cookies\b',
        r'\bagree to cookies\b', r'\benable\b', r'\bturn on\b', r'\bactivate\b',
        r'\baccept all cookies\b', r'\ballow all cookies\b', r'\bi consent\b'
    ]
    
    REJECT_PATTERNS = [
        r'\bdecline\b', r'\breject\b', r'\bdeny\b', r'\bno\b', r'\brefuse\b', r'\bdisagree\b',
        r'\bopt.?out\b', r'\bnecessary only\b', r'\brequired only\b', r'\bessential only\b'
    ]
    
    MANAGE_PATTERNS = [
        r'\bmanage\b', r'\bpreferences\b', r'\bsettings\b', r'\boptions\b', r'\bcustomize\b',
        r'\bchoose\b', r'\bselect\b', r'\bconfigure\b', r'\bcontrol\b'
    ]
    
    CLOSE_PATTERNS = [
        r'\bclose\b', r'\bdismiss\b', r'\b×\b', r'\b✕\b', r'\b×\b'
    ]
    
    def __init__(self):
        """Initialize the banner extractor."""
        self.accept_regex = re.compile('|'.join(self.ACCEPT_PATTERNS), re.IGNORECASE)
        self.reject_regex = re.compile('|'.join(self.REJECT_PATTERNS), re.IGNORECASE)
        self.manage_regex = re.compile('|'.join(self.MANAGE_PATTERNS), re.IGNORECASE)
        self.close_regex = re.compile('|'.join(self.CLOSE_PATTERNS), re.IGNORECASE)
    
    def extract_banner_info(self, html_content: str, site: str) -> Optional[BannerInfo]:
        """
        Extract banner information from HTML content.
        
        Args:
            html_content: HTML content to analyze
            site: Site URL or name
            
        Returns:
            BannerInfo object or None if no banner found
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find potential banner containers
            banner_containers = self._find_banner_containers(soup)
            
            if not banner_containers:
                return None
            
            # Analyze the most likely banner container
            banner_container = banner_containers[0]
            
            # Extract banner type
            banner_type = self._determine_banner_type(banner_container)
            
            # Extract buttons
            buttons = self._extract_buttons(banner_container)
            
            # Extract container selector
            container_selector = self._generate_selector(banner_container)
            
            # Extract overlay selectors
            overlay_selectors = self._find_overlay_selectors(soup, banner_container)
            
            # Calculate confidence score
            confidence = self._calculate_confidence(banner_container, buttons)
            
            return BannerInfo(
                site=site,
                banner_type=banner_type,
                container_selector=container_selector,
                buttons=buttons,
                overlay_selectors=overlay_selectors,
                html_content=str(banner_container),
                detection_confidence=confidence
            )
            
        except Exception as e:
            print(f"Error extracting banner info: {e}")
            return None
    
    def _find_banner_containers(self, soup: BeautifulSoup) -> List[Tag]:
        """Find potential banner containers in the HTML."""
        containers = []
        
        # Common banner selectors
        selectors = [
            "[id*='cookie']",
            "[class*='cookie']",
            "[id*='consent']",
            "[class*='consent']",
            "[id*='gdpr']",
            "[class*='gdpr']",
            "[id*='privacy']",
            "[class*='privacy']",
            ".cc-banner",
            ".cookie-banner",
            ".consent-banner",
            ".gdpr-banner",
            ".privacy-notice",
            "#cookie-notice",
            "#consent-notice",
            "#gdpr-notice",
            "[data-testid*='cookie']",
            "[data-testid*='consent']",
            "[aria-label*='cookie']",
            "[aria-label*='consent']",
            # Additional real-world patterns
            "[id*='ideocookie']",
            "[class*='ideocookie']",
            "[class*='widget-cookie-banner']",
            "[class*='cookie-widget']",
            "[class*='cookie-notice']",
            "[class*='consent-widget']",
            "[class*='gdpr-widget']",
            "[class*='privacy-widget']",
            "[data-widget*='cookie']",
            "[data-widget*='consent']",
            "[data-widget*='gdpr']"
        ]
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    if self._is_likely_banner(element):
                        containers.append(element)
            except Exception:
                continue
        
        # Sort by relevance score
        containers.sort(key=lambda x: self._calculate_relevance_score(x), reverse=True)
        
        return containers
    
    def _is_likely_banner(self, element: Tag) -> bool:
        """Check if an element is likely a consent banner."""
        text = element.get_text().lower()
        
        # Must contain consent-related keywords
        keyword_count = sum(1 for keyword in self.CONSENT_KEYWORDS if keyword in text)
        if keyword_count < 1:  # More lenient - only need 1 keyword
            return False
        
        # Check for button-like elements or clickable elements
        buttons = element.find_all(['button', 'a', 'input', 'div', 'span'])
        clickable_buttons = []
        
        for btn in buttons:
            # Check if element is clickable (has onclick, role=button, or is a button)
            if (btn.name in ['button', 'a', 'input'] or 
                btn.get('onclick') or 
                btn.get('role') == 'button' or
                btn.get('data-action') or
                'click' in btn.get('class', []) or
                any(keyword in btn.get_text().lower() for keyword in ['accept', 'agree', 'reject', 'decline', 'manage'])):
                clickable_buttons.append(btn)
        
        # More lenient - allow banners even without obvious buttons if they have consent keywords
        if keyword_count >= 2 and not clickable_buttons:
            return True
        
        # Check for common banner attributes
        attrs = str(element.attrs).lower()
        if any(keyword in attrs for keyword in self.CONSENT_KEYWORDS):
            return True
        
        # Check if element contains consent-related text patterns
        consent_text_patterns = [
            'cookie', 'consent', 'privacy', 'gdpr', 'accept', 'agree', 
            'decline', 'reject', 'manage', 'preferences'
        ]
        
        for pattern in consent_text_patterns:
            if pattern in text and len(text) > 20:  # Must have some substantial content
                return True
        
        return len(clickable_buttons) > 0
    
    def _calculate_relevance_score(self, element: Tag) -> float:
        """Calculate relevance score for a banner container."""
        score = 0.0
        
        # Text content analysis
        text = element.get_text().lower()
        keyword_count = sum(1 for keyword in self.CONSENT_KEYWORDS if keyword in text)
        score += keyword_count * 0.1
        
        # Button analysis
        buttons = element.find_all(['button', 'a', 'input'])
        if buttons:
            score += len(buttons) * 0.05
            
            # Check for consent-related button text
            for button in buttons:
                button_text = button.get_text().lower()
                if any(re.search(pattern, button_text) for pattern in self.ACCEPT_PATTERNS):
                    score += 0.2
                if any(re.search(pattern, button_text) for pattern in self.REJECT_PATTERNS):
                    score += 0.2
        
        # Attribute analysis
        attrs = str(element.attrs).lower()
        for keyword in self.CONSENT_KEYWORDS:
            if keyword in attrs:
                score += 0.1
        
        # Position analysis (higher score for fixed positioned elements)
        style = element.get('style', '')
        if 'fixed' in style or 'position' in style:
            score += 0.1
        
        return score
    
    def _determine_banner_type(self, container: Tag) -> BannerType:
        """Determine the type of consent banner."""
        # Check CSS classes and styles
        classes = ' '.join(container.get('class', [])).lower()
        style = container.get('style', '').lower()
        id_attr = container.get('id', '').lower()
        
        # Modal detection
        if any(word in classes + style + id_attr for word in ['modal', 'popup', 'overlay', 'dialog']):
            return BannerType.MODAL
        
        # Position-based detection
        if 'fixed' in style or 'absolute' in style:
            if 'bottom' in classes + style:
                return BannerType.BOTTOM_BAR
            elif 'top' in classes + style:
                return BannerType.TOP_BAR
        
        # Default to bottom bar for fixed elements
        if 'fixed' in style:
            return BannerType.BOTTOM_BAR
        
        return BannerType.MODAL
    
    def _extract_buttons(self, container: Tag) -> List[ConsentButton]:
        """Extract consent buttons from the banner container."""
        buttons = []
        
        # Find all button-like elements
        button_elements = container.find_all(['button', 'a', 'input'])
        
        for element in button_elements:
            button = self._analyze_button(element)
            if button:
                buttons.append(button)
        
        return buttons
    
    def _analyze_button(self, element: Tag) -> Optional[ConsentButton]:
        """Analyze a button element and determine its type."""
        text = element.get_text().strip()
        if not text:
            return None
        
        # Determine button type based on text
        button_type = self._classify_button_type(text)
        
        # Generate selector
        selector = self._generate_button_selector(element)
        
        # Get attributes
        attributes = dict(element.attrs)
        
        return ConsentButton(
            text=text,
            button_type=button_type,
            selector=selector,
            is_visible=True,
            attributes=attributes
        )
    
    def _classify_button_type(self, text: str) -> ButtonType:
        """Classify button type based on text content."""
        text_lower = text.lower()
        
        if self.accept_regex.search(text_lower):
            return ButtonType.ACCEPT
        elif self.reject_regex.search(text_lower):
            return ButtonType.REJECT
        elif self.manage_regex.search(text_lower):
            return ButtonType.MANAGE
        elif self.close_regex.search(text_lower):
            return ButtonType.CLOSE
        else:
            # Default to accept if unclear
            return ButtonType.ACCEPT
    
    def _generate_selector(self, element: Tag) -> str:
        """Generate a CSS selector for an element."""
        selectors = []
        
        # Try ID first (but avoid UUIDs and other problematic IDs)
        element_id = element.get('id')
        if element_id and not self._is_problematic_id(element_id):
            selectors.append(f"#{element_id}")
        
        # Try classes (filter out problematic classes)
        classes = element.get('class', [])
        if classes:
            # Filter out UUIDs and very long class names
            filtered_classes = [cls for cls in classes if not self._is_problematic_id(cls) and len(cls) < 50]
            if filtered_classes:
                class_selector = '.' + '.'.join(filtered_classes)
                selectors.append(class_selector)
        
        # Try data attributes
        for attr, value in element.attrs.items():
            if attr.startswith('data-') and not self._is_problematic_id(str(value)):
                selectors.append(f"[{attr}='{value}']")
        
        # Try role attribute
        if element.get('role'):
            selectors.append(f"[role='{element['role']}']")
        
        # Fallback to tag with parent context
        if not selectors:
            selectors.append(self._generate_safe_selector(element))
        
        return ', '.join(selectors)
    
    def _is_problematic_id(self, id_value: str) -> bool:
        """Check if an ID is problematic (UUID, very long, etc.)"""
        if not id_value:
            return True
        
        # Check for UUID pattern
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if re.match(uuid_pattern, id_value, re.IGNORECASE):
            return True
        
        # Check for very long IDs
        if len(id_value) > 100:
            return True
        
        # Check for IDs with only numbers and special characters
        if re.match(r'^[0-9\-_]+$', id_value):
            return True
        
        return False
    
    def _generate_safe_selector(self, element: Tag) -> str:
        """Generate a safe selector when other methods fail."""
        # Use tag name with parent context
        parent = element.parent
        if parent and parent.name != 'body':
            return f"{parent.name} {element.name}"
        else:
            return element.name
    
    def _generate_button_selector(self, element: Tag) -> str:
        """Generate a CSS selector for a button element."""
        return self._generate_selector(element)
    
    def _find_overlay_selectors(self, soup: BeautifulSoup, banner_container: Tag) -> List[str]:
        """Find overlay elements that might need to be hidden."""
        overlay_selectors = []
        
        # Look for common overlay patterns
        overlay_patterns = [
            '.overlay',
            '.backdrop',
            '.modal-backdrop',
            '.cookie-overlay',
            '.consent-overlay',
            '[class*="overlay"]',
            '[class*="backdrop"]'
        ]
        
        for pattern in overlay_patterns:
            try:
                elements = soup.select(pattern)
                for element in elements:
                    if element != banner_container:
                        selector = self._generate_selector(element)
                        if selector not in overlay_selectors:
                            overlay_selectors.append(selector)
            except Exception:
                continue
        
        return overlay_selectors
    
    def _calculate_confidence(self, container: Tag, buttons: List[ConsentButton]) -> float:
        """Calculate confidence score for banner detection."""
        confidence = 0.0
        
        # Base confidence from relevance score
        confidence += self._calculate_relevance_score(container)
        
        # Bonus for having multiple button types
        button_types = {button.button_type for button in buttons}
        if len(button_types) >= 2:
            confidence += 0.2
        
        # Bonus for having accept/reject buttons
        if ButtonType.ACCEPT in button_types and ButtonType.REJECT in button_types:
            confidence += 0.3
        
        # Normalize to 0-1 range
        confidence = min(confidence, 1.0)
        
        return confidence
