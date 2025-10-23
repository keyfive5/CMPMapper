#!/usr/bin/env python3
"""
Test the HCHC Family Health fix
"""

import requests
import json

def test_hchc_fix():
    """Test that the HCHC rule now uses the correct selector."""
    
    print("🔍 Testing HCHC Family Health Fix")
    print("=" * 40)
    
    try:
        # Test the web UI
        response = requests.post('http://127.0.0.1:5000/api/analyze', json={'url': 'https://hchcfamilyhealth.org/on-site-services.php'})
        result = response.json()
        
        if result.get('success'):
            rule = result.get('rule')
            print("✅ Success! Generated rule:")
            print(json.dumps(rule, indent=2))
            
            # Check the DO_CONSENT selector
            site_key = [k for k in rule.keys() if k != '$schema'][0]
            site_rule = rule[site_key]
            
            if isinstance(site_rule.get('methods'), list):
                for method in site_rule.get('methods', []):
                    if method.get('name') == 'DO_CONSENT':
                        action = method.get('action', {})
                        if action:
                            selector = action.get('target', {}).get('selector', '')
                            print(f"\n🎯 DO_CONSENT selector: {selector}")
                            
                            if selector == '.cookies-notification-button':
                                print("✅ PERFECT! This will click the actual consent button")
                                print("✅ The fix is working correctly!")
                            else:
                                print(f"❌ Still using wrong selector: {selector}")
                                print("❌ The fix didn't work")
        else:
            print("❌ Failed:", result.get('error'))
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_hchc_fix()