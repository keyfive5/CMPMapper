#!/usr/bin/env python3
"""
User-friendly testing interface for CMP Mapper.
"""

import sys
import os
import json
from datetime import datetime
sys.path.append('src')

from src.collectors import WebScraper, BannerCollector
from src.detectors import BannerDetector
from src.generators import RuleGenerator
from src.models import PageData, BannerInfo

# Version tracking
VERSION = "1.0.0"
LAST_UPDATED = "2025-01-16 19:15:00 UTC"

def print_header():
    """Print the application header with version info."""
    print("=" * 70)
    print("🍪 CMP MAPPER - Cookie Consent Detection Tool")
    print("=" * 70)
    print(f"📅 Version: {VERSION}")
    print(f"🕒 Last Updated: {LAST_UPDATED}")
    print("=" * 70)

def test_single_url():
    """Test a single URL."""
    print("\n🔍 SINGLE URL TEST")
    print("-" * 50)
    
    url = input("Enter URL to test: ").strip()
    if not url:
        print("❌ No URL provided")
        return
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    print(f"\n🚀 Testing: {url}")
    print("⏳ This may take 10-30 seconds...")
    
    try:
        # Initialize components
        detector = BannerDetector()
        generator = RuleGenerator()
        
        # Collect page data
        with WebScraper(headless=True, timeout=30) as scraper:
            print("📥 Collecting page data...")
            page_data = scraper.collect_page(url, wait_for_banner=True)
            
            if not page_data.html_content:
                print("❌ Failed to collect page data")
                return
            
            print(f"✅ Collected {len(page_data.html_content)} characters")
            
            # Detect banner
            print("🔍 Detecting consent banner...")
            banner_info = detector.detect_banner(page_data)
            
            if banner_info:
                print(f"\n🎉 BANNER DETECTED!")
                print(f"   📋 Type: {banner_info.banner_type.value}")
                print(f"   🎯 Confidence: {banner_info.detection_confidence:.2f}")
                print(f"   📦 Container: {banner_info.container_selector}")
                print(f"   🔘 Buttons: {len(banner_info.buttons)}")
                
                # Show button details
                if banner_info.buttons:
                    print("   🔘 Button Details:")
                    for i, button in enumerate(banner_info.buttons[:5], 1):  # Show first 5
                        print(f"      {i}. {button.button_type.value}: '{button.text}'")
                    if len(banner_info.buttons) > 5:
                        print(f"      ... and {len(banner_info.buttons) - 5} more")
                
                # Generate rule
                print("\n⚙️  Generating Consent O Matic rule...")
                rule = generator.generate_rule(banner_info)
                
                # Save with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"test_rule_{timestamp}.json"
                filepath = generator.save_rule(rule, filename)
                
                print(f"💾 Rule saved to: {filepath}")
                
                # Show rule preview
                print("\n📄 Rule Preview:")
                print(f"   Site: {rule.site}")
                print(f"   Actions: {', '.join(rule.actions)}")
                print(f"   Banner Selector: {rule.selectors.get('banner', 'N/A')[:100]}...")
                
                return True
            else:
                print("\n❌ NO BANNER DETECTED")
                
                # Analyze for potential issues
                print("\n🔍 Analyzing HTML for consent patterns...")
                analyze_html_for_patterns(page_data.html_content)
                
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_multiple_urls():
    """Test multiple URLs from a list."""
    print("\n🔍 MULTIPLE URL TEST")
    print("-" * 50)
    
    # Default test URLs
    default_urls = [
        "https://www.margispharmacy.com/",
        "https://midtowncompoundingpharmacy.ca/",
        "https://beyondrx.ca/"
    ]
    
    print("Default test URLs:")
    for i, url in enumerate(default_urls, 1):
        print(f"  {i}. {url}")
    
    choice = input("\nUse default URLs? (y/n): ").strip().lower()
    
    if choice == 'y' or choice == 'yes':
        urls = default_urls
    else:
        urls_input = input("Enter URLs (comma-separated): ").strip()
        urls = [url.strip() for url in urls_input.split(',') if url.strip()]
    
    if not urls:
        print("❌ No URLs provided")
        return
    
    print(f"\n🚀 Testing {len(urls)} URLs...")
    
    results = []
    for i, url in enumerate(urls, 1):
        print(f"\n{i}/{len(urls)} Testing: {url}")
        print("-" * 40)
        
        try:
            detector = BannerDetector()
            generator = RuleGenerator()
            
            with WebScraper(headless=True, timeout=30) as scraper:
                page_data = scraper.collect_page(url, wait_for_banner=True)
                
                if not page_data.html_content:
                    results.append({'url': url, 'success': False, 'reason': 'No HTML content'})
                    continue
                
                banner_info = detector.detect_banner(page_data)
                
                if banner_info:
                    rule = generator.generate_rule(banner_info)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"batch_rule_{i}_{timestamp}.json"
                    filepath = generator.save_rule(rule, filename)
                    
                    results.append({
                        'url': url, 
                        'success': True, 
                        'confidence': banner_info.detection_confidence,
                        'banner_type': banner_info.banner_type.value,
                        'buttons': len(banner_info.buttons),
                        'rule_file': filepath
                    })
                    
                    print(f"✅ Detected: {banner_info.banner_type.value} (confidence: {banner_info.detection_confidence:.2f})")
                else:
                    results.append({'url': url, 'success': False, 'reason': 'No banner detected'})
                    print("❌ No banner detected")
                    
        except Exception as e:
            results.append({'url': url, 'success': False, 'reason': str(e)})
            print(f"❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"🌐 Sites tested: {total}")
    print(f"✅ Banners detected: {successful}")
    print(f"📈 Success rate: {successful/total*100:.1f}%")
    
    if successful > 0:
        print("\n🎉 Successful detections:")
        for result in results:
            if result['success']:
                print(f"  ✅ {result['url']}")
                print(f"     Type: {result['banner_type']}")
                print(f"     Confidence: {result['confidence']:.2f}")
                print(f"     Buttons: {result['buttons']}")
                print(f"     Rule: {result['rule_file']}")
    
    if successful < total:
        print("\n❌ Failed detections:")
        for result in results:
            if not result['success']:
                print(f"  ❌ {result['url']} - {result['reason']}")

def analyze_html_for_patterns(html_content):
    """Analyze HTML for consent-related patterns."""
    consent_keywords = [
        'cookie', 'consent', 'gdpr', 'privacy', 'accept', 'agree', 
        'decline', 'reject', 'manage', 'preferences'
    ]
    
    html_lower = html_content.lower()
    found_keywords = [kw for kw in consent_keywords if kw in html_lower]
    
    if found_keywords:
        print(f"🔍 Found consent keywords: {', '.join(found_keywords)}")
        
        # Look for specific patterns
        patterns = [
            ('cookie', '🍪 Cookie'),
            ('consent', '📋 Consent'),
            ('accept', '✅ Accept'),
            ('agree', '👍 Agree'),
            ('privacy', '🔒 Privacy'),
            ('gdpr', '🇪🇺 GDPR')
        ]
        
        for keyword, label in patterns:
            if keyword in html_lower:
                import re
                pattern = f'.{{0,50}}{re.escape(keyword)}.{{0,50}}'
                matches = re.findall(pattern, html_lower, re.IGNORECASE)
                if matches:
                    context = matches[0][:80].replace('\n', ' ').strip()
                    print(f"   {label}: {context}...")
    else:
        print("🔍 No obvious consent keywords found")

def show_recent_rules():
    """Show recently generated rules."""
    print("\n📁 RECENT RULES")
    print("-" * 50)
    
    rules_dir = "data/rules"
    if not os.path.exists(rules_dir):
        print("❌ No rules directory found")
        return
    
    try:
        files = [f for f in os.listdir(rules_dir) if f.endswith('.json')]
        if not files:
            print("❌ No rules found")
            return
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(rules_dir, x)), reverse=True)
        
        print(f"📄 Found {len(files)} rule files:")
        for i, filename in enumerate(files[:10], 1):  # Show last 10
            filepath = os.path.join(rules_dir, filename)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            print(f"  {i}. {filename}")
            print(f"     📅 Created: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Load and show basic info
            try:
                with open(filepath, 'r') as f:
                    rule = json.load(f)
                print(f"     🌐 Site: {rule.get('site', 'Unknown')}")
                print(f"     🎯 Confidence: {rule.get('metadata', {}).get('confidence_score', 'Unknown')}")
            except:
                pass
            print()
                
    except Exception as e:
        print(f"❌ Error reading rules: {e}")

def main():
    """Main testing interface."""
    print_header()
    
    while True:
        print("\n🎯 TESTING OPTIONS:")
        print("1. Test single URL")
        print("2. Test multiple URLs (batch)")
        print("3. Show recent rules")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            test_single_url()
        elif choice == '2':
            test_multiple_urls()
        elif choice == '3':
            show_recent_rules()
        elif choice == '4':
            print("\n👋 Thanks for using CMP Mapper!")
            break
        else:
            print("❌ Invalid option. Please choose 1-4.")
        
        input("\nPress Enter to continue...")

if __name__ == '__main__':
    main()
