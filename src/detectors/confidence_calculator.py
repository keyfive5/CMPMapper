"""
Confidence calculation utilities for banner detection.
"""

from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup, Tag

from ..models import BannerInfo, ButtonType, BannerType


class ConfidenceCalculator:
    """Calculates confidence scores for banner detection results."""
    
    def __init__(self):
        """Initialize the confidence calculator."""
        self.weights = self._initialize_weights()
        self.thresholds = self._initialize_thresholds()
    
    def _initialize_weights(self) -> Dict[str, float]:
        """Initialize weights for different confidence factors."""
        return {
            'text_content': 0.25,
            'button_analysis': 0.30,
            'structural_analysis': 0.20,
            'selector_quality': 0.15,
            'attribute_analysis': 0.10
        }
    
    def _initialize_thresholds(self) -> Dict[str, float]:
        """Initialize confidence thresholds for different scenarios."""
        return {
            'minimum_confidence': 0.6,
            'high_confidence': 0.8,
            'very_high_confidence': 0.9,
            'button_confidence_threshold': 0.7,
            'selector_confidence_threshold': 0.8
        }
    
    def calculate_overall_confidence(self, banner_info: BannerInfo, html_content: str) -> float:
        """
        Calculate overall confidence score for banner detection.
        
        Args:
            banner_info: BannerInfo object to analyze
            html_content: Full HTML content for context
            
        Returns:
            Confidence score between 0 and 1
        """
        try:
            # Calculate individual confidence components
            text_confidence = self._calculate_text_confidence(banner_info, html_content)
            button_confidence = self._calculate_button_confidence(banner_info)
            structural_confidence = self._calculate_structural_confidence(banner_info)
            selector_confidence = self._calculate_selector_confidence(banner_info, html_content)
            attribute_confidence = self._calculate_attribute_confidence(banner_info)
            
            # Weight and combine confidence scores
            overall_confidence = (
                text_confidence * self.weights['text_content'] +
                button_confidence * self.weights['button_analysis'] +
                structural_confidence * self.weights['structural_analysis'] +
                selector_confidence * self.weights['selector_quality'] +
                attribute_confidence * self.weights['attribute_analysis']
            )
            
            # Apply additional confidence adjustments
            overall_confidence = self._apply_confidence_adjustments(
                overall_confidence, banner_info, html_content
            )
            
            return min(max(overall_confidence, 0.0), 1.0)
            
        except Exception as e:
            print(f"Error calculating overall confidence: {e}")
            return 0.0
    
    def _calculate_text_confidence(self, banner_info: BannerInfo, html_content: str) -> float:
        """Calculate confidence based on text content analysis."""
        confidence = 0.0
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            banner_element = soup.select_one(banner_info.container_selector)
            
            if not banner_element:
                return 0.0
            
            text = banner_element.get_text().lower()
            
            # Check for consent-related keywords
            consent_keywords = [
                'cookie', 'consent', 'gdpr', 'privacy', 'tracking',
                'analytics', 'advertising', 'personalization'
            ]
            
            keyword_matches = sum(1 for keyword in consent_keywords if keyword in text)
            confidence += (keyword_matches / len(consent_keywords)) * 0.6
            
            # Check for button-related text
            button_keywords = ['accept', 'agree', 'decline', 'reject', 'manage', 'settings']
            button_matches = sum(1 for keyword in button_keywords if keyword in text)
            confidence += (button_matches / len(button_keywords)) * 0.4
            
        except Exception as e:
            print(f"Error calculating text confidence: {e}")
        
        return min(confidence, 1.0)
    
    def _calculate_button_confidence(self, banner_info: BannerInfo) -> float:
        """Calculate confidence based on button analysis."""
        if not banner_info.buttons:
            return 0.0
        
        confidence = 0.0
        
        # Count different button types
        button_types = {button.button_type for button in banner_info.buttons}
        
        # Base confidence for having buttons
        confidence += 0.3
        
        # Bonus for having multiple button types
        if len(button_types) >= 2:
            confidence += 0.2
        
        if len(button_types) >= 3:
            confidence += 0.1
        
        # Bonus for having accept/reject pair
        if ButtonType.ACCEPT in button_types and ButtonType.REJECT in button_types:
            confidence += 0.2
        
        # Bonus for having manage button
        if ButtonType.MANAGE in button_types:
            confidence += 0.1
        
        # Check button text quality
        for button in banner_info.buttons:
            if button.text and len(button.text.strip()) > 0:
                confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _calculate_structural_confidence(self, banner_info: BannerInfo) -> float:
        """Calculate confidence based on structural analysis."""
        confidence = 0.0
        
        # Banner type confidence
        if banner_info.banner_type in [BannerType.MODAL, BannerType.BOTTOM_BAR]:
            confidence += 0.4
        elif banner_info.banner_type in [BannerType.TOP_BAR, BannerType.SIDEBAR]:
            confidence += 0.3
        else:
            confidence += 0.2
        
        # Overlay detection
        if banner_info.overlay_selectors:
            confidence += 0.2
        
        # Additional selectors
        if banner_info.additional_selectors:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_selector_confidence(self, banner_info: BannerInfo, html_content: str) -> float:
        """Calculate confidence based on selector quality."""
        confidence = 0.0
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Test banner selector
            banner_element = soup.select_one(banner_info.container_selector)
            if banner_element:
                confidence += 0.4
                
                # Bonus for specific selector types
                if '#' in banner_info.container_selector:  # ID selector
                    confidence += 0.2
                elif 'data-' in banner_info.container_selector:  # Data attribute
                    confidence += 0.15
                elif 'aria-' in banner_info.container_selector:  # ARIA attribute
                    confidence += 0.1
            
            # Test button selectors
            working_button_selectors = 0
            for button in banner_info.buttons:
                if soup.select_one(button.selector):
                    working_button_selectors += 1
            
            if banner_info.buttons:
                button_confidence = working_button_selectors / len(banner_info.buttons)
                confidence += button_confidence * 0.4
            
        except Exception as e:
            print(f"Error calculating selector confidence: {e}")
        
        return min(confidence, 1.0)
    
    def _calculate_attribute_confidence(self, banner_info: BannerInfo) -> float:
        """Calculate confidence based on attribute analysis."""
        confidence = 0.0
        
        # Check for stable attributes in container selector
        stable_attributes = ['data-consent', 'data-cookie', 'data-gdpr', 'aria-label', 'role']
        
        for attr in stable_attributes:
            if attr in banner_info.container_selector:
                confidence += 0.2
        
        # Check button attributes
        for button in banner_info.buttons:
            if button.attributes:
                # Check for stable button attributes
                stable_button_attrs = ['data-action', 'data-consent', 'aria-label', 'role']
                for attr in stable_button_attrs:
                    if attr in button.attributes:
                        confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _apply_confidence_adjustments(self, base_confidence: float, banner_info: BannerInfo, html_content: str) -> float:
        """Apply additional confidence adjustments based on context."""
        adjusted_confidence = base_confidence
        
        # Adjust based on banner size and content
        if banner_info.html_content:
            html_size = len(banner_info.html_content)
            if html_size > 500:  # Substantial banner content
                adjusted_confidence += 0.05
            elif html_size < 100:  # Very small banner
                adjusted_confidence -= 0.1
        
        # Adjust based on button visibility
        visible_buttons = sum(1 for button in banner_info.buttons if button.is_visible)
        if visible_buttons == 0:
            adjusted_confidence -= 0.1
        elif visible_buttons >= len(banner_info.buttons) * 0.8:
            adjusted_confidence += 0.05
        
        # Adjust based on selector specificity
        if self._is_selector_specific(banner_info.container_selector):
            adjusted_confidence += 0.05
        
        return adjusted_confidence
    
    def _is_selector_specific(self, selector: str) -> bool:
        """Check if a selector is specific enough."""
        # Specific selectors are more reliable
        specific_indicators = ['#', '[data-', '[aria-', '[role=']
        return any(indicator in selector for indicator in specific_indicators)
    
    def get_confidence_breakdown(self, banner_info: BannerInfo, html_content: str) -> Dict[str, float]:
        """
        Get detailed confidence breakdown for debugging.
        
        Args:
            banner_info: BannerInfo object to analyze
            html_content: Full HTML content for context
            
        Returns:
            Dictionary with confidence breakdown
        """
        return {
            'text_confidence': self._calculate_text_confidence(banner_info, html_content),
            'button_confidence': self._calculate_button_confidence(banner_info),
            'structural_confidence': self._calculate_structural_confidence(banner_info),
            'selector_confidence': self._calculate_selector_confidence(banner_info, html_content),
            'attribute_confidence': self._calculate_attribute_confidence(banner_info),
            'overall_confidence': self.calculate_overall_confidence(banner_info, html_content)
        }
    
    def is_confidence_sufficient(self, confidence: float, threshold_type: str = 'minimum') -> bool:
        """
        Check if confidence score meets the specified threshold.
        
        Args:
            confidence: Confidence score to check
            threshold_type: Type of threshold to use
            
        Returns:
            True if confidence is sufficient, False otherwise
        """
        threshold = self.thresholds.get(threshold_type, self.thresholds['minimum_confidence'])
        return confidence >= threshold
    
    def get_confidence_level(self, confidence: float) -> str:
        """
        Get confidence level description.
        
        Args:
            confidence: Confidence score
            
        Returns:
            Confidence level description
        """
        if confidence >= self.thresholds['very_high_confidence']:
            return 'very_high'
        elif confidence >= self.thresholds['high_confidence']:
            return 'high'
        elif confidence >= self.thresholds['minimum_confidence']:
            return 'medium'
        else:
            return 'low'
    
    def compare_banner_confidence(self, banners: List[BannerInfo], html_content: str) -> List[Tuple[BannerInfo, float]]:
        """
        Compare confidence scores of multiple banners.
        
        Args:
            banners: List of BannerInfo objects
            html_content: HTML content for context
            
        Returns:
            List of (BannerInfo, confidence) tuples sorted by confidence
        """
        banner_confidences = []
        
        for banner in banners:
            confidence = self.calculate_overall_confidence(banner, html_content)
            banner_confidences.append((banner, confidence))
        
        # Sort by confidence (highest first)
        banner_confidences.sort(key=lambda x: x[1], reverse=True)
        
        return banner_confidences
    
    def filter_by_confidence(self, banners: List[BannerInfo], html_content: str, 
                           min_confidence: float = None) -> List[BannerInfo]:
        """
        Filter banners by minimum confidence threshold.
        
        Args:
            banners: List of BannerInfo objects
            html_content: HTML content for context
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of banners meeting the confidence threshold
        """
        if min_confidence is None:
            min_confidence = self.thresholds['minimum_confidence']
        
        filtered_banners = []
        
        for banner in banners:
            confidence = self.calculate_overall_confidence(banner, html_content)
            if confidence >= min_confidence:
                filtered_banners.append(banner)
        
        return filtered_banners
