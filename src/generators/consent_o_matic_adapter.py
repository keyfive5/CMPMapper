"""
Adapter for converting rules to Consent O Matic format.
"""

from typing import Dict, List, Any, Optional
from ..models import ConsentRule, ButtonType


class ConsentOMaticAdapter:
    """Adapts generated rules to Consent O Matic format."""
    
    def __init__(self):
        """Initialize the adapter."""
        self.action_mappings = self._initialize_action_mappings()
        self.selector_mappings = self._initialize_selector_mappings()
    
    def _initialize_action_mappings(self) -> Dict[str, str]:
        """Initialize action mappings to Consent O Matic format."""
        return {
            'clickRejectIfPossible': 'clickRejectIfPossible',
            'clickAcceptIfRejectNotAvailable': 'clickAcceptIfRejectNotAvailable',
            'hideBanner': 'hideBanner',
            'hideOverlays': 'hideOverlays',
            'clickManageIfAvailable': 'clickManageIfAvailable',
            'clickCloseIfAvailable': 'clickCloseIfAvailable'
        }
    
    def _initialize_selector_mappings(self) -> Dict[str, str]:
        """Initialize selector mappings to Consent O Matic format."""
        return {
            'banner': 'banner',
            'acceptButton': 'acceptButton',
            'rejectButton': 'rejectButton',
            'manageButton': 'manageButton',
            'closeButton': 'closeButton',
            'moreInfoButton': 'moreInfoButton',
            'overlay': 'overlay'
        }
    
    def convert_to_consent_o_matic(self, rule: ConsentRule) -> Dict[str, Any]:
        """
        Convert a ConsentRule to Consent O Matic format.
        
        Args:
            rule: ConsentRule object to convert
            
        Returns:
            Dictionary in Consent O Matic format
        """
        consent_o_matic_rule = {
            'site': rule.site,
            'selectors': {},
            'actions': [],
            'metadata': rule.metadata.copy()
        }
        
        # Convert selectors
        consent_o_matic_rule['selectors'] = self._convert_selectors(rule.selectors)
        
        # Convert actions
        consent_o_matic_rule['actions'] = self._convert_actions(rule.actions)
        
        # Add Consent O Matic specific metadata
        consent_o_matic_rule['metadata']['consent_o_matic_version'] = '2.0'
        consent_o_matic_rule['metadata']['generated_by'] = 'CMP Mapper'
        
        return consent_o_matic_rule
    
    def _convert_selectors(self, selectors: Dict[str, str]) -> Dict[str, str]:
        """Convert selectors to Consent O Matic format."""
        converted = {}
        
        for key, value in selectors.items():
            # Map to Consent O Matic format
            mapped_key = self.selector_mappings.get(key, key)
            
            if isinstance(value, list):
                # Convert list of selectors to comma-separated string
                converted[mapped_key] = ', '.join(value)
            else:
                converted[mapped_key] = value
        
        return converted
    
    def _convert_actions(self, actions: List[str]) -> List[str]:
        """Convert actions to Consent O Matic format."""
        converted = []
        
        for action in actions:
            # Map to Consent O Matic format
            mapped_action = self.action_mappings.get(action, action)
            converted.append(mapped_action)
        
        return converted
    
    def validate_consent_o_matic_format(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that a rule is in proper Consent O Matic format.
        
        Args:
            rule: Rule dictionary to validate
            
        Returns:
            Validation results
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'format_version': None
        }
        
        # Check required fields
        required_fields = ['site', 'selectors', 'actions']
        for field in required_fields:
            if field not in rule:
                validation['errors'].append(f"Missing required field: {field}")
                validation['valid'] = False
        
        # Check selectors format
        if 'selectors' in rule:
            selectors = rule['selectors']
            if not isinstance(selectors, dict):
                validation['errors'].append("Selectors must be a dictionary")
                validation['valid'] = False
            else:
                # Check for required selector types
                if 'banner' not in selectors:
                    validation['errors'].append("Missing banner selector")
                    validation['valid'] = False
        
        # Check actions format
        if 'actions' in rule:
            actions = rule['actions']
            if not isinstance(actions, list):
                validation['errors'].append("Actions must be a list")
                validation['valid'] = False
            else:
                # Check for valid actions
                valid_actions = list(self.action_mappings.values())
                for action in actions:
                    if action not in valid_actions:
                        validation['warnings'].append(f"Unknown action: {action}")
        
        # Check metadata
        if 'metadata' in rule:
            metadata = rule['metadata']
            if 'consent_o_matic_version' in metadata:
                validation['format_version'] = metadata['consent_o_matic_version']
        
        return validation
    
    def create_consent_o_matic_manifest(self, rules: List[ConsentRule]) -> Dict[str, Any]:
        """
        Create a Consent O Matic manifest for multiple rules.
        
        Args:
            rules: List of ConsentRule objects
            
        Returns:
            Manifest dictionary
        """
        manifest = {
            'version': '2.0',
            'generator': 'CMP Mapper',
            'generated_at': rules[0].metadata.get('generated_at') if rules else None,
            'total_rules': len(rules),
            'rules': []
        }
        
        for rule in rules:
            consent_o_matic_rule = self.convert_to_consent_o_matic(rule)
            manifest['rules'].append(consent_o_matic_rule)
        
        return manifest
    
    def export_for_consent_o_matic(self, rules: List[ConsentRule], format_type: str = 'json') -> str:
        """
        Export rules in a format compatible with Consent O Matic.
        
        Args:
            rules: List of ConsentRule objects
            format_type: Export format ('json', 'js', 'ts')
            
        Returns:
            Exported content as string
        """
        if format_type == 'json':
            return self._export_json(rules)
        elif format_type == 'js':
            return self._export_javascript(rules)
        elif format_type == 'ts':
            return self._export_typescript(rules)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
    
    def _export_json(self, rules: List[ConsentRule]) -> str:
        """Export rules as JSON."""
        import json
        
        if len(rules) == 1:
            return json.dumps(self.convert_to_consent_o_matic(rules[0]), indent=2)
        else:
            manifest = self.create_consent_o_matic_manifest(rules)
            return json.dumps(manifest, indent=2)
    
    def _export_javascript(self, rules: List[ConsentRule]) -> str:
        """Export rules as JavaScript module."""
        js_content = [
            "// Generated by CMP Mapper",
            "// Consent O Matic compatible rules",
            "",
            "const consentRules = ["
        ]
        
        for rule in rules:
            consent_o_matic_rule = self.convert_to_consent_o_matic(rule)
            js_content.append("  " + str(consent_o_matic_rule).replace("'", '"') + ",")
        
        js_content.extend([
            "];",
            "",
            "module.exports = consentRules;"
        ])
        
        return "\n".join(js_content)
    
    def _export_typescript(self, rules: List[ConsentRule]) -> str:
        """Export rules as TypeScript module."""
        ts_content = [
            "// Generated by CMP Mapper",
            "// Consent O Matic compatible rules",
            "",
            "interface ConsentRule {",
            "  site: string;",
            "  selectors: Record<string, string>;",
            "  actions: string[];",
            "  metadata: Record<string, any>;",
            "}",
            "",
            "const consentRules: ConsentRule[] = ["
        ]
        
        for rule in rules:
            consent_o_matic_rule = self.convert_to_consent_o_matic(rule)
            ts_content.append("  " + str(consent_o_matic_rule).replace("'", '"') + ",")
        
        ts_content.extend([
            "];",
            "",
            "export default consentRules;"
        ])
        
        return "\n".join(ts_content)
    
    def create_rule_template(self, banner_type: str = 'generic') -> Dict[str, Any]:
        """
        Create a template rule for a specific banner type.
        
        Args:
            banner_type: Type of banner ('modal', 'bottom_bar', 'top_bar', etc.)
            
        Returns:
            Template rule dictionary
        """
        templates = {
            'modal': {
                'site': 'example.com',
                'selectors': {
                    'banner': '.cookie-modal, .consent-modal, [role="dialog"]',
                    'acceptButton': '.accept-btn, .agree-btn, button:contains("Accept")',
                    'rejectButton': '.reject-btn, .decline-btn, button:contains("Reject")',
                    'closeButton': '.close-btn, .dismiss-btn, [aria-label="Close"]'
                },
                'actions': ['clickRejectIfPossible', 'hideBanner', 'hideOverlays'],
                'metadata': {
                    'banner_type': 'modal',
                    'confidence_score': 0.0,
                    'template': True
                }
            },
            'bottom_bar': {
                'site': 'example.com',
                'selectors': {
                    'banner': '.cookie-bar, .consent-bar, .gdpr-banner',
                    'acceptButton': '.accept, .agree, button:contains("Accept")',
                    'rejectButton': '.reject, .decline, button:contains("Reject")',
                    'manageButton': '.manage, .settings, button:contains("Manage")'
                },
                'actions': ['clickRejectIfPossible', 'hideBanner'],
                'metadata': {
                    'banner_type': 'bottom_bar',
                    'confidence_score': 0.0,
                    'template': True
                }
            },
            'generic': {
                'site': 'example.com',
                'selectors': {
                    'banner': '[class*="cookie"], [id*="cookie"], [class*="consent"]',
                    'acceptButton': 'button:contains("Accept"), button:contains("Agree")',
                    'rejectButton': 'button:contains("Reject"), button:contains("Decline")'
                },
                'actions': ['hideBanner', 'clickRejectIfPossible'],
                'metadata': {
                    'banner_type': 'generic',
                    'confidence_score': 0.0,
                    'template': True
                }
            }
        }
        
        return templates.get(banner_type, templates['generic'])
    
    def merge_rules(self, rules: List[ConsentRule], merge_strategy: str = 'highest_confidence') -> ConsentRule:
        """
        Merge multiple rules for the same site.
        
        Args:
            rules: List of ConsentRule objects for the same site
            merge_strategy: Strategy for merging ('highest_confidence', 'most_selectors', 'combine')
            
        Returns:
            Merged ConsentRule object
        """
        if not rules:
            raise ValueError("No rules to merge")
        
        if len(rules) == 1:
            return rules[0]
        
        # Choose base rule based on strategy
        if merge_strategy == 'highest_confidence':
            base_rule = max(rules, key=lambda r: r.metadata.get('confidence_score', 0))
        elif merge_strategy == 'most_selectors':
            base_rule = max(rules, key=lambda r: len(r.selectors))
        else:  # combine
            base_rule = rules[0]
        
        merged = ConsentRule(
            site=base_rule.site,
            selectors=base_rule.selectors.copy(),
            actions=base_rule.actions.copy(),
            metadata=base_rule.metadata.copy()
        )
        
        if merge_strategy == 'combine':
            # Combine selectors from all rules
            for rule in rules[1:]:
                for key, value in rule.selectors.items():
                    if key in merged.selectors:
                        # Combine selectors
                        if isinstance(value, list):
                            if isinstance(merged.selectors[key], list):
                                merged.selectors[key].extend(value)
                            else:
                                merged.selectors[key] = [merged.selectors[key]] + value
                        else:
                            if isinstance(merged.selectors[key], list):
                                merged.selectors[key].append(value)
                            else:
                                merged.selectors[key] = [merged.selectors[key], value]
                    else:
                        merged.selectors[key] = value
            
            # Combine actions
            all_actions = set()
            for rule in rules:
                all_actions.update(rule.actions)
            merged.actions = list(all_actions)
        
        # Update metadata
        merged.metadata['merged'] = True
        merged.metadata['original_rule_count'] = len(rules)
        merged.metadata['merge_strategy'] = merge_strategy
        
        return merged
