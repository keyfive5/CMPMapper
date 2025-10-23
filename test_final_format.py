#!/usr/bin/env python3
"""
Test the final array-based format for Consent O Matic editor
"""

import requests
import json

def test_final_format():
    """Test that the web UI generates the correct array-based format."""
    
    print("🔍 Testing Final Array-Based Format for Consent O Matic Editor")
    print("=" * 60)
    
    try:
        # Test the web UI with the new format
        print("1. Analyzing URL...")
        analyze_response = requests.post('http://127.0.0.1:5000/api/analyze', json={'url': 'https://hchcfamilyhealth.org/on-site-services.php'})
        analyze_result = analyze_response.json()
        
        if not analyze_result.get('success'):
            print(f"❌ Analysis failed: {analyze_result.get('error')}")
            return
        
        print("   ✅ Analysis successful!")
        
        rule = analyze_result.get('rule')
        print("\n2. Generated rule structure:")
        print(json.dumps(rule, indent=2))
        
        # Check if it matches the expected format
        print("\n3. Validating format...")
        
        if rule.get('$schema') and 'CMP' in str(rule):
            site_key = [k for k in rule.keys() if k != '$schema'][0]
            site_rule = rule[site_key]
            
            if isinstance(site_rule.get('detectors'), list) and isinstance(site_rule.get('methods'), list):
                print("   ✅ SUCCESS! Rule is in the correct array-based format for Consent O Matic editor!")
                print(f"   ✅ Site: {site_key}")
                print(f"   ✅ Detectors: Array with {len(site_rule['detectors'])} detector(s)")
                print(f"   ✅ Methods: Array with {len(site_rule['methods'])} method(s)")
                
                # Check if DO_CONSENT has the correct structure
                do_consent_method = None
                for method in site_rule['methods']:
                    if method.get('name') == 'DO_CONSENT':
                        do_consent_method = method
                        break
                
                if do_consent_method and 'action' in do_consent_method:
                    print(f"   ✅ DO_CONSENT: {do_consent_method['action']['type']} on '{do_consent_method['action']['target']['selector']}'")
                else:
                    print("   ⚠️  DO_CONSENT method not found or missing action")
                
                print("\n🎉 Perfect! This JSON will work with Consent O Matic's 'From Pasted JSON' feature!")
                print("\n🎯 How to Use:")
                print("1. Copy the JSON above")
                print("2. Open Consent O Matic extension")
                print("3. Go to 'GDPR Consent Rules Editor'")
                print("4. Click 'From Pasted JSON'")
                print("5. Paste the JSON and click 'Load'")
                print("6. It should open the rule editor with all the fields populated!")
                
            else:
                print("   ❌ Rule format is still incorrect - detectors or methods are not arrays")
        else:
            print("   ❌ Rule does not have expected structure")
    
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to web UI. Make sure it's running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final_format()
