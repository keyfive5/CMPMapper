#!/usr/bin/env python3
"""
Analyze Walmart HTML content to find cookie banner
"""

import sys
import os
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.collectors.web_scraper import WebScraper

def analyze_walmart_html():
    """Analyze Walmart HTML to find cookie banner elements."""
    
    url = 'https://www.walmart.ca/en/cp/digital-pharmacy/6000206038183'
    print(f"🔍 Analyzing Walmart HTML Content")
    print(f"URL: {url}")
    print("=" * 60)
    
    try:
        scraper = WebScraper()
        page_data = scraper.collect_page(url)
        
        if not page_data or not page_data.html_content:
            print("❌ Failed to collect page data")
            return
        
        html_content = page_data.html_content
        html_lower = html_content.lower()
        
        print(f"📄 HTML Content Analysis:")
        print(f"   Total size: {len(html_content)} characters")
        
        # Find all cookie mentions with context
        print(f"\n🍪 Cookie Mentions (with context):")
        cookie_matches = []
        for match in re.finditer(r'cookie', html_lower):
            start = max(0, match.start() - 50)
            end = min(len(html_content), match.end() + 50)
            context = html_content[start:end]
            cookie_matches.append((match.start(), context))
        
        for i, (pos, context) in enumerate(cookie_matches[:5], 1):  # Show first 5
            print(f"   {i}. Position {pos}: ...{context}...")
        
        # Look for specific Walmart cookie banner patterns
        print(f"\n🔍 Searching for Walmart-specific patterns:")
        
        # Common Walmart cookie banner patterns
        walmart_patterns = [
            r'cookie.*settings',
            r'cookie.*preferences',
            r'cookie.*choices',
            r'manage.*cookie',
            r'cookie.*policy',
            r'accept.*all.*cookie',
            r'cookie.*consent',
            r'privacy.*settings',
            r'data.*preferences'
        ]
        
        for pattern in walmart_patterns:
            matches = re.findall(pattern, html_lower)
            if matches:
                print(f"   ✅ Found '{pattern}': {len(matches)} matches")
        
        # Look for JavaScript cookie handling
        print(f"\n🔍 JavaScript Cookie Handling:")
        js_patterns = [
            r'cookieconsent',
            r'cookiebot',
            r'consentmanager',
            r'privacy.*banner',
            r'cookie.*banner',
            r'gdpr.*consent'
        ]
        
        for pattern in js_patterns:
            if pattern in html_lower:
                print(f"   ✅ Found JavaScript pattern: {pattern}")
        
        # Look for specific HTML elements that might be cookie banners
        print(f"\n🔍 HTML Elements Analysis:")
        
        # Find div elements with cookie-related classes
        div_pattern = r'<div[^>]*class="[^"]*"[^>]*>'
        div_matches = re.findall(div_pattern, html_lower)
        
        cookie_divs = []
        for div in div_matches:
            if any(word in div for word in ['cookie', 'consent', 'privacy', 'banner']):
                cookie_divs.append(div)
        
        if cookie_divs:
            print(f"   ✅ Found {len(cookie_divs)} div elements with cookie-related classes:")
            for div in cookie_divs[:3]:  # Show first 3
                print(f"      {div}")
        
        # Look for button elements
        button_pattern = r'<button[^>]*>.*?</button>'
        button_matches = re.findall(button_pattern, html_lower, re.DOTALL)
        
        cookie_buttons = []
        for button in button_matches:
            if any(word in button for word in ['accept', 'consent', 'cookie', 'allow', 'agree']):
                cookie_buttons.append(button)
        
        if cookie_buttons:
            print(f"   ✅ Found {len(cookie_buttons)} button elements with consent-related text:")
            for button in cookie_buttons[:3]:  # Show first 3
                clean_button = re.sub(r'\s+', ' ', button.strip())
                print(f"      {clean_button[:100]}...")
        
        # Look for anchor elements
        anchor_pattern = r'<a[^>]*>.*?</a>'
        anchor_matches = re.findall(anchor_pattern, html_lower, re.DOTALL)
        
        cookie_anchors = []
        for anchor in anchor_matches:
            if any(word in anchor for word in ['cookie', 'privacy', 'consent', 'settings', 'preferences']):
                cookie_anchors.append(anchor)
        
        if cookie_anchors:
            print(f"   ✅ Found {len(cookie_anchors)} anchor elements with cookie-related text:")
            for anchor in cookie_anchors[:3]:  # Show first 3
                clean_anchor = re.sub(r'\s+', ' ', anchor.strip())
                print(f"      {clean_anchor[:100]}...")
        
        # Save HTML content for manual inspection
        output_file = 'walmart_page_content.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\n💾 Saved HTML content to: {output_file}")
        
        print(f"\n📊 Summary:")
        print(f"   - Cookie mentions: {len(cookie_matches)}")
        print(f"   - Cookie-related divs: {len(cookie_divs)}")
        print(f"   - Cookie-related buttons: {len(cookie_buttons)}")
        print(f"   - Cookie-related anchors: {len(cookie_anchors)}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_walmart_html()
