#!/usr/bin/env python3
"""
Simple analysis of Consent O Matic JSON formats
"""

import requests
import json
import os

def fetch_and_analyze_examples():
    """Fetch and analyze a few key examples."""
    
    examples = [
        {
            "name": "Cookiebot",
            "url": "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules/cookiebot.json"
        },
        {
            "name": "OneTrust", 
            "url": "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules/onetrust.json"
        },
        {
            "name": "Amazon",
            "url": "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules/amazon.json"
        }
    ]
    
    results = {}
    
    print("🔍 Fetching Consent O Matic examples...")
    print("=" * 50)
    
    for example in examples:
        try:
            print(f"📥 Fetching {example['name']}...")
            response = requests.get(example['url'], timeout=10)
            response.raise_for_status()
            
            rule_data = response.json()
            results[example['name']] = rule_data
            
            print(f"   ✅ Success: {len(str(rule_data))} characters")
            
            # Show structure
            if isinstance(rule_data, dict):
                print(f"   📋 Structure: {list(rule_data.keys())}")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    return results

def create_format_guide(results):
    """Create a format guide based on the results."""
    
    guide = {
        "title": "Consent O Matic JSON Format Guide",
        "description": "Understanding different Consent O Matic JSON rule formats",
        "formats": {
            "detector_method_format": {
                "description": "Uses detectors and methods structure",
                "example": "Cookiebot, OneTrust",
                "structure": {
                    "detectors": {
                        "presentMatcher": "CSS selector to detect banner presence",
                        "showingMatcher": "CSS selector to detect banner visibility"
                    },
                    "methods": {
                        "HIDE_CMP": "Hide the banner",
                        "DO_CONSENT": "Click accept button", 
                        "OPEN_OPTIONS": "Open preferences",
                        "SAVE_CONSENT": "Save preferences"
                    }
                }
            },
            "simple_action_format": {
                "description": "Simple action-based format",
                "example": "Amazon, Facebook",
                "structure": {
                    "actions": "Array of actions to perform",
                    "target": "CSS selector for the element"
                }
            }
        },
        "common_patterns": {
            "banner_detection": [
                ".cookie-banner",
                "#cookie-notice", 
                "[data-cookie]",
                ".consent-banner"
            ],
            "button_selectors": [
                "#accept-cookies",
                ".accept-button",
                "[data-accept]",
                ".consent-accept"
            ],
            "action_types": [
                "click",
                "hide", 
                "wait",
                "scroll"
            ]
        }
    }
    
    return guide

def save_results(results, guide):
    """Save the analysis results."""
    
    os.makedirs("data/consent_o_matic_research", exist_ok=True)
    
    # Save examples
    with open("data/consent_o_matic_research/examples.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Save guide
    with open("data/consent_o_matic_research/format_guide.json", 'w', encoding='utf-8') as f:
        json.dump(guide, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to:")
    print(f"   • data/consent_o_matic_research/examples.json")
    print(f"   • data/consent_o_matic_research/format_guide.json")

def main():
    """Main function."""
    
    print("🍪 Consent O Matic Format Analysis")
    print("=" * 50)
    
    # Fetch examples
    results = fetch_and_analyze_examples()
    
    if not results:
        print("❌ No examples fetched.")
        return
    
    # Create guide
    guide = create_format_guide(results)
    
    # Save results
    save_results(results, guide)
    
    print(f"\n🎉 Analysis Complete!")
    print(f"   • Analyzed {len(results)} examples")
    print(f"   • Created format guide")
    
    # Show key insights
    print(f"\n📊 Key Insights:")
    for name, data in results.items():
        if isinstance(data, dict):
            keys = list(data.keys())
            print(f"   • {name}: {keys}")

if __name__ == "__main__":
    main()
