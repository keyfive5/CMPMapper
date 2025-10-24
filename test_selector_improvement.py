#!/usr/bin/env python3
"""
Test the improved selector generation for complex selectors
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.generators.rule_generator import RuleGenerator

def test_selector_improvements():
    """Test the improved selector extraction."""
    
    print("Testing Improved Selector Generation")
    print("=" * 50)
    
    generator = RuleGenerator()
    
    # Test cases with problematic selectors
    test_cases = [
        {
            "name": "Fauquier Strickland Angular Material",
            "selector": ".mdc-button.mat-mdc-button.ng-tns-c2562930882-0.mat-unthemed.mat-mdc-button-base.ng-star-inserted",
            "expected": ".mdc-button"
        },
        {
            "name": "BlendRx Complex",
            "selector": "#ae8691b3-3701-479b-9637-df346cca9778-accept, .x-el.x-el-a.c1-3g.c1-3h.c1-11.c1-6g.c1-1z.c1-1g.c1-8l.c1-em.c1-en.c1-eo.c1-3n.c1-9m.c1-z.c1-1y.c1-1d.c1-1f.c1-1e.c1-p.c1-29.c1-4.c1-4g.c1-4h.c1-ep.c1-eq.c1-er.c1-2o.c1-es.c1-3.c1-b.c1-3i.c1-6m.c1-3b.c1-et.c1-eu.c1-9t.c1-3c.c1-3d.c1-3e.c1-3f, [data-ux-btn='primary'], [data-ux='ButtonPrimary'], [data-aid='FOOTER_COOKIE_CLOSE_RENDERED'], [data-typography='ButtonAlpha'], [data-tccl='ux2.COOKIE_BANNER.cookie1.Group.Default.Button.Primary.81316.click,click']",
            "expected": "#ae8691b3-3701-479b-9637-df346cca9778-accept"
        },
        {
            "name": "Angular Dynamic Class",
            "selector": ".button.ng-tns-c1234567890-5.mat-button-base",
            "expected": ".button"
        },
        {
            "name": "Material Design Complex",
            "selector": ".mat-mdc-button.mat-unthemed.mat-mdc-button-base",
            "expected": ".mdc-button"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {test_case['name']}")
        print(f"   Original: {test_case['selector'][:100]}...")
        
        improved = generator._extract_simple_selector(test_case['selector'])
        print(f"   Improved: {improved}")
        print(f"   Expected: {test_case['expected']}")
        
        if improved == test_case['expected']:
            print("   Result: PASS")
        else:
            print("   Result: FAIL")
            print(f"   Note: Got '{improved}' instead of '{test_case['expected']}'")

if __name__ == "__main__":
    test_selector_improvements()
