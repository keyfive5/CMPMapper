#!/usr/bin/env python3
"""
Direct test for Arkell Medical banner detection
"""

import requests
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.collectors.web_scraper import WebScraper
from src.detectors.banner_detector import BannerDetector
from bs4 import BeautifulSoup

def test_arkell_direct():
    """Direct test for Arkell Medical banner detection."""
    
    url = 'https://www.arkellmedical.ca/'
    print(f"Direct Test for Arkell Medical Banner Detection")
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
            
            # Step 2: Direct BeautifulSoup test
            print("\n2. Direct BeautifulSoup test...")
            soup = BeautifulSoup(page_data.html_content, 'html.parser')
            
            # Test our new selectors
            cky_containers = soup.select("[class*='cky-']")
            print(f"   Found {len(cky_containers)} elements with cky- classes")
            
            # Test specific CookieYes selectors
            cky_modal = soup.select(".cky-modal")
            cky_consent = soup.select(".cky-consent-container")
            cky_notice = soup.select(".cky-notice")
            
            print(f"   .cky-modal: {len(cky_modal)} elements")
            print(f"   .cky-consent-container: {len(cky_consent)} elements")
            print(f"   .cky-notice: {len(cky_notice)} elements")
            
            if cky_consent:
                print(f"   First cky-consent-container: {cky_consent[0].get('class', [])}")
            
            # Step 3: Test our detector's _find_all_banner_containers method
            print("\n3. Testing detector's _find_all_banner_containers...")
            containers = detector._find_all_banner_containers(soup)
            print(f"   Found {len(containers)} banner containers")
            
            for i, container in enumerate(containers, 1):
                classes = container.get('class', [])
                container_id = container.get('id', '')
                print(f"      Container {i}: classes={classes}, id={container_id}")
            
            # Step 4: Test banner detection
            print("\n4. Testing banner detection...")
            banner_info = detector.detect_banner(page_data)
            
            if banner_info:
                print("   Banner detected!")
                print(f"      Container: {banner_info.container_selector}")
                print(f"      Confidence: {banner_info.detection_confidence}")
                print(f"      Buttons: {len(banner_info.buttons)}")
            else:
                print("   No banner detected")
                
                # Let's try to manually create a banner info
                print("\n5. Manual banner creation...")
                if cky_consent:
                    # Create a manual banner info
                    from src.models import BannerInfo, BannerType
                    
                    # Find buttons in the consent container
                    buttons = cky_consent[0].find_all(['button', 'a'])
                    print(f"   Found {len(buttons)} buttons in consent container")
                    
                    for i, btn in enumerate(buttons, 1):
                        btn_text = btn.get_text().strip()
                        btn_classes = btn.get('class', [])
                        print(f"      Button {i}: '{btn_text}' classes={btn_classes}")
        else:
            print("   Failed to collect page data")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_arkell_direct()
