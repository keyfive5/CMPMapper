#!/usr/bin/env python3
"""
Debug Arkell Medical detection issue
"""

import requests
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.collectors.web_scraper import WebScraper
from src.detectors.banner_detector import BannerDetector
from src.generators.rule_generator import RuleGenerator

def debug_arkellmedical():
    """Debug why Arkell Medical is not detecting banner anymore."""
    
    url = 'https://www.arkellmedical.ca/'
    print(f"Debugging Arkell Medical Detection Issue")
    print(f"URL: {url}")
    print("=" * 60)
    
    try:
        scraper = WebScraper()
        detector = BannerDetector()
        
        # Step 1: Test with Selenium
        print("1. Testing with Selenium WebDriver...")
        page_data = scraper.collect_page(url)
        
        # Step 2: Check page data
        if page_data and page_data.html_content:
            print(f"   Page data collected: {len(page_data.html_content)} characters")
            
            # Check for bot detection
            if page_data.metadata.get('blocked'):
                print(f"   Bot protection detected: {page_data.metadata.get('error')}")
                print("   This might be why banner detection is failing!")
            
            # Manual content analysis
            html_lower = page_data.html_content.lower()
            cookie_count = html_lower.count('cookie')
            consent_count = html_lower.count('consent')
            banner_count = html_lower.count('banner')
            cky_count = html_lower.count('cky-')
            
            print(f"   Content analysis:")
            print(f"      'cookie' mentions: {cookie_count}")
            print(f"      'consent' mentions: {consent_count}")
            print(f"      'banner' mentions: {banner_count}")
            print(f"      'cky-' mentions: {cky_count}")
            
            # Step 3: Test banner detection
            print("\n2. Testing banner detection...")
            banner_info = detector.detect_banner(page_data)
            
            if banner_info:
                print("   Banner detected!")
                print(f"      Container: {banner_info.container_selector}")
                print(f"      Confidence: {banner_info.detection_confidence}")
                print(f"      Buttons: {len(banner_info.buttons)}")
                
                for i, button in enumerate(banner_info.buttons, 1):
                    print(f"        Button {i}: {button.text} ({button.selector})")
            else:
                print("   No banner detected")
                print("   This is the problem!")
                
                # Save HTML for manual inspection
                with open('arkellmedical_debug.html', 'w', encoding='utf-8') as f:
                    f.write(page_data.html_content)
                print(f"   Saved HTML to arkellmedical_debug.html for manual inspection")
                
                # Try manual detection
                print("\n3. Trying manual detection...")
                if cookie_count > 0 or consent_count > 0 or cky_count > 0:
                    print("   Content suggests cookie banner should be present")
                    print("   Banner detection algorithm might need adjustment")
                else:
                    print("   No cookie-related content found")
                    print("   Site might have changed or bot detection is active")
        else:
            print("   Failed to collect page data")
            print("   This is likely a bot detection issue")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_arkellmedical()
