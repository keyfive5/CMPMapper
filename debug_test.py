#!/usr/bin/env python3
"""
Debug test to isolate the ButtonType issue.
"""

import sys
import os
sys.path.append('src')

try:
    print("Testing imports...")
    from src.models import BannerInfo, BannerType, ConsentButton, ButtonType
    print("✓ Models imported successfully")
    
    from src.extractors import BannerExtractor
    print("✓ BannerExtractor imported successfully")
    
    from src.detectors import BannerDetector
    print("✓ BannerDetector imported successfully")
    
    # Test banner extraction with simple HTML
    html_content = '''
    <div id="ideocookie-widget" class="cookie-banner">
        <div class="ideocookie-title">Your privacy is our priority</div>
        <div class="ideocookie-buttons">
            <div id="ideocookie-selectall" class="cookie-button__primary">Accept All</div>
            <div id="ideocookie-rejectall" class="cookie-button__secondary">Reject All</div>
        </div>
    </div>
    '''
    
    print("\nTesting banner extraction...")
    extractor = BannerExtractor()
    banner_info = extractor.extract_banner_info(html_content, "test.com")
    
    if banner_info:
        print(f"✓ Banner detected! Type: {banner_info.banner_type.value}")
        print(f"  Confidence: {banner_info.detection_confidence:.2f}")
        print(f"  Buttons: {len(banner_info.buttons)}")
    else:
        print("✗ No banner detected")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
