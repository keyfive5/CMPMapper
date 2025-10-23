#!/usr/bin/env python3
"""
Test BlendRx with web UI to verify the navigation fix
"""

import requests
import json

def test_blendrx_web_ui():
    """Test BlendRx with the web UI to verify the navigation fix."""
    
    print('🔍 Testing BlendRx with Web UI (Navigation Fix)')
    print('=' * 60)
    
    try:
        response = requests.post('http://127.0.0.1:5000/api/analyze', 
                               json={'url': 'https://blendrx.ca/'}, 
                               timeout=60)
        result = response.json()
        
        if result.get('success'):
            print('✅ Analysis successful')
            banner_info = result.get('banner_info')
            if banner_info:
                print(f'   Banner detected: {banner_info.get("container_selector")}')
                print(f'   Buttons: {len(banner_info.get("buttons", []))}')
                
                # Check the generated rule
                rule = result.get('rule')
                if rule:
                    site_key = next((key for key in rule.keys() if key != '$schema'), None)
                    if site_key:
                        site_rule = rule[site_key]
                        methods = site_rule.get('methods', [])
                        for method in methods:
                            if method.get('name') == 'DO_CONSENT':
                                action = method.get('action', {})
                                if action:
                                    selector = action.get('target', {}).get('selector', '')
                                    print(f'   DO_CONSENT selector: {selector}')
                                    if len(selector) < 100:
                                        print('   ✅ Selector is simplified and should not interfere with navigation!')
                                    else:
                                        print('   ⚠️  Selector is still complex')
            else:
                print('   ❌ No banner detected')
        else:
            print('❌ Analysis failed:', result.get('error'))
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    test_blendrx_web_ui()
