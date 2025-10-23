#!/usr/bin/env python3
"""
Test the web UI fix for Consent O Matic format
"""

import sys
import os
import json
import requests
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_web_ui_fix():
    """Test that the web UI returns the correct Consent O Matic format."""
    
    print("🔍 Testing Web UI Fix for Consent O Matic Format")
    print("=" * 60)
    
    try:
        # Test the API endpoint
        url = "http://127.0.0.1:5000/api/analyze"
        data = {
            "url": "https://hchcfamilyhealth.org/on-site-services.php"
        }
        
        print("1. Sending request to web UI...")
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Request failed with status code: {response.status_code}")
            return
        
        result = response.json()
        
        if not result.get('success'):
            print(f"❌ API returned error: {result.get('error', 'Unknown error')}")
            return
        
        print("   ✅ Request successful!")
        
        # Check if the rule is in the correct format
        rule = result.get('rule')
        if not rule:
            print("❌ No rule found in response")
            return
        
        print("2. Checking rule format...")
        
        # Check for Consent O Matic format
        if rule.get('$schema') and 'detectors' in str(rule) and 'methods' in str(rule):
            print("   ✅ Rule is in Consent O Matic format!")
            
            # Show the rule structure
            print(f"\n📄 Generated Rule Structure:")
            print(f"   - Schema: {rule.get('$schema', 'N/A')}")
            
            # Find the site key
            site_key = None
            for key in rule.keys():
                if key != '$schema':
                    site_key = key
                    break
            
            if site_key:
                print(f"   - Site: {site_key}")
                site_rule = rule[site_key]
                
                if 'detectors' in site_rule:
                    detectors = site_rule['detectors']
                    if isinstance(detectors, dict):
                        # Object-based format
                        if 'presentMatcher' in detectors:
                            present_selector = detectors['presentMatcher']['target']['selector']
                            print(f"     Present Matcher = '{present_selector}'")
                        if 'showingMatcher' in detectors:
                            showing_selector = detectors['showingMatcher']['target']['selector']
                            print(f"     Showing Matcher = '{showing_selector}'")
                    else:
                        # Array-based format (fallback)
                        print(f"   - Detectors: {len(detectors)} found")
                        for i, detector in enumerate(detectors):
                            if 'presentMatcher' in detector:
                                present_selector = detector['presentMatcher'][0]['target']['selector']
                                print(f"     Detector {i+1}: Present Matcher = '{present_selector}'")
                            if 'showingMatcher' in detector:
                                showing_selector = detector['showingMatcher'][0]['target']['selector']
                                print(f"     Detector {i+1}: Showing Matcher = '{showing_selector}'")
                
                if 'methods' in site_rule:
                    methods = site_rule['methods']
                    if isinstance(methods, dict):
                        # Object-based format
                        print(f"   - Methods: {len(methods)} found")
                        for method_name, method_data in methods.items():
                            if 'action' in method_data:
                                action_type = method_data['action'].get('type', 'Unknown')
                                target_selector = method_data['action'].get('target', {}).get('selector', 'N/A')
                                print(f"     - {method_name}: {action_type} on '{target_selector}'")
                            else:
                                print(f"     - {method_name}: No action defined")
                    else:
                        # Array-based format (fallback)
                        print(f"   - Methods: {len(methods)} found")
                        for method in methods:
                            method_name = method.get('name', 'Unknown')
                            if 'action' in method:
                                action_type = method['action'].get('type', 'Unknown')
                                target_selector = method['action'].get('target', {}).get('selector', 'N/A')
                                print(f"     - {method_name}: {action_type} on '{target_selector}'")
                            else:
                                print(f"     - {method_name}: No action defined")
            
            print(f"\n🎉 SUCCESS! The web UI now returns the correct Consent O Matic format!")
            
        else:
            print("   ❌ Rule is still in the old format")
            print(f"   Rule keys: {list(rule.keys())}")
            if 'selectors' in rule:
                print(f"   Old format detected - has 'selectors' key")
            if 'actions' in rule:
                print(f"   Old format detected - has 'actions' key")
    
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to web UI. Make sure it's running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_web_ui_fix()
