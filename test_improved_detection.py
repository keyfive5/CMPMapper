#!/usr/bin/env python3
"""
Test improved cookie banner detection
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.collectors.web_scraper import WebScraper
from src.detectors.banner_detector import BannerDetector
from src.generators.rule_generator import RuleGenerator

def test_improved_detection():
    """Test improved cookie banner detection."""
    
    print(f"🔍 Testing Improved Cookie Banner Detection")
    print("=" * 60)
    
    # Test URLs
    test_urls = [
        'https://hchcfamilyhealth.org/on-site-services.php',  # Known working
        'https://www.walmart.ca/en/cp/digital-pharmacy/6000206038183',  # Walmart
        'https://www.margispharmacy.com/',  # Known working
        'https://midtowncompoundingpharmacy.ca/',  # Known working
        'https://beyondrx.ca/'  # Known working
    ]
    
    scraper = WebScraper()
    detector = BannerDetector()
    generator = RuleGenerator()
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}. Testing: {url}")
        print("-" * 40)
        
        try:
            # Collect page data
            page_data = scraper.collect_page(url)
            
            if not page_data or not page_data.html_content:
                print("   ❌ Failed to collect page data")
                continue
            
            print(f"   ✅ Page data collected: {len(page_data.html_content)} characters")
            
            # Check for bot protection
            html_lower = page_data.html_content.lower()
            if 'robot' in html_lower or 'captcha' in html_lower or 'verification' in html_lower:
                print("   ⚠️  Bot protection page detected")
                continue
            
            # Detect banner
            banner_info = detector.detect_banner(page_data)
            
            if banner_info:
                print("   ✅ Banner detected!")
                print(f"      Container: {banner_info.container_selector}")
                print(f"      Confidence: {banner_info.detection_confidence:.2f}")
                print(f"      Buttons: {len(banner_info.buttons)}")
                
                for j, button in enumerate(banner_info.buttons, 1):
                    print(f"        Button {j}: {button.button_type.value} - '{button.text}'")
                
                # Generate rule
                rule = generator.generate_consent_o_matic_json(banner_info)
                if rule:
                    print("   ✅ Consent O Matic rule generated!")
                    
                    # Save rule
                    site_name = url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
                    filename = f"data/consent_o_matic_rules/{site_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    os.makedirs(os.path.dirname(filename), exist_ok=True)
                    
                    import json
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(rule, f, indent=2, ensure_ascii=False)
                    
                    print(f"   💾 Rule saved to: {filename}")
                else:
                    print("   ❌ Failed to generate rule")
            else:
                print("   ❌ No banner detected")
                
                # Show some analysis
                cookie_count = html_lower.count('cookie')
                consent_count = html_lower.count('consent')
                privacy_count = html_lower.count('privacy')
                
                print(f"      Cookie mentions: {cookie_count}")
                print(f"      Consent mentions: {consent_count}")
                print(f"      Privacy mentions: {privacy_count}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   - Tested {len(test_urls)} URLs")
    print(f"   - Improved detection patterns applied")
    print(f"   - Check results above for detection success")

if __name__ == "__main__":
    test_improved_detection()
