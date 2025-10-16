#!/usr/bin/env python3
"""
Demo script to show CMP Mapper Web UI functionality.
"""

import requests
import json
import time

def test_web_ui():
    """Test the web UI functionality."""
    base_url = "http://127.0.0.1:5000"
    
    print("CMP Mapper Web UI Demo")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("1. Testing server connection...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("   [OK] Server is running!")
        else:
            print(f"   [ERROR] Server returned status {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"   [ERROR] Server not responding: {e}")
        return
    
    # Test 2: Analyze HTML content
    print("\n2. Testing HTML analysis...")
    test_html = '''
    <div id="cookie-consent-modal" class="modal-overlay">
        <div class="cookie-banner">
            <h3>Cookie Consent</h3>
            <p>We use cookies to improve your experience.</p>
            <button id="accept-btn" class="btn-accept">Accept All</button>
            <button id="reject-btn" class="btn-reject">Reject All</button>
            <button id="manage-btn" class="btn-manage">Manage Preferences</button>
        </div>
    </div>
    '''
    
    try:
        response = requests.post(
            f"{base_url}/api/analyze-html",
            json={"html": test_html, "url": "demo-site.com"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   [OK] HTML analysis successful!")
                
                banner_info = data.get('banner_info')
                if banner_info:
                    print(f"      Banner Type: {banner_info.get('banner_type', 'Unknown')}")
                    print(f"      Confidence: {banner_info.get('confidence', 0):.2f}")
                    print(f"      Buttons Found: {len(banner_info.get('buttons', []))}")
                    
                    rule = data.get('rule')
                    if rule:
                        print(f"      Rule Generated: Yes")
                        print(f"      Actions: {', '.join(rule.get('actions', []))}")
                        print(f"      Selectors: {len(rule.get('selectors', {}))}")
                else:
                    print("      No banner detected")
            else:
                print("   [ERROR] Analysis failed")
        else:
            print(f"   [ERROR] API returned status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   [ERROR] API request failed: {e}")
    
    # Test 3: Test rule download
    print("\n3. Testing rule download...")
    try:
        response = requests.get(f"{base_url}/api/download-rule", timeout=10)
        if response.status_code == 200:
            print("   [OK] Rule download successful!")
            print(f"      File size: {len(response.content)} bytes")
        else:
            print(f"   [ERROR] Download returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   [ERROR] Download failed: {e}")
    
    print("\n" + "=" * 50)
    print("Demo completed!")
    print(f"Web UI is available at: {base_url}")
    print("Open your browser and navigate to the URL above to use the interface.")

if __name__ == "__main__":
    test_web_ui()

