#!/usr/bin/env python3
"""
Test Westmount Medical Pharmacy cookie banner detection
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.collectors.web_scraper import WebScraper
from src.detectors.banner_detector import BannerDetector
from src.extractors.banner_extractor import BannerExtractor
from src.generators.rule_generator import RuleGenerator

def test_westmount_pharmacy():
    """Test cookie banner detection on Westmount Medical Pharmacy."""
    
    url = "https://www.westmountmedicalpharmacy.ca/"
    
    print(f"🔍 Testing Westmount Medical Pharmacy: {url}")
    print("=" * 60)
    
    try:
        # Initialize components
        scraper = WebScraper()
        detector = BannerDetector()
        extractor = BannerExtractor()
        generator = RuleGenerator()
        
        # Step 1: Collect page data
        print("1. Collecting page data...")
        page_data = scraper.collect_page(url)
        
        if not page_data:
            print("❌ Failed to collect page data")
            return
        
        print(f"   ✅ Page data collected: {len(page_data.html_content)} characters")
        
        # Step 2: Detect banner
        print("2. Detecting consent banner...")
        banner_info = detector.detect_banner(page_data)
        
        if not banner_info:
            print("   ❌ No banner detected")
            return
        
        print(f"   ✅ Banner detected!")
        print(f"      - Confidence: {banner_info.detection_confidence:.2f}")
        print(f"      - Container: {banner_info.container_selector}")
        print(f"      - Buttons: {len(banner_info.buttons)}")
        
        for i, button in enumerate(banner_info.buttons, 1):
            print(f"        Button {i}: {button.button_type.value} - '{button.text}'")
            print(f"        Selector: {button.selector}")
        
        # Step 3: Extract features
        print("3. Extracting banner features...")
        extracted_info = extractor.extract_banner_features(banner_info)
        
        if extracted_info:
            print(f"   ✅ Features extracted!")
            print(f"      - Banner Type: {extracted_info.banner_type}")
            print(f"      - Button Count: {len(extracted_info.buttons)}")
            print(f"      - Has Overlays: {extracted_info.overlay_selectors is not None}")
        
        # Step 4: Generate rule
        print("4. Generating Consent O Matic rule...")
        rule = generator.generate_rule(extracted_info if extracted_info else banner_info)
        
        if rule:
            print(f"   ✅ Rule generated!")
            print(f"      - Site: {rule.site}")
            print(f"      - Selectors: {len(rule.selectors)}")
            print(f"      - Actions: {len(rule.actions)}")
            
            # Show selectors
            print(f"      - Banner Selector: {rule.selectors.get('banner', 'N/A')}")
            print(f"      - Accept Button: {rule.selectors.get('acceptButton', 'N/A')}")
            if rule.selectors.get('manageButton'):
                print(f"      - Manage Button: {rule.selectors.get('manageButton')}")
            if rule.selectors.get('rejectButton'):
                print(f"      - Reject Button: {rule.selectors.get('rejectButton')}")
        
        # Step 5: Create Consent O Matic JSON
        print("5. Creating Consent O Matic JSON...")
        consent_o_matic_rule = create_consent_o_matic_json(rule, url)
        
        if consent_o_matic_rule:
            print("   ✅ Consent O Matic JSON created!")
            
            # Save the rule
            import json
            from datetime import datetime
            
            os.makedirs("data/consent_o_matic_rules", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/consent_o_matic_rules/westmount_medical_pharmacy_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(consent_o_matic_rule, f, indent=2, ensure_ascii=False)
            
            print(f"   📁 Saved to: {filename}")
            
            # Show how to use
            print(f"\n🎯 How to Use:")
            print(f"1. Copy the JSON content from: {filename}")
            print(f"2. Open Consent O Matic extension")
            print(f"3. Go to 'GDPR Consent Rules Editor'")
            print(f"4. Click 'From Pasted JSON'")
            print(f"5. Paste the JSON and click 'Load'")
            print(f"6. Click 'Save Custom Rule'")
            print(f"7. Test by visiting: {url}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def create_consent_o_matic_json(rule, url):
    """Create Consent O Matic compatible JSON rule."""
    
    if not rule:
        return None
    
    # Extract site name
    site_name = url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
    site_name_clean = "".join(word.capitalize() for word in site_name.replace(".", "").split("-"))
    
    # Create the rule structure
    consent_o_matic_rule = {
        "$schema": "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules.schema.json",
        site_name_clean: {
            "detectors": {
                "presentMatcher": {
                    "type": "css",
                    "target": {
                        "selector": rule.selectors.get('banner', '.cookie-banner')
                    }
                },
                "showingMatcher": {
                    "type": "css",
                    "target": {
                        "selector": rule.selectors.get('banner', '.cookie-banner')
                    }
                }
            },
            "methods": {
                "HIDE_CMP": {
                    "action": {
                        "type": "hide",
                        "target": {
                            "selector": rule.selectors.get('banner', '.cookie-banner')
                        }
                    }
                }
            }
        }
    }
    
    # Add accept button if available
    if rule.selectors.get('acceptButton'):
        consent_o_matic_rule[site_name_clean]["methods"]["DO_CONSENT"] = {
            "action": {
                "type": "click",
                "target": {
                    "selector": rule.selectors.get('acceptButton')
                }
            }
        }
        
        # Add save consent (usually same as accept)
        consent_o_matic_rule[site_name_clean]["methods"]["SAVE_CONSENT"] = {
            "action": {
                "type": "click",
                "target": {
                    "selector": rule.selectors.get('acceptButton')
                }
            }
        }
    
    # Add manage button if available
    if rule.selectors.get('manageButton'):
        consent_o_matic_rule[site_name_clean]["methods"]["OPEN_OPTIONS"] = {
            "action": {
                "type": "click",
                "target": {
                    "selector": rule.selectors.get('manageButton')
                }
            }
        }
    
    # Add reject button if available
    if rule.selectors.get('rejectButton'):
        consent_o_matic_rule[site_name_clean]["methods"]["DO_REJECT"] = {
            "action": {
                "type": "click",
                "target": {
                    "selector": rule.selectors.get('rejectButton')
                }
            }
        }
    
    return consent_o_matic_rule

if __name__ == "__main__":
    test_westmount_pharmacy()
