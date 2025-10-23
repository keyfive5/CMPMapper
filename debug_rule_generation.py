#!/usr/bin/env python3
"""
Debug the rule generation to see what's happening
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.collectors.web_scraper import WebScraper
from src.detectors.banner_detector import BannerDetector
from src.generators.rule_generator import RuleGenerator

def debug_rule_generation():
    """Debug the rule generation process."""
    
    print("🔍 Debugging Rule Generation")
    print("=" * 40)
    
    try:
        # Initialize components
        scraper = WebScraper()
        detector = BannerDetector()
        generator = RuleGenerator()
        
        # Test URL
        url = "https://hchcfamilyhealth.org/on-site-services.php"
        
        # Step 1: Collect page data
        print("1. Collecting page data...")
        page_data = scraper.collect_page(url)
        
        if not page_data:
            print("❌ Failed to collect page data")
            return
        
        print(f"   ✅ Page data collected: {len(page_data.html_content)} characters")
        
        # Step 2: Detect banner
        print("2. Detecting consent banner...")
        banner_info = detector.detect_banner(page_data)
        
        if not banner_info:
            print("   ❌ No banner detected")
            return
        
        print(f"   ✅ Banner detected!")
        print(f"      - Site: {banner_info.site}")
        print(f"      - Container: {banner_info.container_selector}")
        print(f"      - Buttons: {len(banner_info.buttons)}")
        
        # Step 3: Generate old format rule
        print("3. Generating old format rule...")
        old_rule = generator.generate_rule(banner_info)
        
        if old_rule:
            print("   ✅ Old format rule generated!")
            print(f"      - Site: {old_rule.site}")
            print(f"      - Selectors: {list(old_rule.selectors.keys())}")
            print(f"      - Actions: {old_rule.actions}")
        else:
            print("   ❌ Failed to generate old format rule")
        
        # Step 4: Generate Consent O Matic format rule
        print("4. Generating Consent O Matic format rule...")
        consent_o_matic_rule = generator.generate_consent_o_matic_json(banner_info)
        
        if consent_o_matic_rule:
            print("   ✅ Consent O Matic format rule generated!")
            print(f"      - Keys: {list(consent_o_matic_rule.keys())}")
            
            if '$schema' in consent_o_matic_rule:
                print(f"      - Schema: {consent_o_matic_rule['$schema']}")
            
            # Find the site key
            site_key = None
            for key in consent_o_matic_rule.keys():
                if key != '$schema':
                    site_key = key
                    break
            
            if site_key:
                print(f"      - Site Key: {site_key}")
                site_rule = consent_o_matic_rule[site_key]
                
                if 'detectors' in site_rule:
                    print(f"      - Detectors: {len(site_rule['detectors'])}")
                
                if 'methods' in site_rule:
                    methods = site_rule['methods']
                    if isinstance(methods, list):
                        # Array-based format (for editor)
                        print(f"      - Methods: {len(methods)} found")
                        for method in methods:
                            method_name = method.get('name', 'Unknown')
                            if 'action' in method:
                                action_type = method['action'].get('type', 'Unknown')
                                target_selector = method['action'].get('target', {}).get('selector', 'N/A')
                                print(f"        - {method_name}: {action_type} on '{target_selector}'")
                            else:
                                print(f"        - {method_name}: No action defined")
                    else:
                        # Object-based format (fallback)
                        print(f"      - Methods: {len(methods)} found")
                        for method_name, method_data in methods.items():
                            print(f"        - {method_name}")
        else:
            print("   ❌ Failed to generate Consent O Matic format rule")
        
        # Step 5: Show the actual JSON
        print("\n5. Generated Consent O Matic Rule JSON:")
        if consent_o_matic_rule:
            print(json.dumps(consent_o_matic_rule, indent=2))
        else:
            print("   No rule generated")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_rule_generation()
