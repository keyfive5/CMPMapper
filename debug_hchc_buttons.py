#!/usr/bin/env python3
"""
Debug HCHC Family Health button detection issue
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.collectors.web_scraper import WebScraper
from src.detectors.banner_detector import BannerDetector
from src.generators.rule_generator import RuleGenerator

def debug_hchc_buttons():
    """Debug HCHC Family Health button detection."""
    
    url = 'https://hchcfamilyhealth.org/on-site-services.php'
    print(f"🔍 Debugging HCHC Family Health Button Detection")
    print(f"URL: {url}")
    print("=" * 60)
    
    try:
        scraper = WebScraper()
        detector = BannerDetector()
        generator = RuleGenerator()
        
        # Step 1: Collect page data
        print("1. Collecting page data...")
        page_data = scraper.collect_page(url)
        
        if not page_data or not page_data.html_content:
            print("   ❌ Failed to collect page data")
            return
        
        print(f"   ✅ Page data collected: {len(page_data.html_content)} characters")
        
        # Step 2: Detect banner
        print("2. Detecting banner...")
        banner_info = detector.detect_banner(page_data)
        
        if not banner_info:
            print("   ❌ No banner detected")
            return
        
        print("   ✅ Banner detected!")
        print(f"      Container: {banner_info.container_selector}")
        print(f"      Confidence: {banner_info.detection_confidence}")
        print(f"      Buttons: {len(banner_info.buttons)}")
        
        # Step 3: Analyze buttons
        print("\n3. Button Analysis:")
        for i, button in enumerate(banner_info.buttons, 1):
            print(f"   Button {i}:")
            print(f"      Type: {button.button_type.value}")
            print(f"      Text: '{button.text}'")
            print(f"      Selector: {button.selector}")
            
            # Check if this looks like the correct consent button
            if 'accept' in button.button_type.value.lower():
                if '.cookies-notification-button' in button.selector:
                    print(f"      ✅ This looks like the correct consent button!")
                elif 'p a' in button.selector:
                    print(f"      ⚠️  This might be a link instead of the consent button")
                else:
                    print(f"      ❓ Unknown selector pattern")
        
        # Step 4: Generate rule and check the DO_CONSENT selector
        print("\n4. Generated Rule Analysis:")
        rule = generator.generate_consent_o_matic_json(banner_info)
        
        if rule:
            site_key = [k for k in rule.keys() if k != '$schema'][0]
            site_rule = rule[site_key]
            
            # Find DO_CONSENT method
            for method in site_rule.get('methods', []):
                if method.get('name') == 'DO_CONSENT':
                    action = method.get('action', {})
                    if action:
                        selector = action.get('target', {}).get('selector', '')
                        print(f"   DO_CONSENT selector: {selector}")
                        
                        if selector == '.cookies-notification-button':
                            print("   ✅ Correct selector found!")
                        elif selector == 'p a':
                            print("   ❌ Wrong selector - this will click a link instead of the consent button")
                        else:
                            print(f"   ❓ Unknown selector: {selector}")
        
        # Step 5: Show the generated rule
        print("\n5. Generated Rule:")
        print(json.dumps(rule, indent=2))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_hchc_buttons()
