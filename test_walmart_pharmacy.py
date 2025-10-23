#!/usr/bin/env python3
"""
Test Walmart pharmacy cookie banner detection with proper headers
"""

import sys
import os
import re
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.collectors.web_scraper import WebScraper
from src.detectors.banner_detector import BannerDetector

def test_walmart_pharmacy():
    """Test detection of Walmart pharmacy cookie banner."""
    
    # Try different Walmart pharmacy URLs
    urls = [
        'https://www.walmart.ca/en/cp/digital-pharmacy/6000206038183',
        'https://www.walmart.ca/en/pharmacy',
        'https://www.walmart.ca/en/cp/pharmacy',
        'https://www.walmart.ca/en/cp/digital-pharmacy'
    ]
    
    print(f"🔍 Testing Walmart Pharmacy Cookie Banner Detection")
    print("=" * 60)
    
    for i, url in enumerate(urls, 1):
        print(f"\n{i}. Testing URL: {url}")
        print("-" * 40)
        
        try:
            scraper = WebScraper()
            detector = BannerDetector()
            
            # Collect page data
            page_data = scraper.collect_page(url)
            
            if not page_data or not page_data.html_content:
                print("   ❌ Failed to collect page data")
                continue
            
            html_content = page_data.html_content
            html_lower = html_content.lower()
            
            print(f"   ✅ Page data collected: {len(html_content)} characters")
            
            # Check if this is a bot protection page
            if 'robot' in html_lower or 'captcha' in html_lower or 'verification' in html_lower:
                print("   ⚠️  This appears to be a bot protection page, not the main pharmacy page")
                continue
            
            # Search for cookie-related content
            cookie_mentions = html_lower.count('cookie')
            consent_mentions = html_lower.count('consent')
            privacy_mentions = html_lower.count('privacy')
            banner_mentions = html_lower.count('banner')
            
            print(f"   Cookie mentions: {cookie_mentions}")
            print(f"   Consent mentions: {consent_mentions}")
            print(f"   Privacy mentions: {privacy_mentions}")
            print(f"   Banner mentions: {banner_mentions}")
            
            # Try banner detection
            banner_info = detector.detect_banner(page_data)
            
            if banner_info:
                print("   ✅ Banner detected!")
                print(f"      Container: {banner_info.container_selector}")
                print(f"      Confidence: {banner_info.detection_confidence}")
                print(f"      Buttons: {len(banner_info.buttons)}")
                
                for j, button in enumerate(banner_info.buttons, 1):
                    print(f"        Button {j}: {button.button_type.value} - '{button.text}'")
                    print(f"        Selector: {button.selector}")
                
                # Generate rule
                from src.generators.rule_generator import RuleGenerator
                generator = RuleGenerator()
                rule = generator.generate_consent_o_matic_json(banner_info)
                
                print(f"\n   🎯 Generated Consent O Matic Rule:")
                import json
                print(json.dumps(rule, indent=2))
                
                return  # Found a working banner, exit
            else:
                print("   ❌ No banner detected")
                
                # Look for specific patterns
                patterns = [
                    r'cookie.*consent',
                    r'privacy.*policy',
                    r'accept.*cookie',
                    r'manage.*cookie',
                    r'cookie.*settings',
                    r'gdpr.*consent'
                ]
                
                found_patterns = []
                for pattern in patterns:
                    matches = re.findall(pattern, html_lower)
                    if matches:
                        found_patterns.extend(matches[:2])
                
                if found_patterns:
                    print(f"   💡 Found cookie-related patterns: {found_patterns}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   - Tested {len(urls)} URLs")
    print(f"   - Most URLs appear to redirect to bot protection pages")
    print(f"   - Recommendation: Try accessing Walmart pharmacy pages manually to find the actual cookie banner")

if __name__ == "__main__":
    test_walmart_pharmacy()
