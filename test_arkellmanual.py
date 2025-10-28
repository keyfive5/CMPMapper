#!/usr/bin/env python3
"""
Manual test for Arkell Medical banner detection
"""

import requests
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.collectors.web_scraper import WebScraper
from src.detectors.banner_detector import BannerDetector

def test_arkell_manual():
    """Manual test for Arkell Medical banner detection."""
    
    url = 'https://www.arkellmedical.ca/'
    print(f"Manual Test for Arkell Medical Banner Detection")
    print(f"URL: {url}")
    print("=" * 60)
    
    try:
        scraper = WebScraper()
        detector = BannerDetector()
        
        # Step 1: Collect page data
        print("1. Collecting page data...")
        page_data = scraper.collect_page(url)
        
        if page_data and page_data.html_content:
            print(f"   Page data collected: {len(page_data.html_content)} characters")
            
            # Step 2: Manual banner detection
            print("\n2. Manual banner detection...")
            
            # Look for CookieYes specific patterns
            html_content = page_data.html_content
            
            # Check for CookieYes container
            cky_modal_found = '.cky-modal' in html_content
            cky_consent_found = '.cky-consent-container' in html_content
            cky_notice_found = '.cky-notice' in html_content
            
            print(f"   .cky-modal found: {cky_modal_found}")
            print(f"   .cky-consent-container found: {cky_consent_found}")
            print(f"   .cky-notice found: {cky_notice_found}")
            
            # Check for buttons
            accept_button_found = 'cky-btn-accept' in html_content
            reject_button_found = 'cky-btn-reject' in html_content
            settings_button_found = 'cky-btn-customize' in html_content
            
            print(f"   Accept button found: {accept_button_found}")
            print(f"   Reject button found: {reject_button_found}")
            print(f"   Settings button found: {settings_button_found}")
            
            # Step 3: Test our detector
            print("\n3. Testing our banner detector...")
            banner_info = detector.detect_banner(page_data)
            
            if banner_info:
                print("   Banner detected by our algorithm!")
                print(f"      Container: {banner_info.container_selector}")
                print(f"      Confidence: {banner_info.detection_confidence}")
                print(f"      Buttons: {len(banner_info.buttons)}")
            else:
                print("   No banner detected by our algorithm")
                print("   This is the problem - our detection is failing")
                
                # Let's try to debug the detection process
                print("\n4. Debugging detection process...")
                
                # Check if our patterns are working
                
                # Look for specific patterns manually
                patterns_to_check = [
                    '[id*="cookie"]',
                    '[class*="cookie"]', 
                    '[class*="consent"]',
                    '.cky-modal',
                    '.cky-consent-container',
                    '#cky-modal',
                    '.cookie-banner',
                    '.consent-banner'
                ]
                
                for pattern in patterns_to_check:
                    if pattern in html_content:
                        print(f"   Pattern '{pattern}' found in HTML")
                    else:
                        print(f"   Pattern '{pattern}' NOT found in HTML")
        else:
            print("   Failed to collect page data")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_arkell_manual()
