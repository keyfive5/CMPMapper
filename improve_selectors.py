#!/usr/bin/env python3
"""
Improve selectors for better Consent O Matic compatibility.
"""

import json
import os
from bs4 import BeautifulSoup

def find_better_accept_selector(html_file, target_url):
    """Find better accept button selectors by analyzing the HTML."""
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for common accept button patterns
    accept_patterns = [
        # Text-based patterns
        'accept', 'agree', 'ok', 'yes', 'allow', 'consent',
        'accept all', 'agree all', 'allow all', 'accept cookies'
    ]
    
    better_selectors = []
    
    for pattern in accept_patterns:
        # Find elements containing the pattern
        elements = soup.find_all(text=lambda text: text and pattern.lower() in text.lower())
        
        for element in elements:
            # Get the parent element (usually the button)
            parent = element.parent
            
            if parent:
                # Generate selector
                selector = generate_simple_selector(parent)
                if selector and selector not in better_selectors:
                    better_selectors.append({
                        'selector': selector,
                        'text': element.strip(),
                        'tag': parent.name,
                        'classes': parent.get('class', []),
                        'id': parent.get('id', '')
                    })
    
    return better_selectors

def generate_simple_selector(element):
    """Generate a simple, reliable selector."""
    
    # Try ID first
    if element.get('id'):
        return f"#{element['id']}"
    
    # Try class combination
    classes = element.get('class', [])
    if classes:
        # Filter out generic classes
        good_classes = [cls for cls in classes if len(cls) > 3 and not cls.startswith('x-')]
        if good_classes:
            return f".{'.'.join(good_classes[:2])}"  # Use max 2 classes
    
    # Try data attributes
    for attr, value in element.attrs.items():
        if attr.startswith('data-') and value:
            return f"[{attr}='{value}']"
    
    # Fallback to tag with parent context
    if element.parent:
        return f"{element.parent.name} {element.name}"
    
    return None

def main():
    """Main function to improve selectors."""
    print("🔍 Improving Accept Button Selectors")
    print("=" * 50)
    
    # Look for HTML files
    examples_dir = "data/examples"
    if not os.path.exists(examples_dir):
        print("❌ No examples directory found")
        return
    
    html_files = [f for f in os.listdir(examples_dir) if f.endswith('.json')]
    
    for html_file in html_files[:2]:  # Check first 2 files
        file_path = os.path.join(examples_dir, html_file)
        print(f"\n📄 Analyzing: {html_file}")
        
        try:
            # Read the JSON file (it contains HTML)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            html_content = data.get('html_content', '')
            if not html_content:
                print("  ❌ No HTML content found")
                continue
            
            # Save HTML to temp file for analysis
            temp_html = f"temp_{html_file.replace('.json', '.html')}"
            with open(temp_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Find better selectors
            selectors = find_better_accept_selector(temp_html, data.get('url', ''))
            
            print(f"  🎯 Found {len(selectors)} potential accept button selectors:")
            for i, sel in enumerate(selectors[:5], 1):  # Show top 5
                print(f"    {i}. {sel['selector']}")
                print(f"       Text: '{sel['text']}'")
                print(f"       Tag: {sel['tag']}, Classes: {sel['classes']}")
            
            # Clean up temp file
            os.remove(temp_html)
            
        except Exception as e:
            print(f"  ❌ Error analyzing {html_file}: {e}")

if __name__ == '__main__':
    main()
