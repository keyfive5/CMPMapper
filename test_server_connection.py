#!/usr/bin/env python3
"""
Quick test to verify the fixed server is working
"""

import requests
import time

def test_server():
    """Test if the server is responding"""
    try:
        print("Testing server on http://127.0.0.1:5000...")
        time.sleep(3)  # Give server time to start
        
        response = requests.get("http://127.0.0.1:5000/", timeout=10)
        
        if response.status_code == 200:
            print("✅ Server is responding!")
            if "CMP Mapper" in response.text:
                print("✅ CMP Mapper interface is loading!")
            else:
                print("⚠️  Server responding but CMP Mapper content not found")
            
            # Test API endpoint
            print("\nTesting API endpoint...")
            api_response = requests.post(
                "http://127.0.0.1:5000/api/analyze",
                json={"url": "https://example.com"},
                timeout=30
            )
            
            if api_response.status_code == 200:
                print("✅ API endpoint is working!")
                data = api_response.json()
                if data.get('success'):
                    print("✅ Analysis completed successfully")
                else:
                    print(f"⚠️  Analysis failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ API endpoint failed: {api_response.status_code}")
                
        else:
            print(f"❌ Server not responding: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server - is it running?")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_server()
