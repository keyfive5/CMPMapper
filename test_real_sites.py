#!/usr/bin/env python3
"""
Test CMP Mapper with real pharmacy websites.
"""

import sys
import os
sys.path.append('src')

from src.collectors import WebScraper, BannerCollector
from src.detectors import BannerDetector
from src.generators import RuleGenerator
from src.models import PageData, BannerInfo

def test_pharmacy_sites():
    """Test CMP Mapper with real pharmacy websites."""
    
    # Real pharmacy sites to test
    pharmacy_urls = [
        "https://www.margispharmacy.com/",
        "https://midtowncompoundingpharmacy.ca/", 
        "https://beyondrx.ca/"
    ]
    
    print("Testing CMP Mapper with Real Pharmacy Sites")
    print("=" * 60)
    
    detector = BannerDetector()
    generator = RuleGenerator()
    
    results = []
    
    for i, url in enumerate(pharmacy_urls, 1):
        print(f"\n{i}. Testing: {url}")
        print("-" * 50)
        
        try:
            # Collect page data
            with WebScraper(headless=True, timeout=30) as scraper:
                print("  Collecting page data...")
                page_data = scraper.collect_page(url, wait_for_banner=True)
                
                if not page_data.html_content:
                    print("  [ERROR] No HTML content collected")
                    continue
                
                print(f"  [OK] Collected {len(page_data.html_content)} characters")
                
                # Save page data for analysis
                scraper.save_page_data(page_data, f"pharmacy_test_{i}.json")
                
                # Try to detect banner
                print("  Detecting consent banner...")
                banner_info = detector.detect_banner(page_data)
                
                if banner_info:
                    print(f"  [SUCCESS] Banner detected!")
                    print(f"    Type: {banner_info.banner_type.value}")
                    print(f"    Confidence: {banner_info.detection_confidence:.2f}")
                    print(f"    Container: {banner_info.container_selector}")
                    print(f"    Buttons: {len(banner_info.buttons)}")
                    
                    for button in banner_info.buttons:
                        print(f"      - {button.button_type.value}: {button.text}")
                    
                    # Generate rule
                    print("  Generating Consent O Matic rule...")
                    rule = generator.generate_rule(banner_info)
                    filepath = generator.save_rule(rule, f"pharmacy_rule_{i}.json")
                    print(f"    [OK] Rule saved to: {filepath}")
                    
                    results.append({
                        'url': url,
                        'success': True,
                        'banner_info': banner_info,
                        'rule_file': filepath
                    })
                    
                else:
                    print("  [NO BANNER] No consent banner detected")
                    
                    # Let's analyze the HTML for potential banner patterns
                    print("  Analyzing HTML for banner patterns...")
                    analyze_html_for_banners(page_data.html_content, url)
                    
                    results.append({
                        'url': url,
                        'success': False,
                        'reason': 'No banner detected'
                    })
                    
        except Exception as e:
            print(f"  [ERROR] {e}")
            results.append({
                'url': url,
                'success': False,
                'reason': str(e)
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"Sites tested: {total}")
    print(f"Banners detected: {successful}")
    print(f"Success rate: {successful/total*100:.1f}%")
    
    if successful > 0:
        print("\nSuccessful detections:")
        for result in results:
            if result['success']:
                banner = result['banner_info']
                print(f"  ✓ {result['url']} - {banner.banner_type.value} (confidence: {banner.detection_confidence:.2f})")
    
    if successful < total:
        print("\nFailed detections:")
        for result in results:
            if not result['success']:
                print(f"  ✗ {result['url']} - {result['reason']}")
    
    return results

def analyze_html_for_banners(html_content, url):
    """Analyze HTML content for potential banner patterns."""
    
    # Look for common consent-related terms
    consent_keywords = [
        'cookie', 'consent', 'gdpr', 'privacy', 'accept', 'agree', 
        'decline', 'reject', 'manage', 'preferences'
    ]
    
    html_lower = html_content.lower()
    found_keywords = [kw for kw in consent_keywords if kw in html_lower]
    
    if found_keywords:
        print(f"    Found consent keywords: {', '.join(found_keywords)}")
        
        # Look for specific patterns
        patterns_to_check = [
            ('cookie', 'cookie'),
            ('consent', 'consent'),
            ('accept', 'accept'),
            ('agree', 'agree'),
            ('privacy', 'privacy'),
            ('gdpr', 'gdpr')
        ]
        
        for keyword, label in patterns_to_check:
            if keyword in html_lower:
                # Find the context around the keyword
                import re
                pattern = f'.{{0,50}}{re.escape(keyword)}.{{0,50}}'
                matches = re.findall(pattern, html_lower, re.IGNORECASE)
                if matches:
                    print(f"    {label.upper()} context: {matches[0][:100]}...")
    else:
        print("    No obvious consent keywords found")

if __name__ == '__main__':
    test_pharmacy_sites()
