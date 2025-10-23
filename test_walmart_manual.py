#!/usr/bin/env python3
"""
Test Walmart with manual approach to bypass bot detection
"""

import sys
import os
import time
import random
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.collectors.web_scraper import WebScraper
from src.detectors.banner_detector import BannerDetector

def test_walmart_manual():
    """Test Walmart with manual approach."""
    
    print(f"🔍 Testing Walmart with Manual Approach")
    print("=" * 60)
    
    # Try different approaches
    approaches = [
        {
            'name': 'Standard Approach',
            'headless': True,
            'timeout': 30,
            'wait_time': 0
        },
        {
            'name': 'Non-Headless Approach',
            'headless': False,
            'timeout': 30,
            'wait_time': 5
        },
        {
            'name': 'Delayed Approach',
            'headless': True,
            'timeout': 60,
            'wait_time': 10
        }
    ]
    
    url = 'https://www.walmart.ca/en/cp/digital-pharmacy/6000206038183'
    
    for i, approach in enumerate(approaches, 1):
        print(f"\n{i}. {approach['name']}")
        print("-" * 30)
        
        try:
            # Create scraper with different settings
            scraper = WebScraper(headless=approach['headless'], timeout=approach['timeout'])
            detector = BannerDetector()
            
            print(f"   Collecting page data...")
            page_data = scraper.collect_page(url)
            
            if not page_data or not page_data.html_content:
                print("   ❌ Failed to collect page data")
                scraper.close()
                continue
            
            print(f"   ✅ Page data collected: {len(page_data.html_content)} characters")
            
            # Wait a bit
            if approach['wait_time'] > 0:
                print(f"   Waiting {approach['wait_time']} seconds...")
                time.sleep(approach['wait_time'])
            
            # Check for bot protection
            html_lower = page_data.html_content.lower()
            is_bot_protection = any(word in html_lower for word in ['robot', 'captcha', 'verification', 'bot protection'])
            
            if is_bot_protection:
                print("   ⚠️  Bot protection page detected")
                
                # Try to find any cookie-related content anyway
                cookie_count = html_lower.count('cookie')
                consent_count = html_lower.count('consent')
                privacy_count = html_lower.count('privacy')
                
                print(f"      Cookie mentions: {cookie_count}")
                print(f"      Consent mentions: {consent_count}")
                print(f"      Privacy mentions: {privacy_count}")
                
                if cookie_count > 0:
                    print("      💡 Cookie-related content found despite bot protection")
            else:
                print("   ✅ No bot protection detected!")
                
                # Try to detect banner
                banner_info = detector.detect_banner(page_data)
                
                if banner_info:
                    print("   ✅ Banner detected!")
                    print(f"      Container: {banner_info.container_selector}")
                    print(f"      Confidence: {banner_info.detection_confidence:.2f}")
                    print(f"      Buttons: {len(banner_info.buttons)}")
                    
                    for j, button in enumerate(banner_info.buttons, 1):
                        print(f"        Button {j}: {button.button_type.value} - '{button.text}'")
                    
                    return banner_info  # Success!
                else:
                    print("   ❌ No banner detected")
            
            scraper.close()
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   - Tested {len(approaches)} different approaches")
    print(f"   - Walmart appears to have strong bot detection")
    print(f"   - Recommendation: Try accessing Walmart manually to find the actual cookie banner")
    
    return None

if __name__ == "__main__":
    test_walmart_manual()
