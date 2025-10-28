#!/usr/bin/env python3
"""
Simple test to verify server is working
"""

import requests
import time

def test_server():
    try:
        print("Testing server...")
        time.sleep(2)
        
        response = requests.get("http://127.0.0.1:5000/", timeout=5)
        
        if response.status_code == 200:
            print("SUCCESS: Server is responding!")
            if "CMP Mapper" in response.text:
                print("SUCCESS: CMP Mapper interface found!")
            else:
                print("WARNING: Server responding but CMP Mapper content not found")
        else:
            print(f"ERROR: Server returned status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server")
    except requests.exceptions.Timeout:
        print("ERROR: Server timeout")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_server()
