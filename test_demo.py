#!/usr/bin/env python3
"""
Simple demonstration of CMP Mapper functionality.
"""

import sys
import os
sys.path.append('src')

from src.extractors import BannerExtractor
from src.generators import RuleGenerator
from src.models import BannerInfo, BannerType, ConsentButton, ButtonType

def main():
    print('CMP Mapper - Basic Functionality Test')
    print('=' * 50)

    # Test banner extraction with example HTML
    html_content = '''
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

    print('1. Testing banner extraction...')
    try:
        extractor = BannerExtractor()
        banner_info = extractor.extract_banner_info(html_content, 'example.com')

        if banner_info:
            print(f'   [OK] Banner detected!')
            print(f'   Type: {banner_info.banner_type.value}')
            print(f'   Confidence: {banner_info.detection_confidence:.2f}')
            print(f'   Buttons: {len(banner_info.buttons)}')
            print(f'   Container: {banner_info.container_selector}')
            
            print('\n2. Testing rule generation...')
            generator = RuleGenerator()
            rule = generator.generate_rule(banner_info)
            
            print(f'   [OK] Rule generated for: {rule.site}')
            print(f'   Actions: {rule.actions}')
            print(f'   Selectors: {list(rule.selectors.keys())}')
            
            print('\n3. Testing rule validation...')
            validation = generator.validate_rule(rule)
            print(f'   Valid: {validation["valid"]}')
            print(f'   Score: {validation["score"]:.2f}')
            
            print('\n4. Testing rule optimization...')
            optimized = generator.optimize_rule(rule)
            print(f'   [OK] Rule optimized')
            print(f'   Optimized actions: {optimized.actions}')
            
        else:
            print('   [FAIL] No banner detected')

    except Exception as e:
        print(f'   [ERROR] {e}')
        import traceback
        traceback.print_exc()

    print('\nTest completed!')

if __name__ == '__main__':
    main()

