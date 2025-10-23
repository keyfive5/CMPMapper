#!/usr/bin/env python3
"""
Research Consent O Matic JSON formats from the official repository
"""

import requests
import json
import os
from typing import Dict, List, Any

def fetch_consent_o_matic_examples():
    """Fetch and analyze Consent O Matic JSON rule examples."""
    
    # Sample URLs from the references you provided
    sample_urls = [
        "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules/cookiebot.json",
        "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules/onetrust.json", 
        "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules/amazon.json",
        "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules/facebook.json",
        "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules/google_popup.json",
        "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules/cookieinformation.json",
        "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules/quantcast.json",
        "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules/sourcepoint.json"
    ]
    
    examples = {}
    
    print("🔍 Fetching Consent O Matic JSON examples...")
    print("=" * 60)
    
    for url in sample_urls:
        try:
            print(f"📥 Fetching: {url.split('/')[-1]}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            rule_data = response.json()
            rule_name = url.split('/')[-1].replace('.json', '')
            examples[rule_name] = rule_data
            
            print(f"   ✅ Success: {len(str(rule_data))} characters")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    return examples

def analyze_json_formats(examples: Dict[str, Any]):
    """Analyze the different JSON formats found."""
    
    print(f"\n📊 Analyzing {len(examples)} JSON rule formats...")
    print("=" * 60)
    
    format_analysis = {
        "common_patterns": {},
        "action_types": set(),
        "selector_patterns": set(),
        "method_types": set()
    }
    
    for rule_name, rule_data in examples.items():
        print(f"\n🔍 Analyzing {rule_name}:")
        
        # Analyze structure
        if isinstance(rule_data, dict):
            for key, value in rule_data.items():
                if key not in format_analysis["common_patterns"]:
                    format_analysis["common_patterns"][key] = 0
                format_analysis["common_patterns"][key] += 1
                
                # Look for actions
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if "action" in sub_key.lower():
                            if isinstance(sub_value, dict) and "type" in sub_value:
                                format_analysis["action_types"].add(sub_value["type"])
                        if "method" in sub_key.lower():
                            format_analysis["method_types"].add(sub_key)
                        if "selector" in sub_key.lower():
                            if isinstance(sub_value, str):
                                format_analysis["selector_patterns"].add(sub_value[:50] + "...")
    
    return format_analysis

def create_format_guide(examples: Dict[str, Any], analysis: Dict[str, Any]):
    """Create a comprehensive format guide."""
    
    guide = {
        "title": "Consent O Matic JSON Format Guide",
        "description": "Complete guide to Consent O Matic JSON rule formats",
        "formats": {},
        "examples": {},
        "patterns": analysis
    }
    
    # Categorize examples by format type
    for rule_name, rule_data in examples.items():
        if isinstance(rule_data, dict):
            # Determine format type
            if "detectors" in rule_data and "methods" in rule_data:
                format_type = "detector_method_format"
            elif "actions" in rule_data:
                format_type = "action_format"
            elif "presentMatcher" in str(rule_data):
                format_type = "matcher_format"
            else:
                format_type = "custom_format"
            
            if format_type not in guide["formats"]:
                guide["formats"][format_type] = []
            
            guide["formats"][format_type].append({
                "name": rule_name,
                "structure": list(rule_data.keys()) if isinstance(rule_data, dict) else [],
                "example": rule_data
            })
    
    return guide

def save_research_results(examples: Dict[str, Any], analysis: Dict[str, Any], guide: Dict[str, Any]):
    """Save research results to files."""
    
    os.makedirs("data/consent_o_matic_research", exist_ok=True)
    
    # Save examples
    with open("data/consent_o_matic_research/examples.json", 'w', encoding='utf-8') as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)
    
    # Save analysis
    with open("data/consent_o_matic_research/analysis.json", 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    # Save guide
    with open("data/consent_o_matic_research/format_guide.json", 'w', encoding='utf-8') as f:
        json.dump(guide, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Research results saved to:")
    print(f"   • data/consent_o_matic_research/examples.json")
    print(f"   • data/consent_o_matic_research/analysis.json") 
    print(f"   • data/consent_o_matic_research/format_guide.json")

def main():
    """Main research function."""
    
    print("🍪 Consent O Matic JSON Format Research")
    print("=" * 60)
    
    # Fetch examples
    examples = fetch_consent_o_matic_examples()
    
    if not examples:
        print("❌ No examples fetched. Check your internet connection.")
        return
    
    # Analyze formats
    analysis = analyze_json_formats(examples)
    
    # Create guide
    guide = create_format_guide(examples, analysis)
    
    # Save results
    save_research_results(examples, analysis, guide)
    
    print(f"\n🎉 Research Complete!")
    print(f"   • Analyzed {len(examples)} rule examples")
    print(f"   • Found {len(analysis['action_types'])} action types")
    print(f"   • Found {len(analysis['method_types'])} method types")
    print(f"   • Found {len(analysis['selector_patterns'])} selector patterns")

if __name__ == "__main__":
    main()
