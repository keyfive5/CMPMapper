#!/usr/bin/env python3
"""
Test Fauquier Strickland site to identify and fix JSON generation issues
"""

import requests
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.collectors.web_scraper import WebScraper
from src.detectors.banner_detector import BannerDetector
from src.generators.rule_generator import RuleGenerator

def test_fauquierstrickland():
    """Test Fauquier Strickland site to identify JSON generation issues."""
    
    url = 'https://www.fauquierstrickland.com/page/contact'
    print(f"Testing Fauquier Strickland JSON Generation Issues")
    print(f"URL: {url}")
    print("=" * 70)
    
    try:
        scraper = WebScraper()
        detector = BannerDetector()
        generator = RuleGenerator()
        
        # Step 1: Test with Selenium
        print("1. Testing with Selenium WebDriver...")
        page_data = scraper.collect_page(url)
        
        if page_data and page_data.html_content:
            print(f"   Page data collected: {len(page_data.html_content)} characters")
            
            # Step 2: Test banner detection
            print("\n2. Testing banner detection...")
            banner_info = detector.detect_banner(page_data)
            
            if banner_info:
                print("   Banner detected!")
                print(f"      Container: {banner_info.container_selector}")
                print(f"      Confidence: {banner_info.detection_confidence}")
                print(f"      Buttons: {len(banner_info.buttons)}")
                
                for i, button in enumerate(banner_info.buttons, 1):
                    print(f"        Button {i}: {button.text} ({button.selector})")
                
                # Step 3: Test rule generation
                print("\n3. Testing rule generation...")
                try:
                    rule = generator.generate_consent_o_matic_json(banner_info)
                    print("   Rule generated successfully")
                    
                    # Analyze the generated rule for issues
                    print("\n4. Analyzing generated rule for issues...")
                    site_key = next((key for key in rule.keys() if key != '$schema'), None)
                    if site_key:
                        site_rule = rule[site_key]
                        
                        # Check detectors
                        detectors = site_rule.get('detectors', [])
                        if detectors:
                            print(f"   📋 Detectors: {len(detectors)} found")
                            for i, detector in enumerate(detectors, 1):
                                present_matcher = detector.get('presentMatcher', [])
                                showing_matcher = detector.get('showingMatcher', [])
                                print(f"      Detector {i}:")
                                print(f"        Present Matcher: {len(present_matcher)} matcher(s)")
                                print(f"        Showing Matcher: {len(showing_matcher)} matcher(s)")
                                
                                # Check if selectors are too specific
                                for matcher in present_matcher:
                                    selector = matcher.get('target', {}).get('selector', '')
                                    if len(selector) > 100:
                                        print(f"        ⚠️  Present selector too long: {len(selector)} chars")
                                    if '.ng-tns-c' in selector:
                                        print(f"        ⚠️  Present selector has Angular class: {selector[:50]}...")
                        
                        # Check methods
                        methods = site_rule.get('methods', [])
                        print(f"   📋 Methods: {len(methods)} found")
                        for i, method in enumerate(methods, 1):
                            method_name = method.get('name', 'Unknown')
                            action = method.get('action', {})
                            if action:
                                selector = action.get('target', {}).get('selector', '')
                                print(f"      Method {i}: {method_name}")
                                print(f"        Selector: {selector[:100]}...")
                                
                                # Check for problematic selectors
                                if len(selector) > 100:
                                    print(f"        ⚠️  Selector too long: {len(selector)} chars")
                                if '.ng-tns-c' in selector:
                                    print(f"        ⚠️  Selector has Angular class: {selector[:50]}...")
                                if '.mat-mdc-button' in selector:
                                    print(f"        ⚠️  Selector has Material Design class: {selector[:50]}...")
                            else:
                                print(f"      Method {i}: {method_name} (no action)")
                        
                        # Generate improved rule
                        print("\n5. Generating improved rule...")
                        improved_rule = generate_improved_rule(banner_info)
                        if improved_rule:
                            print("   Improved rule generated")
                            print("\n6. Improved Rule:")
                            print(json.dumps(improved_rule, indent=2, ensure_ascii=False))
                        
                except Exception as e:
                    print(f"   Rule generation failed: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("   No banner detected")
                
                # Save HTML for manual inspection
                with open('fauquierstrickland_debug.html', 'w', encoding='utf-8') as f:
                    f.write(page_data.html_content)
                print(f"   Saved HTML to fauquierstrickland_debug.html for manual inspection")
        else:
            print("   Failed to collect page data")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def generate_improved_rule(banner_info):
    """Generate an improved rule with better selectors."""
    
    # Extract site name for the rule key
    site_name = banner_info.site.replace("https://", "").replace("http://", "").replace("www.", "")
    site_name = site_name.split("/")[0]
    
    # Create improved rule structure
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
    
    # Add DO_CONSENT method with improved selector
    accept_buttons = [btn for btn in banner_info.buttons if btn.button_type.value == "accept"]
    if accept_buttons:
        # Try to find a simpler selector
        best_button = accept_buttons[0]
        improved_selector = improve_selector(best_button.selector)
        
        consent_method = {
            "action": {
                "type": "click",
                "target": {
                    "selector": improved_selector
                }
            },
            "name": "DO_CONSENT"
        }
        rule[f"{site_name} CMP"]["methods"].insert(2, consent_method)
    
    return rule

def improve_selector(selector):
    """Improve a selector by removing overly specific parts."""
    
    # If selector is too long or has Angular classes, try to simplify
    if len(selector) > 100 or '.ng-tns-c' in selector or '.mat-mdc-button' in selector:
        # Try to extract a simpler selector
        parts = selector.split(', ')
        if parts:
            # Take the first part and try to simplify it
            first_part = parts[0].strip()
            
            # Remove Angular-specific classes
            if '.ng-tns-c' in first_part:
                # Try to find a more generic class
                classes = first_part.split('.')
                simple_classes = [cls for cls in classes if not cls.startswith('ng-tns-c') and not cls.startswith('mat-')]
                if simple_classes:
                    return '.' + '.'.join(simple_classes[1:])  # Skip the first empty element
            
            # If it's still too long, try to find the most specific but reasonable selector
            if len(first_part) > 50:
                # Look for button-related classes
                if 'button' in first_part.lower():
                    return '.mdc-button'  # Use a more generic Material Design button class
                elif 'btn' in first_part.lower():
                    return '.btn'  # Use a generic button class
                else:
                    return first_part[:50] + '...'  # Truncate if too long
            
            return first_part
    
    return selector

if __name__ == "__main__":
    test_fauquierstrickland()
