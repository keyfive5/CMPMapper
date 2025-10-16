"""
Button extraction utilities for consent banners.
"""

import re
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup, Tag

from ..models import ConsentButton, ButtonType


class ButtonExtractor:
    """Extracts and analyzes consent buttons from HTML content."""
    
    # Extended button text patterns
    ACCEPT_PATTERNS = [
        r'\baccept\b', r'\bagree\b', r'\bok\b', r'\byes\b', r'\ballow\b', r'\bconsent\b',
        r'\bcontinue\b', r'\bproceed\b', r'\bi accept\b', r'\bi agree\b', r'\bgot it\b',
        r'\baccept all\b', r'\bagree all\b', r'\ballow all\b', r'\baccept cookies\b',
        r'\bagree to cookies\b', r'\benable\b', r'\bturn on\b', r'\bactivate\b'
    ]
    
    REJECT_PATTERNS = [
        r'\bdecline\b', r'\breject\b', r'\bdeny\b', r'\bno\b', r'\brefuse\b', r'\bdisagree\b',
        r'\bopt.?out\b', r'\bnecessary only\b', r'\brequired only\b', r'\bessential only\b',
        r'\breject all\b', r'\bdecline all\b', r'\bdeny all\b', r'\bopt out\b',
        r'\bdisable\b', r'\bturn off\b', r'\bdeactivate\b', r'\bblock\b'
    ]
    
    MANAGE_PATTERNS = [
        r'\bmanage\b', r'\bpreferences\b', r'\bsettings\b', r'\boptions\b', r'\bcustomize\b',
        r'\bchoose\b', r'\bselect\b', r'\bconfigure\b', r'\bcontrol\b', r'\badjust\b',
        r'\bmanage cookies\b', r'\bcookie settings\b', r'\bprivacy settings\b',
        r'\bmanage preferences\b', r'\bcustomize cookies\b'
    ]
    
    CLOSE_PATTERNS = [
        r'\bclose\b', r'\bdismiss\b', r'\b×\b', r'\b✕\b', r'\b×\b', r'\b×\b',
        r'\b×\b', r'\b×\b', r'\b×\b', r'\b×\b'
    ]
    
    MORE_INFO_PATTERNS = [
        r'\bmore info\b', r'\bmore information\b', r'\blearn more\b', r'\bdetails\b',
        r'\babout\b', r'\bwhat\b', r'\bhow\b', r'\bwhy\b', r'\bprivacy policy\b',
        r'\bcookie policy\b', r'\bdata protection\b'
    ]
    
    def __init__(self):
        """Initialize the button extractor."""
        self.accept_regex = re.compile('|'.join(self.ACCEPT_PATTERNS), re.IGNORECASE)
        self.reject_regex = re.compile('|'.join(self.REJECT_PATTERNS), re.IGNORECASE)
        self.manage_regex = re.compile('|'.join(self.MANAGE_PATTERNS), re.IGNORECASE)
        self.close_regex = re.compile('|'.join(self.CLOSE_PATTERNS), re.IGNORECASE)
        self.more_info_regex = re.compile('|'.join(self.MORE_INFO_PATTERNS), re.IGNORECASE)
    
    def extract_buttons_from_html(self, html_content: str, container_selector: str = None) -> List[ConsentButton]:
        """
        Extract consent buttons from HTML content.
        
        Args:
            html_content: HTML content to analyze
            container_selector: Optional CSS selector to limit search to specific container
            
        Returns:
            List of ConsentButton objects
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            if container_selector:
                container = soup.select_one(container_selector)
                if not container:
                    return []
                search_area = container
            else:
                search_area = soup
            
            return self._extract_buttons_from_element(search_area)
            
        except Exception as e:
            print(f"Error extracting buttons from HTML: {e}")
            return []
    
    def _extract_buttons_from_element(self, element: Tag) -> List[ConsentButton]:
        """Extract buttons from a specific element."""
        buttons = []
        
        # Find all button-like elements
        button_elements = element.find_all(['button', 'a', 'input'])
        
        for btn_element in button_elements:
            button = self._analyze_button_element(btn_element)
            if button:
                buttons.append(button)
        
        return buttons
    
    def _analyze_button_element(self, element: Tag) -> Optional[ConsentButton]:
        """Analyze a button element and extract its properties."""
        # Get button text
        text = self._get_button_text(element)
        if not text or len(text.strip()) == 0:
            return None
        
        # Determine button type
        button_type = self._classify_button_type(text)
        
        # Generate selector
        selector = self._generate_button_selector(element)
        
        # Check visibility
        is_visible = self._is_button_visible(element)
        
        # Get attributes
        attributes = dict(element.attrs)
        
        return ConsentButton(
            text=text.strip(),
            button_type=button_type,
            selector=selector,
            is_visible=is_visible,
            attributes=attributes
        )
    
    def _get_button_text(self, element: Tag) -> str:
        """Extract text content from a button element."""
        # For input elements, check value attribute
        if element.name == 'input':
            return element.get('value', '')
        
        # For other elements, get text content
        text = element.get_text()
        
        # Clean up text
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = text.strip()
        
        return text
    
    def _classify_button_type(self, text: str) -> ButtonType:
        """Classify button type based on text content."""
        text_lower = text.lower()
        
        # Check patterns in order of specificity
        if self.accept_regex.search(text_lower):
            return ButtonType.ACCEPT
        elif self.reject_regex.search(text_lower):
            return ButtonType.REJECT
        elif self.manage_regex.search(text_lower):
            return ButtonType.MANAGE
        elif self.close_regex.search(text_lower):
            return ButtonType.CLOSE
        elif self.more_info_regex.search(text_lower):
            return ButtonType.MORE_INFO
        else:
            # Default classification based on context
            return self._default_button_classification(text_lower)
    
    def _default_button_classification(self, text_lower: str) -> ButtonType:
        """Default button classification when patterns don't match."""
        # Single character buttons are usually close buttons
        if len(text_lower.strip()) <= 2:
            return ButtonType.CLOSE
        
        # Buttons with "all" are usually accept/reject
        if 'all' in text_lower:
            if any(word in text_lower for word in ['accept', 'allow', 'enable']):
                return ButtonType.ACCEPT
            elif any(word in text_lower for word in ['reject', 'decline', 'deny']):
                return ButtonType.REJECT
        
        # Default to accept for unclear cases
        return ButtonType.ACCEPT
    
    def _generate_button_selector(self, element: Tag) -> str:
        """Generate a CSS selector for a button element."""
        selectors = []
        
        # Try ID first (most specific)
        if element.get('id'):
            selectors.append(f"#{element['id']}")
        
        # Try classes
        if element.get('class'):
            classes = '.'.join(element['class'])
            selectors.append(f".{classes}")
        
        # Try data attributes
        for attr, value in element.attrs.items():
            if attr.startswith('data-'):
                selectors.append(f"[{attr}='{value}']")
        
        # Try aria-label
        if element.get('aria-label'):
            selectors.append(f"[aria-label='{element['aria-label']}']")
        
        # Try title attribute
        if element.get('title'):
            selectors.append(f"[title='{element['title']}']")
        
        # Fallback to tag with text content
        if not selectors:
            text = self._get_button_text(element)
            if text:
                # Escape special characters in text
                escaped_text = re.escape(text)
                selectors.append(f"{element.name}:contains('{escaped_text}')")
            else:
                selectors.append(element.name)
        
        return ', '.join(selectors)
    
    def _is_button_visible(self, element: Tag) -> bool:
        """Check if a button is likely visible."""
        # Check style attributes
        style = element.get('style', '')
        if 'display: none' in style or 'visibility: hidden' in style:
            return False
        
        # Check classes that might hide the element
        classes = element.get('class', [])
        hidden_classes = ['hidden', 'invisible', 'sr-only', 'screen-reader-only']
        if any(cls in hidden_classes for cls in classes):
            return False
        
        # Check for aria-hidden
        if element.get('aria-hidden') == 'true':
            return False
        
        return True
    
    def group_buttons_by_type(self, buttons: List[ConsentButton]) -> Dict[ButtonType, List[ConsentButton]]:
        """Group buttons by their type."""
        grouped = {}
        for button in buttons:
            if button.button_type not in grouped:
                grouped[button.button_type] = []
            grouped[button.button_type].append(button)
        return grouped
    
    def find_primary_buttons(self, buttons: List[ConsentButton]) -> Dict[ButtonType, ConsentButton]:
        """Find the primary button for each type (most likely to work)."""
        grouped = self.group_buttons_by_type(buttons)
        primary = {}
        
        for button_type, button_list in grouped.items():
            if button_list:
                # Choose the most visible button as primary
                primary_button = max(button_list, key=lambda b: b.is_visible)
                primary[button_type] = primary_button
        
        return primary
    
    def validate_button_selectors(self, buttons: List[ConsentButton], html_content: str) -> List[ConsentButton]:
        """Validate that button selectors work with the HTML content."""
        validated_buttons = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for button in buttons:
                # Try to find the element using the selector
                try:
                    elements = soup.select(button.selector)
                    if elements:
                        validated_buttons.append(button)
                    else:
                        # Try to generate a better selector
                        improved_selector = self._improve_selector(button, soup)
                        if improved_selector:
                            button.selector = improved_selector
                            validated_buttons.append(button)
                except Exception:
                    # Skip invalid selectors
                    continue
            
        except Exception as e:
            print(f"Error validating button selectors: {e}")
            return buttons  # Return original if validation fails
        
        return validated_buttons
    
    def _improve_selector(self, button: ConsentButton, soup: BeautifulSoup) -> Optional[str]:
        """Try to improve a button selector."""
        # This is a simplified implementation
        # In practice, you might want to use more sophisticated selector generation
        text = button.text.lower()
        
        # Try to find by text content
        elements = soup.find_all(['button', 'a', 'input'], string=re.compile(re.escape(text), re.IGNORECASE))
        if elements:
            return self._generate_button_selector(elements[0])
        
        return None
