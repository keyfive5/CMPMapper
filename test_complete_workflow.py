#!/usr/bin/env python3
"""
Complete workflow test: CMP Mapper → JSON → Consent O Matic
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.collectors.web_scraper import WebScraper
from src.detectors.banner_detector import BannerDetector
from src.generators.rule_generator import RuleGenerator

def test_complete_workflow():
    """Test the complete workflow from detection to rule generation"""
    
    print("🍪 CMP Mapper Complete Workflow Test")
    print("=" * 60)
    
    # Test URLs
    test_urls = [
        "https://margispharmacy.com",
        "https://midtowncompoundingpharmacy.ca", 
        "https://beyondrx.ca"
    ]
    
    results = []
    
    for url in test_urls:
        print(f"\n🔍 Testing: {url}")
        print("-" * 40)
        
        try:
            # Step 1: Collect page data
            print("1. Collecting page data...")
            with WebScraper(headless=True, timeout=30) as scraper:
                page_data = scraper.collect_page(url)
            
            if not page_data or not page_data.html_content:
                print("   ❌ Failed to collect page data")
                continue
            
            print(f"   ✅ Page data collected: {len(page_data.html_content)} characters")
            
            # Step 2: Detect banner
            print("2. Detecting consent banner...")
            detector = BannerDetector()
            banner_info = detector.detect_banner(page_data)
            
            if not banner_info:
                print("   ❌ No banner detected")
                continue
            
            print(f"   ✅ Banner detected!")
            print(f"      - Confidence: {banner_info.detection_confidence:.2f}")
            print(f"      - Container: {banner_info.container_selector}")
            print(f"      - Buttons: {len(banner_info.buttons)}")
            
            # Step 3: Generate rule
            print("3. Generating Consent O Matic rule...")
            generator = RuleGenerator()
            rule = generator.generate_rule(banner_info)
            
            print(f"   ✅ Rule generated!")
            print(f"      - Site: {rule.site}")
            print(f"      - Selectors: {len(rule.selectors)}")
            print(f"      - Actions: {len(rule.actions)}")
            
            # Step 4: Save rule
            print("4. Saving rule to JSON...")
            rule_file = generator.save_rule(rule)
            print(f"   ✅ Rule saved to: {rule_file}")
            
            # Step 5: Show rule content
            print("5. Rule content preview:")
            with open(rule_file, 'r', encoding='utf-8') as f:
                rule_data = json.load(f)
            
            print(f"   📋 Rule Summary:")
            print(f"      - Name: {rule_data.get('name', 'Unknown')}")
            print(f"      - Selectors: {list(rule_data.get('selectors', {}).keys())}")
            print(f"      - Actions: {rule_data.get('actions', [])}")
            
            results.append({
                'url': url,
                'success': True,
                'rule_file': rule_file,
                'confidence': banner_info.detection_confidence
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'url': url,
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print(f"\n📊 Workflow Test Summary")
    print("=" * 60)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if successful:
        print(f"\n🎯 Generated Rules:")
        for result in successful:
            print(f"   • {result['url']} → {result['rule_file']} (Confidence: {result['confidence']:.2f})")
    
    if failed:
        print(f"\n❌ Failed URLs:")
        for result in failed:
            print(f"   • {result['url']}: {result['error']}")
    
    print(f"\n📋 Next Steps:")
    print("1. Open Consent O Matic extension")
    print("2. Go to 'GDPR Consent Rules Editor'")
    print("3. Click 'From Pasted JSON'")
    print("4. Copy and paste the JSON content from the generated rule files")
    print("5. Click 'Load' to import the rule")
    print("6. Click 'Save Custom Rule' to make it permanent")
    print("7. Test by visiting the websites - banners should be handled automatically!")
    
    return results

if __name__ == "__main__":
    test_complete_workflow()
