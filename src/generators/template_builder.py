"""
Template builder for creating Consent O Matic rule templates.
"""

from typing import Dict, List, Optional, Any
from ..models import BannerInfo, ButtonType, BannerType


class TemplateBuilder:
    """Builds rule templates based on banner information and patterns."""
    
    def __init__(self):
        """Initialize the template builder."""
        self.template_patterns = self._initialize_template_patterns()
        self.action_templates = self._initialize_action_templates()
    
    def _initialize_template_patterns(self) -> Dict[str, Dict]:
        """Initialize template patterns for different banner types."""
        return {
            'modal': {
                'banner_selectors': [
                    '.modal', '.popup', '.overlay', '.dialog', '[role="dialog"]',
                    '[aria-modal="true"]', '.cookie-modal', '.consent-modal'
                ],
                'common_actions': ['hideBanner', 'hideOverlays'],
                'button_patterns': {
                    'accept': ['.accept-btn', '.agree-btn', '.ok-btn', '[data-action="accept"]'],
                    'reject': ['.reject-btn', '.decline-btn', '.no-btn', '[data-action="reject"]'],
                    'close': ['.close-btn', '.dismiss-btn', '.cancel-btn', '[data-action="close"]']
                }
            },
            'bottom_bar': {
                'banner_selectors': [
                    '.bottom-banner', '.cookie-bar', '.consent-bar', '.gdpr-bar',
                    '[style*="bottom"]', '.fixed-bottom', '.sticky-bottom'
                ],
                'common_actions': ['hideBanner'],
                'button_patterns': {
                    'accept': ['.accept', '.agree', '.allow', '.ok'],
                    'reject': ['.reject', '.decline', '.deny', '.no'],
                    'manage': ['.manage', '.settings', '.preferences', '.options']
                }
            },
            'top_bar': {
                'banner_selectors': [
                    '.top-banner', '.header-banner', '.cookie-header', '.consent-header',
                    '[style*="top"]', '.fixed-top', '.sticky-top'
                ],
                'common_actions': ['hideBanner'],
                'button_patterns': {
                    'accept': ['.accept', '.agree', '.allow', '.ok'],
                    'reject': ['.reject', '.decline', '.deny', '.no'],
                    'close': ['.close', '.dismiss', '.×', '.✕']
                }
            },
            'sidebar': {
                'banner_selectors': [
                    '.sidebar', '.panel', '.drawer', '.slide-out',
                    '[style*="right"]', '[style*="left"]', '.fixed-sidebar'
                ],
                'common_actions': ['hideBanner'],
                'button_patterns': {
                    'accept': ['.accept', '.agree', '.allow', '.ok'],
                    'reject': ['.reject', '.decline', '.deny', '.no'],
                    'manage': ['.manage', '.settings', '.preferences', '.options']
                }
            }
        }
    
    def _initialize_action_templates(self) -> Dict[str, List[str]]:
        """Initialize action templates for different scenarios."""
        return {
            'standard_consent': [
                'clickRejectIfPossible',
                'hideBanner'
            ],
            'modal_consent': [
                'clickRejectIfPossible',
                'hideBanner',
                'hideOverlays'
            ],
            'manage_preferences': [
                'clickManageIfAvailable',
                'clickRejectIfPossible',
                'hideBanner'
            ],
            'simple_accept': [
                'clickAcceptIfRejectNotAvailable',
                'hideBanner'
            ],
            'close_only': [
                'clickCloseIfAvailable',
                'hideBanner'
            ]
        }
    
    def build_template(self, banner_info: BannerInfo) -> Dict[str, Any]:
        """
        Build a rule template based on banner information.
        
        Args:
            banner_info: BannerInfo object
            
        Returns:
            Rule template dictionary
        """
        template = {
            'site': banner_info.site,
            'selectors': {},
            'actions': [],
            'metadata': {
                'banner_type': banner_info.banner_type.value,
                'confidence': banner_info.detection_confidence,
                'button_count': len(banner_info.buttons)
            }
        }
        
        # Build selectors based on banner type
        template['selectors'] = self._build_selectors(banner_info)
        
        # Build actions based on banner type and buttons
        template['actions'] = self._build_actions(banner_info)
        
        return template
    
    def _build_selectors(self, banner_info: BannerInfo) -> Dict[str, str]:
        """Build CSS selectors for the template."""
        selectors = {}
        
        # Banner selector
        selectors['banner'] = banner_info.container_selector
        
        # Button selectors
        button_selectors = self._build_button_selectors(banner_info)
        selectors.update(button_selectors)
        
        # Overlay selectors
        if banner_info.overlay_selectors:
            selectors['overlay'] = banner_info.overlay_selectors
        
        # Additional selectors
        selectors.update(banner_info.additional_selectors)
        
        return selectors
    
    def _build_button_selectors(self, banner_info: BannerInfo) -> Dict[str, str]:
        """Build button selectors for the template."""
        button_selectors = {}
        
        # Group buttons by type
        buttons_by_type = {}
        for button in banner_info.buttons:
            button_type = button.button_type.value
            if button_type not in buttons_by_type:
                buttons_by_type[button_type] = []
            buttons_by_type[button_type].append(button)
        
        # Create selectors for each button type
        for button_type, buttons in buttons_by_type.items():
            selector_key = f"{button_type}Button"
            
            if len(buttons) == 1:
                button_selectors[selector_key] = buttons[0].selector
            else:
                # Combine multiple selectors for the same button type
                combined_selectors = [button.selector for button in buttons]
                button_selectors[selector_key] = ', '.join(combined_selectors)
        
        return button_selectors
    
    def _build_actions(self, banner_info: BannerInfo) -> List[str]:
        """Build actions for the template."""
        actions = []
        
        # Determine action strategy based on banner type and buttons
        button_types = {button.button_type for button in banner_info.buttons}
        
        # Choose action template based on banner characteristics
        if BannerType.MODAL == banner_info.banner_type:
            actions.extend(self.action_templates['modal_consent'])
        elif ButtonType.MANAGE in button_types:
            actions.extend(self.action_templates['manage_preferences'])
        elif ButtonType.REJECT in button_types:
            actions.extend(self.action_templates['standard_consent'])
        elif ButtonType.CLOSE in button_types and len(button_types) == 1:
            actions.extend(self.action_templates['close_only'])
        else:
            actions.extend(self.action_templates['simple_accept'])
        
        # Add banner-specific actions
        if banner_info.banner_type == BannerType.MODAL and banner_info.overlay_selectors:
            if 'hideOverlays' not in actions:
                actions.append('hideOverlays')
        
        return actions
    
    def build_fallback_template(self, banner_info: BannerInfo) -> Dict[str, Any]:
        """
        Build a fallback template when normal template building fails.
        
        Args:
            banner_info: BannerInfo object
            
        Returns:
            Fallback template dictionary
        """
        return {
            'site': banner_info.site,
            'selectors': {
                'banner': banner_info.container_selector or '[class*="cookie"], [id*="cookie"]',
                'acceptButton': 'button:contains("Accept"), button:contains("Agree")',
                'rejectButton': 'button:contains("Reject"), button:contains("Decline")'
            },
            'actions': ['hideBanner', 'clickRejectIfPossible'],
            'metadata': {
                'banner_type': 'unknown',
                'confidence': 0.0,
                'fallback': True,
                'button_count': 0
            }
        }
    
    def enhance_template_with_patterns(self, template: Dict[str, Any], banner_info: BannerInfo) -> Dict[str, Any]:
        """
        Enhance template with pattern-based selectors.
        
        Args:
            template: Base template
            banner_info: BannerInfo object
            
        Returns:
            Enhanced template
        """
        enhanced = template.copy()
        
        # Get pattern for banner type
        banner_type = banner_info.banner_type.value
        if banner_type in self.template_patterns:
            patterns = self.template_patterns[banner_type]
            
            # Add fallback selectors based on patterns
            if 'banner' not in enhanced['selectors'] or not enhanced['selectors']['banner']:
                enhanced['selectors']['banner'] = ', '.join(patterns['banner_selectors'])
            
            # Add fallback button selectors
            for button_type, button_patterns in patterns['button_patterns'].items():
                selector_key = f"{button_type}Button"
                if selector_key not in enhanced['selectors'] or not enhanced['selectors'][selector_key]:
                    enhanced['selectors'][selector_key] = ', '.join(button_patterns)
        
        return enhanced
    
    def validate_template(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a rule template.
        
        Args:
            template: Template dictionary
            
        Returns:
            Validation results
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'score': 0.0
        }
        
        score = 0.0
        
        # Check required fields
        required_fields = ['site', 'selectors', 'actions']
        for field in required_fields:
            if field not in template:
                validation['errors'].append(f"Missing required field: {field}")
                validation['valid'] = False
            else:
                score += 0.2
        
        # Check selectors
        if 'selectors' in template:
            selectors = template['selectors']
            if 'banner' not in selectors or not selectors['banner']:
                validation['errors'].append("Missing banner selector")
                validation['valid'] = False
            else:
                score += 0.3
            
            # Check for button selectors
            button_selectors = [key for key in selectors.keys() if 'Button' in key]
            if not button_selectors:
                validation['warnings'].append("No button selectors found")
            else:
                score += 0.2
        
        # Check actions
        if 'actions' in template:
            if not template['actions']:
                validation['warnings'].append("No actions defined")
            else:
                score += 0.2
        
        # Check metadata
        if 'metadata' in template:
            metadata = template['metadata']
            if 'confidence' in metadata and metadata['confidence'] < 0.6:
                validation['warnings'].append(f"Low confidence score: {metadata['confidence']}")
        
        validation['score'] = score
        
        return validation
    
    def get_template_variants(self, banner_info: BannerInfo) -> List[Dict[str, Any]]:
        """
        Get multiple template variants for a banner.
        
        Args:
            banner_info: BannerInfo object
            
        Returns:
            List of template variants
        """
        variants = []
        
        # Standard template
        standard_template = self.build_template(banner_info)
        variants.append(standard_template)
        
        # Enhanced template with patterns
        enhanced_template = self.enhance_template_with_patterns(standard_template, banner_info)
        variants.append(enhanced_template)
        
        # Fallback template
        fallback_template = self.build_fallback_template(banner_info)
        variants.append(fallback_template)
        
        return variants
    
    def compare_templates(self, templates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple templates and recommend the best one.
        
        Args:
            templates: List of template dictionaries
            
        Returns:
            Comparison results
        """
        comparison = {
            'best_template': None,
            'template_scores': [],
            'recommendations': []
        }
        
        best_score = 0.0
        
        for i, template in enumerate(templates):
            validation = self.validate_template(template)
            score = validation['score']
            
            comparison['template_scores'].append({
                'index': i,
                'score': score,
                'valid': validation['valid'],
                'errors': validation['errors'],
                'warnings': validation['warnings']
            })
            
            if score > best_score and validation['valid']:
                best_score = score
                comparison['best_template'] = i
        
        # Generate recommendations
        if comparison['best_template'] is not None:
            best_template = templates[comparison['best_template']]
            
            if best_template['metadata'].get('confidence', 0) < 0.8:
                comparison['recommendations'].append("Consider manual testing due to low confidence")
            
            if len(best_template['selectors']) < 3:
                comparison['recommendations'].append("Template may need additional selectors")
        
        return comparison
