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
            selectors['overlay'] = ', '.join(banner_info.overlay_selectors)
        
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
    
    def generate_consent_o_matic_json(self, banner_info: BannerInfo) -> dict:
        """Generate proper Consent O Matic JSON format (array-based structure for editor)."""
        
        # Extract site name for the rule key
        site_name = self._get_site_name(banner_info.site)
        
        # Create the proper Consent O Matic structure (array-based format for editor)
        rule = {
            "$schema": "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules.schema.json",
            f"{site_name} CMP": {
                "detectors": [
                    {
                        "presentMatcher": [
                            {
                                "type": "css",
                                "target": {
                                    "selector": banner_info.container_selector
                                }
                            }
                        ],
                        "showingMatcher": [
                            {
                                "type": "css",
                                "target": {
                                    "selector": banner_info.container_selector
                                }
                            }
                        ]
                    }
                ],
                "methods": [
                    {
                        "name": "HIDE_CMP"
                    },
                    {
                        "name": "OPEN_OPTIONS"
                    },
                    {
                        "name": "SAVE_CONSENT"
                    },
                    {
                        "name": "UTILITY"
                    }
                ]
            }
        }
        
        # Add DO_CONSENT method if accept button exists
        accept_buttons = [btn for btn in banner_info.buttons if btn.button_type.value == "accept"]
        if accept_buttons:
            # Prioritize buttons with better selectors (avoid generic selectors like "p a")
            best_button = self._select_best_accept_button(accept_buttons)
            
            consent_method = {
                "action": {
                    "type": "click",
                    "target": {
                        "selector": best_button.selector
                    }
                },
                "name": "DO_CONSENT"
            }
            rule[f"{site_name} CMP"]["methods"].insert(2, consent_method)
        
        return rule
    
    def _select_best_accept_button(self, accept_buttons: list) -> object:
        """
        Select the best accept button from a list of accept buttons.
        Prioritizes buttons with specific selectors over generic ones.
        """
        # Priority order for button selectors (best to worst)
        priority_patterns = [
            r'\.cookies-notification-button',  # Specific cookie notification button
            r'\.cookie-consent',  # Cookie consent button
            r'\.consent-button',  # Consent button
            r'\.accept-button',  # Accept button
            r'\.btn.*accept',  # Button with accept in class
            r'\[data-.*accept.*\]',  # Data attribute with accept
            r'button.*accept',  # Button element with accept text
        ]
        
        # Generic selectors to avoid (worst)
        avoid_patterns = [
            r'p a',  # Generic paragraph link
            r'a$',  # Generic anchor
            r'button$',  # Generic button
        ]
        
        import re
        
        # Score each button
        best_button = accept_buttons[0]  # Default to first button
        best_score = -1
        
        for button in accept_buttons:
            score = 0
            selector = button.selector.lower()
            
            # Check for priority patterns (higher score = better)
            for i, pattern in enumerate(priority_patterns):
                if re.search(pattern, selector):
                    score += len(priority_patterns) - i  # Higher score for earlier patterns
                    break
            
            # Check for avoid patterns (negative score)
            for pattern in avoid_patterns:
                if re.search(pattern, selector):
                    score -= 10  # Heavy penalty for generic selectors
                    break
            
            # Bonus for specific button text
            if button.text and button.text.lower() in ['accept', 'accept all', 'agree', 'consent']:
                score += 5
            
            if score > best_score:
                best_score = score
                best_button = button
        
        return best_button
    
    def _get_site_name(self, site_url: str) -> str:
        """Extract a clean site name from URL."""
        # Remove protocol and get domain
        domain = site_url.replace("https://", "").replace("http://", "").replace("www.", "")
        # Remove path and get just the domain
        domain = domain.split("/")[0]
        return domain
    
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
    
    def generate_multi_site_rule(self, banners: List[BannerInfo]) -> ConsentRule:
        """
        Generate a single rule that works across multiple sites with similar banners.
        
        Args:
            banners: List of BannerInfo objects from different sites
            
        Returns:
            ConsentRule object optimized for multiple sites
        """
        if not banners:
            raise ValueError("No banners provided for multi-site rule generation")
        
        # Extract common patterns across all banners
        common_selectors = self._find_common_selectors(banners)
        common_actions = self._find_common_actions(banners)
        
        # Create combined site identifier
        sites = [self._extract_domain(banner.site) for banner in banners]
        combined_site = f"multi-site-{len(sites)}-sites"
        
        # Calculate average confidence
        avg_confidence = sum(banner.detection_confidence for banner in banners) / len(banners)
        
        # Generate metadata
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "generator_version": "0.1.0",
            "confidence_score": avg_confidence,
            "banner_type": "multi-site",
            "sites_covered": sites,
            "site_count": len(sites),
            "multi_site_rule": True,
            "tested": False
        }
        
        # Create the multi-site rule
        rule = ConsentRule(
            site=combined_site,
            selectors=common_selectors,
            actions=common_actions,
            metadata=metadata
        )
        
        return rule
    
    def _find_common_selectors(self, banners: List[BannerInfo]) -> Dict[str, str]:
        """Find common selectors across multiple banners."""
        common_selectors = {}
        
        # Collect all selectors by type
        selector_groups = {
            'banner': [],
            'acceptButton': [],
            'rejectButton': [],
            'manageButton': [],
            'closeButton': [],
            'overlay': []
        }
        
        for banner in banners:
            # Banner container
            if banner.container_selector:
                selector_groups['banner'].append(banner.container_selector)
            
            # Buttons
            for button in banner.buttons:
                button_type = f"{button.button_type.value}Button"
                if button_type in selector_groups:
                    selector_groups[button_type].append(button.selector)
            
            # Overlays
            if banner.overlay_selectors:
                selector_groups['overlay'].extend(banner.overlay_selectors)
        
        # Find most common selectors
        for selector_type, selectors in selector_groups.items():
            if selectors:
                # Find the most common selector (simple approach)
                from collections import Counter
                counter = Counter(selectors)
                most_common = counter.most_common(1)[0]
                
                # If there's a clear winner (appears in >50% of sites), use it
                if most_common[1] > len(banners) * 0.5:
                    common_selectors[selector_type] = most_common[0]
                else:
                    # Otherwise, combine multiple selectors
                    unique_selectors = list(set(selectors))
                    if len(unique_selectors) <= 3:  # Keep it manageable
                        common_selectors[selector_type] = ', '.join(unique_selectors)
                    else:
                        # Use the most common ones
                        top_selectors = [s[0] for s in counter.most_common(3)]
                        common_selectors[selector_type] = ', '.join(top_selectors)
        
        return common_selectors
    
    def _find_common_actions(self, banners: List[BannerInfo]) -> List[str]:
        """Find common actions across multiple banners."""
        action_counts = {}
        
        # Generate actions for each banner
        for banner in banners:
            actions = self._generate_actions(banner)
            for action in actions:
                action_counts[action] = action_counts.get(action, 0) + 1
        
        # Include actions that appear in at least 50% of banners
        threshold = len(banners) * 0.5
        common_actions = [action for action, count in action_counts.items() if count >= threshold]
        
        # Ensure we have at least basic actions
        if not common_actions:
            common_actions = ["hideBanner", "clickRejectIfPossible"]
        
        return common_actions
    
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
