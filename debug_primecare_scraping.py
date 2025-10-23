#!/usr/bin/env python3
"""
Debug Prime Care Pharmacy scraping issue
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.collectors.web_scraper import WebScraper
from src.detectors.banner_detector import BannerDetector

def debug_primecare_scraping():
    """Debug Prime Care Pharmacy scraping issue."""
    
    url = 'https://primecarepharmacy.ca/'
    print(f"🔍 Debugging Prime Care Pharmacy Scraping")
    print(f"URL: {url}")
    print("=" * 60)
    
    try:
        scraper = WebScraper()
        detector = BannerDetector()
        
        # Step 1: Test with Selenium
        print("1. Testing with Selenium WebDriver...")
        page_data = scraper.collect_page(url)
        
        if page_data and page_data.html_content:
            print(f"   ✅ Page data collected: {len(page_data.html_content)} characters")
            
            # Analyze content manually
            html_lower = page_data.html_content.lower()
            cookie_count = html_lower.count('cookie')
            consent_count = html_lower.count('consent')
            privacy_count = html_lower.count('privacy')
            banner_count = html_lower.count('banner')
            
            print(f"   📊 Content analysis:")
            print(f"      'cookie' mentions: {cookie_count}")
            print(f"      'consent' mentions: {consent_count}")
            print(f"      'privacy' mentions: {privacy_count}")
            print(f"      'banner' mentions: {banner_count}")
            
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
            else:
                print("   ❌ No banner detected")
                
                # Save HTML for manual inspection
                with open('primecare_debug.html', 'w', encoding='utf-8') as f:
                    f.write(page_data.html_content)
                print(f"   💾 Saved HTML to primecare_debug.html for manual inspection")
                
                # Look for cookie-related content
                html_lower = page_data.html_content.lower()
                cookie_count = html_lower.count('cookie')
                consent_count = html_lower.count('consent')
                privacy_count = html_lower.count('privacy')
                
                print(f"   📊 Content analysis:")
                print(f"      'cookie' mentions: {cookie_count}")
                print(f"      'consent' mentions: {consent_count}")
                print(f"      'privacy' mentions: {privacy_count}")
                
                if cookie_count > 0 or consent_count > 0 or privacy_count > 0:
                    print("   💡 Cookie-related content found, but banner detection failed")
                    print("   💡 This might be a detection pattern issue")
                else:
                    print("   💡 No cookie-related content found")
                    print("   💡 This might be a scraping issue or the site has no cookie banner")
        else:
            print("   ❌ Failed to collect page data")
            print("   💡 This indicates a scraping/blocking issue")
            
            # Test if the scraper is working at all
            print("\n3. Testing scraper with a known working site...")
            test_url = 'https://hchcfamilyhealth.org/on-site-services.php'
            test_data = scraper.collect_page(test_url)
            
            if test_data and test_data.html_content:
                print(f"   ✅ Scraper works (test site: {len(test_data.html_content)} chars)")
                print("   💡 Issue is specific to Prime Care Pharmacy")
            else:
                print("   ❌ Scraper not working at all")
                print("   💡 This indicates a general scraping issue")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_primecare_scraping()
