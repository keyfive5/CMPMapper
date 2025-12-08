#!/usr/bin/env python3
"""
Quick command-line test for CMP Mapper.
Usage: python quick_test.py <URL>
"""

import sys
import os
from datetime import datetime
sys.path.append('src')

from version import print_version_info
from src.collectors import WebScraper
from src.detectors import BannerDetector
from src.generators import RuleGenerator

def quick_test(url):
    """Quick test for a single URL."""
    print_version_info()
    print("=" * 70)
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    print(f"\n🚀 Quick Testing: {url}")
    print("⏳ This may take 10-30 seconds...")
    
    try:
        detector = BannerDetector()
        generator = RuleGenerator()
        
        with WebScraper(headless=True, timeout=30) as scraper:
            print("📥 Collecting page data...")
            page_data = scraper.collect_page(url, wait_for_banner=True)
            
            if not page_data.html_content:
                print("❌ Failed to collect page data")
                return False
            
            print(f"✅ Collected {len(page_data.html_content)} characters")
            
            print("🔍 Detecting consent banner...")
            banner_info = detector.detect_banner(page_data)
            
            if banner_info:
                print(f"\n🎉 SUCCESS! Banner detected:")
                print(f"   📋 Type: {banner_info.banner_type.value}")
                print(f"   🎯 Confidence: {banner_info.detection_confidence:.2f}")
                print(f"   📦 Container: {banner_info.container_selector}")
                print(f"   🔘 Buttons: {len(banner_info.buttons)}")
                
                # Generate rule
                rule = generator.generate_rule(banner_info)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"quick_test_{timestamp}.json"
                filepath = generator.save_rule(rule, filename)
                
                print(f"💾 Rule saved: {filepath}")
                return True
            else:
                print("\n❌ No banner detected")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python quick_test.py <URL>")
        print("Example: python quick_test.py margispharmacy.com")
        sys.exit(1)
    
    url = sys.argv[1]
    success = quick_test(url)
    sys.exit(0 if success else 1)
