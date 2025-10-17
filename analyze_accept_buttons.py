#!/usr/bin/env python3
"""
Analyze accept buttons in the collected HTML to find better selectors.
"""

import json
from bs4 import BeautifulSoup

def analyze_pharmacy_html():
    """Analyze the pharmacy HTML for accept buttons."""
    
    # Read pharmacy HTML
    with open('data/examples/pharmacy_test_1.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    html = data['html_content']
    soup = BeautifulSoup(html, 'html.parser')
    
    print("🔍 Analyzing Accept Buttons in Margis Pharmacy HTML")
    print("=" * 60)
    
    # Look for elements containing 'accept'
    accept_elements = soup.find_all(string=lambda text: text and 'accept' in text.lower())
    
    print(f"Found {len(accept_elements)} elements containing 'accept':")
    
    for i, elem in enumerate(accept_elements[:10], 1):  # Show first 10
        parent = elem.parent
        text = elem.strip()
        
        print(f"\n{i}. Text: '{text}'")
        print(f"   Parent tag: {parent.name}")
        print(f"   Parent classes: {parent.get('class', [])}")
        print(f"   Parent ID: {parent.get('id', '')}")
        
        # Generate selector
        if parent.get('id'):
            selector = f"#{parent['id']}"
        elif parent.get('class'):
            classes = [cls for cls in parent.get('class', []) if len(cls) > 3]
            if classes:
                selector = f".{'.'.join(classes[:2])}"
            else:
                selector = f"{parent.name}"
        else:
            selector = f"{parent.name}"
        
        print(f"   Suggested selector: {selector}")
    
    # Look for ideocookie specific elements
    print(f"\n🎯 Looking for ideocookie specific elements:")
    ideocookie_elements = soup.find_all(class_=lambda x: x and 'ideocookie' in ' '.join(x))
    
    for elem in ideocookie_elements[:5]:
        text = elem.get_text(strip=True)
        if text and len(text) < 50:  # Only short text (likely buttons)
            print(f"   Text: '{text}'")
            print(f"   Classes: {elem.get('class', [])}")
            print(f"   ID: {elem.get('id', '')}")
            print("---")

if __name__ == '__main__':
    analyze_pharmacy_html()
