#!/usr/bin/env python3
"""
Test HTML parsing for Arkell Medical
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from bs4 import BeautifulSoup

def test_html_parsing():
    """Test HTML parsing for Arkell Medical."""
    
    print("Testing HTML Parsing for Arkell Medical")
    print("=" * 50)
    
    try:
        # Read the debug HTML file
        with open('arkellmedical_debug.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"HTML file size: {len(html_content)} characters")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Test various selectors
        selectors_to_test = [
            "[class*='cky-']",
            ".cky-modal",
            ".cky-consent-container", 
            ".cky-notice",
            ".cky-hide",
            "[class*='cookie']",
            "[class*='consent']"
        ]
        
        print("\nTesting selectors:")
        for selector in selectors_to_test:
            elements = soup.select(selector)
            print(f"   {selector}: {len(elements)} elements")
            
            if elements and selector.startswith("[class*='cky-']"):
                print(f"      First element classes: {elements[0].get('class', [])}")
        
        # Test direct class search
        print("\nDirect class search:")
        all_elements = soup.find_all(class_=True)
        cky_elements = []
        for element in all_elements:
            classes = element.get('class', [])
            if any('cky-' in cls for cls in classes):
                cky_elements.append(element)
        
        print(f"   Elements with cky- classes: {len(cky_elements)}")
        
        if cky_elements:
            for i, element in enumerate(cky_elements[:3], 1):  # Show first 3
                classes = element.get('class', [])
                tag_name = element.name
                print(f"      Element {i}: <{tag_name}> classes={classes}")
        
        # Test text search
        print("\nText search:")
        privacy_text = soup.find_all(text=lambda text: text and 'privacy' in text.lower())
        cookie_text = soup.find_all(text=lambda text: text and 'cookie' in text.lower())
        consent_text = soup.find_all(text=lambda text: text and 'consent' in text.lower())
        
        print(f"   Text containing 'privacy': {len(privacy_text)}")
        print(f"   Text containing 'cookie': {len(cookie_text)}")
        print(f"   Text containing 'consent': {len(consent_text)}")
        
        if privacy_text:
            print(f"      First privacy text: '{privacy_text[0].strip()[:50]}...'")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_html_parsing()
