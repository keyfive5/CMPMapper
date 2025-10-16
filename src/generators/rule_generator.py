"""
Rule template generator for Consent O Matic compatible JSON rules.
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import urlparse

from ..models import BannerInfo, ConsentRule, ButtonType, BannerType
from .template_builder import TemplateBuilder
from .consent_o_matic_adapter import ConsentOMaticAdapter


class RuleGenerator:
    """Generates Consent O Matic compatible rule templates from banner information."""
    
    def __init__(self):
        """Initialize the rule generator."""
        self.template_builder = TemplateBuilder()
        self.adapter = ConsentOMaticAdapter()
        
        # Default rule template structure
        self.default_template = {
            "site": "",
            "selectors": {
                "banner": "",
                "acceptButton": "",
                "rejectButton": "",
                "manageButton": "",
                "closeButton": "",
                "overlay": []
            },
            "actions": [],
            "metadata": {
                "generated_at": "",
                "generator_version": "0.1.0",
                "confidence_score": 0.0,
                "banner_type": "",
                "tested": False
            }
        }
    
    def generate_rule(self, banner_info: BannerInfo, site_url: str = None) -> ConsentRule:
        """
        Generate a Consent O Matic rule from banner information.
        
        Args:
            banner_info: BannerInfo object containing banner data
            site_url: Optional site URL (defaults to banner_info.site)
            
        Returns:
            ConsentRule object
        """
        try:
            # Extract site domain
            site = site_url or banner_info.site
            domain = self._extract_domain(site)
            
            # Generate selectors
            selectors = self._generate_selectors(banner_info)
            
            # Generate actions
            actions = self._generate_actions(banner_info)
            
            # Create metadata
            metadata = self._generate_metadata(banner_info)
            
            # Create rule
            rule = ConsentRule(
                site=domain,
                selectors=selectors,
                actions=actions,
                metadata=metadata
            )
            
            return rule
            
        except Exception as e:
            print(f"Error generating rule: {e}")
            return self._create_fallback_rule(banner_info, site_url)
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc or url
        except Exception:
            return url
    
    def _generate_selectors(self, banner_info: BannerInfo) -> Dict[str, str]:
        """Generate CSS selectors for the rule."""
        selectors = {}
        
        # Banner selector
        selectors['banner'] = banner_info.container_selector
        
        # Button selectors
        for button in banner_info.buttons:
            button_type = button.button_type.value
            selector_key = f"{button_type}Button"
            
            if selector_key not in selectors:
                selectors[selector_key] = button.selector
            else:
                # Combine multiple selectors for the same button type
                existing = selectors[selector_key]
                selectors[selector_key] = f"{existing}, {button.selector}"
        
        # Overlay selectors
        if banner_info.overlay_selectors:
            selectors['overlay'] = banner_info.overlay_selectors
        
        # Additional selectors
        selectors.update(banner_info.additional_selectors)
        
        return selectors
    
    def _generate_actions(self, banner_info: BannerInfo) -> List[str]:
        """Generate actions for the rule."""
        actions = []
        
        # Determine banner type and add appropriate actions
        if banner_info.banner_type == BannerType.MODAL:
            actions.append("hideBanner")
        elif banner_info.banner_type == BannerType.BOTTOM_BAR:
            actions.append("hideBanner")
        elif banner_info.banner_type == BannerType.TOP_BAR:
            actions.append("hideBanner")
        
        # Add reject action if reject button is available
        has_reject = any(button.button_type == ButtonType.REJECT for button in banner_info.buttons)
        if has_reject:
            actions.append("clickRejectIfPossible")
        else:
            actions.append("clickAcceptIfRejectNotAvailable")
        
        # Add overlay hiding if overlays are detected
        if banner_info.overlay_selectors:
            actions.append("hideOverlays")
        
        return actions
    
    def _generate_metadata(self, banner_info: BannerInfo) -> Dict[str, Any]:
        """Generate metadata for the rule."""
        return {
            "generated_at": datetime.now().isoformat(),
            "generator_version": "0.1.0",
            "confidence_score": banner_info.detection_confidence,
            "banner_type": banner_info.banner_type.value,
            "button_count": len(banner_info.buttons),
            "button_types": [button.button_type.value for button in banner_info.buttons],
            "has_overlays": len(banner_info.overlay_selectors) > 0,
            "tested": False,
            "original_site": banner_info.site
        }
    
    def _create_fallback_rule(self, banner_info: BannerInfo, site_url: str = None) -> ConsentRule:
        """Create a fallback rule when generation fails."""
        site = site_url or banner_info.site or "unknown"
        domain = self._extract_domain(site)
        
        return ConsentRule(
            site=domain,
            selectors={
                "banner": banner_info.container_selector or "[class*='cookie'], [id*='cookie']",
                "acceptButton": "button:contains('Accept'), button:contains('Agree')",
                "rejectButton": "button:contains('Reject'), button:contains('Decline')"
            },
            actions=["hideBanner", "clickRejectIfPossible"],
            metadata={
                "generated_at": datetime.now().isoformat(),
                "generator_version": "0.1.0",
                "confidence_score": 0.0,
                "banner_type": "unknown",
                "tested": False,
                "fallback": True
            }
        )
    
    def generate_multiple_rules(self, banners: List[BannerInfo], site_url: str = None) -> List[ConsentRule]:
        """
        Generate rules for multiple banners.
        
        Args:
            banners: List of BannerInfo objects
            site_url: Optional site URL
            
        Returns:
            List of ConsentRule objects
        """
        rules = []
        
        for banner in banners:
            rule = self.generate_rule(banner, site_url)
            rules.append(rule)
        
        return rules
    
    def save_rule(self, rule: ConsentRule, filename: str = None) -> str:
        """
        Save a rule to a JSON file.
        
        Args:
            rule: ConsentRule object to save
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        try:
            os.makedirs("data/rules", exist_ok=True)
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{rule.site}_{timestamp}.json"
            
            # Ensure filename has .json extension
            if not filename.endswith('.json'):
                filename += '.json'
            
            filepath = os.path.join("data/rules", filename)
            
            # Convert to Consent O Matic format
            consent_o_matic_rule = self.adapter.convert_to_consent_o_matic(rule)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(consent_o_matic_rule, f, indent=2, ensure_ascii=False)
            
            print(f"Rule saved to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error saving rule: {e}")
            return ""
    
    def save_rules_batch(self, rules: List[ConsentRule], base_filename: str = None) -> List[str]:
        """
        Save multiple rules to separate files.
        
        Args:
            rules: List of ConsentRule objects
            base_filename: Optional base filename prefix
            
        Returns:
            List of file paths
        """
        saved_files = []
        
        for i, rule in enumerate(rules):
            if base_filename:
                filename = f"{base_filename}_{i+1}.json"
            else:
                filename = None
            
            filepath = self.save_rule(rule, filename)
            if filepath:
                saved_files.append(filepath)
        
        return saved_files
    
    def create_rule_summary(self, rules: List[ConsentRule]) -> Dict[str, Any]:
        """
        Create a summary of generated rules.
        
        Args:
            rules: List of ConsentRule objects
            
        Returns:
            Summary dictionary
        """
        summary = {
            "total_rules": len(rules),
            "sites": [],
            "banner_types": {},
            "confidence_scores": [],
            "action_counts": {},
            "generated_at": datetime.now().isoformat()
        }
        
        for rule in rules:
            # Sites
            summary["sites"].append(rule.site)
            
            # Banner types
            banner_type = rule.metadata.get("banner_type", "unknown")
            summary["banner_types"][banner_type] = summary["banner_types"].get(banner_type, 0) + 1
            
            # Confidence scores
            confidence = rule.metadata.get("confidence_score", 0.0)
            summary["confidence_scores"].append(confidence)
            
            # Action counts
            for action in rule.actions:
                summary["action_counts"][action] = summary["action_counts"].get(action, 0) + 1
        
        # Calculate statistics
        if summary["confidence_scores"]:
            summary["avg_confidence"] = sum(summary["confidence_scores"]) / len(summary["confidence_scores"])
            summary["min_confidence"] = min(summary["confidence_scores"])
            summary["max_confidence"] = max(summary["confidence_scores"])
        
        return summary
    
    def save_rule_summary(self, summary: Dict[str, Any], filename: str = None) -> str:
        """
        Save rule summary to a JSON file.
        
        Args:
            summary: Summary dictionary
            filename: Optional filename
            
        Returns:
            Path to saved file
        """
        try:
            os.makedirs("data/rules", exist_ok=True)
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"rule_summary_{timestamp}.json"
            
            if not filename.endswith('.json'):
                filename += '.json'
            
            filepath = os.path.join("data/rules", filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            print(f"Rule summary saved to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error saving rule summary: {e}")
            return ""
    
    def validate_rule(self, rule: ConsentRule) -> Dict[str, Any]:
        """
        Validate a generated rule.
        
        Args:
            rule: ConsentRule object to validate
            
        Returns:
            Validation results
        """
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "score": 0.0
        }
        
        score = 0.0
        
        # Check required fields
        if not rule.site:
            validation["errors"].append("Missing site field")
            validation["valid"] = False
        else:
            score += 0.2
        
        # Check selectors
        if not rule.selectors.get("banner"):
            validation["errors"].append("Missing banner selector")
            validation["valid"] = False
        else:
            score += 0.3
        
        # Check for at least one button selector
        button_selectors = [key for key in rule.selectors.keys() if "Button" in key]
        if not button_selectors:
            validation["warnings"].append("No button selectors found")
        else:
            score += 0.3
        
        # Check actions
        if not rule.actions:
            validation["warnings"].append("No actions defined")
        else:
            score += 0.2
        
        # Check confidence score
        confidence = rule.metadata.get("confidence_score", 0.0)
        if confidence < 0.6:
            validation["warnings"].append(f"Low confidence score: {confidence}")
        
        validation["score"] = score
        
        return validation
    
    def optimize_rule(self, rule: ConsentRule) -> ConsentRule:
        """
        Optimize a rule for better performance and reliability.
        
        Args:
            rule: ConsentRule object to optimize
            
        Returns:
            Optimized ConsentRule object
        """
        optimized = ConsentRule(
            site=rule.site,
            selectors=rule.selectors.copy(),
            actions=rule.actions.copy(),
            metadata=rule.metadata.copy()
        )
        
        # Optimize selectors
        optimized.selectors = self._optimize_selectors(optimized.selectors)
        
        # Optimize actions
        optimized.actions = self._optimize_actions(optimized.actions)
        
        # Update metadata
        optimized.metadata["optimized"] = True
        optimized.metadata["optimized_at"] = datetime.now().isoformat()
        
        return optimized
    
    def _optimize_selectors(self, selectors: Dict[str, str]) -> Dict[str, str]:
        """Optimize CSS selectors for better performance."""
        optimized = {}
        
        for key, value in selectors.items():
            if isinstance(value, list):
                # Optimize list of selectors
                optimized_list = []
                for selector in value:
                    if selector and selector.strip():
                        optimized_list.append(selector.strip())
                optimized[key] = optimized_list
            else:
                # Optimize single selector
                if value and value.strip():
                    optimized[key] = value.strip()
        
        return optimized
    
    def _optimize_actions(self, actions: List[str]) -> List[str]:
        """Optimize action list."""
        # Remove duplicates while preserving order
        seen = set()
        optimized = []
        
        for action in actions:
            if action not in seen:
                seen.add(action)
                optimized.append(action)
        
        return optimized
