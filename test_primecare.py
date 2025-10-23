#!/usr/bin/env python3
"""
Test Prime Care Pharmacy detection
"""

import requests
import json

def test_primecare():
    """Test Prime Care Pharmacy detection."""
    
    print("🔍 Testing Prime Care Pharmacy Detection")
    print("=" * 50)
    
    try:
        # Test the web UI
        response = requests.post('http://127.0.0.1:5000/api/analyze', json={'url': 'https://primecarepharmacy.ca/'})
        result = response.json()
        
        if result.get('success'):
            print("✅ Analysis successful")
            banner_info = result.get('banner_info')
            if banner_info:
                print(f"   Banner detected: {banner_info.get('container_selector')}")
                print(f"   Buttons: {len(banner_info.get('buttons', []))}")
                
                for i, button in enumerate(banner_info.get('buttons', []), 1):
                    print(f"     Button {i}: {button.get('text')} ({button.get('selector')})")
            else:
                print("   ❌ No banner detected")
                print("   Page data collected, but banner detection failed")
                
                # Check if we have page data
                page_data = result.get('page_data')
                if page_data:
                    print(f"   Page size: {len(page_data.get('html_content', ''))} characters")
                    print(f"   Cookie mentions: {page_data.get('cookie_mentions', 0)}")
                    print(f"   Consent mentions: {page_data.get('consent_mentions', 0)}")
        else:
            print("❌ Analysis failed:", result.get('error'))
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_primecare()
