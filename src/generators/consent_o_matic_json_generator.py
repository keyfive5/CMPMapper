"""
Consent O Matic JSON Generator
Creates proper JSON rules that work directly with Consent O Matic editor
"""

import json
from typing import Dict, List, Any
from src.models import BannerInfo, ConsentRule


class ConsentOMaticJSONGenerator:
    """Generates Consent O Matic compatible JSON rules."""
    
    def __init__(self):
        self.schema_url = "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules.schema.json"
    
    def generate_rule_json(self, banner_info: BannerInfo) -> Dict[str, Any]:
        """
        Generate a Consent O Matic JSON rule from banner info.
        
        Args:
            banner_info: Detected banner information
            
        Returns:
            Consent O Matic compatible JSON rule
        """
        # Extract site name for the rule key
        site_name = self._get_site_name(banner_info.site)
        
        # Create the rule structure
        rule = {
            "$schema": self.schema_url,
            site_name: {
                "detectors": self._create_detectors(banner_info),
                "methods": self._create_methods(banner_info)
            }
        }
        
        return rule
    
    def _get_site_name(self, site_url: str) -> str:
        """Extract a clean site name from URL."""
        # Remove protocol and get domain
        domain = site_url.replace("https://", "").replace("http://", "").replace("www.", "")
        # Remove path and get just the domain
        domain = domain.split("/")[0]
        # Convert to PascalCase for rule name
        parts = domain.split(".")
        if len(parts) > 1:
            return "".join(word.capitalize() for word in parts[0].split("-"))
        return domain.capitalize()
    
    def _create_detectors(self, banner_info: BannerInfo) -> Dict[str, Any]:
        """Create detector configuration."""
        return {
            "presentMatcher": {
                "type": "css",
                "target": {
                    "selector": banner_info.container_selector
                }
            },
            "showingMatcher": {
                "type": "css", 
                "target": {
                    "selector": banner_info.container_selector
                }
            }
        }
    
    def _create_methods(self, banner_info: BannerInfo) -> Dict[str, Any]:
        """Create method configurations."""
        methods = {}
        
        # HIDE_CMP - Hide the banner
        methods["HIDE_CMP"] = {
            "action": {
                "type": "hide",
                "target": {
                    "selector": banner_info.container_selector
                }
            }
        }
        
        # DO_CONSENT - Click accept button
        accept_buttons = [btn for btn in banner_info.buttons if btn.button_type.value == "accept"]
        if accept_buttons:
            # Use the first accept button's selector
            methods["DO_CONSENT"] = {
                "action": {
                    "type": "click",
                    "target": {
                        "selector": accept_buttons[0].selector
                    }
                }
            }
        
        # OPEN_OPTIONS - Click manage button (if available)
        manage_buttons = [btn for btn in banner_info.buttons if btn.button_type.value == "manage"]
        if manage_buttons:
            methods["OPEN_OPTIONS"] = {
                "action": {
                    "type": "click",
                    "target": {
                        "selector": manage_buttons[0].selector
                    }
                }
            }
        
        # SAVE_CONSENT - Usually same as DO_CONSENT for simple banners
        if "DO_CONSENT" in methods:
            methods["SAVE_CONSENT"] = methods["DO_CONSENT"].copy()
        
        return methods
    
    def save_rule_json(self, banner_info: BannerInfo, filename: str = None) -> str:
        """
        Generate and save a Consent O Matic JSON rule.
        
        Args:
            banner_info: Detected banner information
            filename: Optional custom filename
            
        Returns:
            Path to saved JSON file
        """
        import os
        from datetime import datetime
        
        # Generate the rule
        rule_json = self.generate_rule_json(banner_info)
        
        # Create filename if not provided
        if not filename:
            site_name = self._get_site_name(banner_info.site)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{site_name}_consent_o_matic_{timestamp}.json"
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Create directory if needed
        os.makedirs("data/consent_o_matic_rules", exist_ok=True)
        filepath = os.path.join("data/consent_o_matic_rules", filename)
        
        # Save the rule
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(rule_json, f, indent=2, ensure_ascii=False)
        
        return filepath


def test_json_generator():
    """Test the JSON generator with sample data."""
    from src.models import BannerInfo, BannerType, ConsentButton, ButtonType
    
    # Create sample banner info
    banner_info = BannerInfo(
        site="https://margispharmacy.com",
        banner_type=BannerType.MODAL,
        container_selector=".ideocookie-banner",
        buttons=[
            ConsentButton(
                text="Google",
                button_type=ButtonType.ACCEPT,
                selector="#ideocookie-selectall"
            ),
            ConsentButton(
                text="Facebook", 
                button_type=ButtonType.ACCEPT,
                selector="#ideocookie-selectall"
            )
        ],
        html_content="<div class='ideocookie-banner'>...</div>",
        detection_confidence=1.0
    )
    
    # Generate JSON
    generator = ConsentOMaticJSONGenerator()
    rule_json = generator.generate_rule_json(banner_info)
    
    print("Generated Consent O Matic JSON:")
    print(json.dumps(rule_json, indent=2))
    
    # Save to file
    filepath = generator.save_rule_json(banner_info)
    print(f"\nSaved to: {filepath}")


if __name__ == "__main__":
    test_json_generator()
