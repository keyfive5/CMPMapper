#!/usr/bin/env python3
"""
Test Walmart cookie banner detection
"""

import sys
import os
import re
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.collectors.web_scraper import WebScraper
from src.detectors.banner_detector import BannerDetector

def test_walmart_detection():
    """Test detection of Walmart's cookie banner."""
    
    url = 'https://www.walmart.ca/en/cp/digital-pharmacy/6000206038183'
    print(f"🔍 Testing Walmart Cookie Banner Detection")
    print(f"URL: {url}")
    print("=" * 60)
    
    try:
        scraper = WebScraper()
        detector = BannerDetector()
        
        # Step 1: Collect page data
        print("1. Collecting page data...")
        page_data = scraper.collect_page(url)
        
        if not page_data or not page_data.html_content:
            print("   ❌ Failed to collect page data")
            return
        
        print(f"   ✅ Page data collected: {len(page_data.html_content)} characters")
        
        # Step 2: Search for cookie-related content
        print("\n2. Analyzing HTML for cookie-related content...")
        html_lower = page_data.html_content.lower()
        
        # Count mentions
        cookie_mentions = html_lower.count('cookie')
        consent_mentions = html_lower.count('consent')
        privacy_mentions = html_lower.count('privacy')
        banner_mentions = html_lower.count('banner')
        
        print(f"   Cookie mentions: {cookie_mentions}")
        print(f"   Consent mentions: {consent_mentions}")
        print(f"   Privacy mentions: {privacy_mentions}")
        print(f"   Banner mentions: {banner_mentions}")
        
        # Step 3: Search for specific patterns
        print("\n3. Searching for cookie banner patterns...")
        patterns = [
            r'cookie.*banner',
            r'consent.*banner', 
            r'privacy.*notice',
            r'cookie.*notice',
            r'cookie.*policy',
            r'accept.*cookie',
            r'manage.*cookie',
            r'gdpr.*consent',
            r'cookie.*consent'
        ]
        
        found_patterns = []
        for pattern in patterns:
            matches = re.findall(pattern, html_lower)
            if matches:
                print(f"   ✅ Found pattern '{pattern}': {len(matches)} matches")
                found_patterns.extend(matches[:3])  # Show first 3 matches
        
        # Step 4: Look for specific CSS classes or IDs
        print("\n4. Searching for cookie-related CSS selectors...")
        css_patterns = [
            r'class="[^"]*cookie[^"]*"',
            r'id="[^"]*cookie[^"]*"',
            r'class="[^"]*consent[^"]*"',
            r'id="[^"]*consent[^"]*"',
            r'class="[^"]*privacy[^"]*"',
            r'id="[^"]*privacy[^"]*"',
            r'class="[^"]*banner[^"]*"',
            r'id="[^"]*banner[^"]*"'
        ]
        
        found_selectors = []
        for pattern in css_patterns:
            matches = re.findall(pattern, html_lower)
            if matches:
                print(f"   ✅ Found CSS selector pattern: {matches[0]}")
                found_selectors.extend(matches[:2])
        
        # Step 5: Try current detection
        print("\n5. Testing current banner detection...")
        banner_info = detector.detect_banner(page_data)
        
        if banner_info:
            print("   ✅ Banner detected with current detector!")
            print(f"      Container: {banner_info.container_selector}")
            print(f"      Confidence: {banner_info.detection_confidence}")
            print(f"      Buttons: {len(banner_info.buttons)}")
            
            for i, button in enumerate(banner_info.buttons, 1):
                print(f"        Button {i}: {button.button_type.value} - '{button.text}'")
                print(f"        Selector: {button.selector}")
        else:
            print("   ❌ No banner detected with current detector")
            
            # Step 6: Manual search for potential banner elements
            print("\n6. Manual search for potential banner elements...")
            
            # Look for div elements that might contain cookie banners
            div_patterns = [
                r'<div[^>]*class="[^"]*cookie[^"]*"[^>]*>.*?</div>',
                r'<div[^>]*class="[^"]*consent[^"]*"[^>]*>.*?</div>',
                r'<div[^>]*class="[^"]*privacy[^"]*"[^>]*>.*?</div>',
                r'<div[^>]*class="[^"]*banner[^"]*"[^>]*>.*?</div>'
            ]
            
            for pattern in div_patterns:
                matches = re.findall(pattern, html_lower, re.DOTALL)
                if matches:
                    print(f"   ✅ Found potential banner div: {matches[0][:100]}...")
            
            # Look for button elements
            button_patterns = [
                r'<button[^>]*>.*?(?:accept|consent|cookie).*?</button>',
                r'<a[^>]*>.*?(?:accept|consent|cookie).*?</a>'
            ]
            
            for pattern in button_patterns:
                matches = re.findall(pattern, html_lower, re.DOTALL)
                if matches:
                    print(f"   ✅ Found potential consent button: {matches[0][:100]}...")
        
        print(f"\n📊 Analysis Summary:")
        print(f"   - Total HTML size: {len(page_data.html_content)} characters")
        print(f"   - Cookie mentions: {cookie_mentions}")
        print(f"   - Found patterns: {len(found_patterns)}")
        print(f"   - Found selectors: {len(found_selectors)}")
        print(f"   - Banner detected: {'Yes' if banner_info else 'No'}")
        
        if not banner_info and (cookie_mentions > 0 or consent_mentions > 0):
            print(f"\n💡 Recommendation: Update banner detector to handle Walmart's cookie implementation")
            print(f"   The page clearly contains cookie-related content but wasn't detected.")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_walmart_detection()
