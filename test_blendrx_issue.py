#!/usr/bin/env python3
"""
Test BlendRx site to identify the navigation issue
"""

import requests
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.collectors.web_scraper import WebScraper
from src.detectors.banner_detector import BannerDetector
from src.generators.rule_generator import RuleGenerator

def test_blendrx_issue():
    """Test BlendRx site to identify the navigation issue."""
    
    url = 'https://blendrx.ca/'
    print(f"🔍 Testing BlendRx Navigation Issue")
    print(f"URL: {url}")
    print("=" * 60)
    
    try:
        scraper = WebScraper()
        detector = BannerDetector()
        generator = RuleGenerator()
        
        # Step 1: Test with Selenium
        print("1. Testing with Selenium WebDriver...")
        page_data = scraper.collect_page(url)
        
        if page_data and page_data.html_content:
            print(f"   ✅ Page data collected: {len(page_data.html_content)} characters")
            
            # Analyze content for navigation issues
            html_lower = page_data.html_content.lower()
            about_us_count = html_lower.count('about us')
            navigation_count = html_lower.count('navigation')
            menu_count = html_lower.count('menu')
            
            print(f"   📊 Content analysis:")
            print(f"      'about us' mentions: {about_us_count}")
            print(f"      'navigation' mentions: {navigation_count}")
            print(f"      'menu' mentions: {menu_count}")
            
            # Step 2: Test banner detection
            print("\n2. Testing banner detection...")
            banner_info = detector.detect_banner(page_data)
            
            if banner_info:
                print("   ✅ Banner detected!")
                print(f"      Container: {banner_info.container_selector}")
                print(f"      Confidence: {banner_info.detection_confidence}")
                print(f"      Buttons: {len(banner_info.buttons)}")
                
                for i, button in enumerate(banner_info.buttons, 1):
                    print(f"        Button {i}: {button.text} ({button.selector})")
                
                # Step 3: Test rule generation
                print("\n3. Testing rule generation...")
                try:
                    rule = generator.generate_consent_o_matic_json(banner_info)
                    print("   ✅ Rule generated successfully")
                    
                    # Check if the rule might be causing navigation issues
                    site_key = next((key for key in rule.keys() if key != '$schema'), None)
                    if site_key:
                        site_rule = rule[site_key]
                        methods = site_rule.get('methods', [])
                        
                        print(f"   📋 Generated methods:")
                        for method in methods:
                            if method.get('name') == 'DO_CONSENT':
                                action = method.get('action', {})
                                if action:
                                    selector = action.get('target', {}).get('selector', '')
                                    print(f"      DO_CONSENT: {selector}")
                                    
                                    # Check if selector might interfere with navigation
                                    if 'about' in selector.lower() or 'nav' in selector.lower():
                                        print("      ⚠️  WARNING: Selector might interfere with navigation!")
                                    elif 'button' in selector.lower() or 'accept' in selector.lower():
                                        print("      ✅ Selector looks safe for navigation")
                                    
                except Exception as e:
                    print(f"   ❌ Rule generation failed: {e}")
            else:
                print("   ❌ No banner detected")
                
                # Save HTML for manual inspection
                with open('blendrx_debug.html', 'w', encoding='utf-8') as f:
                    f.write(page_data.html_content)
                print(f"   💾 Saved HTML to blendrx_debug.html for manual inspection")
        else:
            print("   ❌ Failed to collect page data")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_blendrx_issue()
