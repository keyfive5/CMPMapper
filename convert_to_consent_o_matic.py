#!/usr/bin/env python3
"""
Convert CMP Mapper generated rules to Consent O Matic format.
"""

import json
import os
from datetime import datetime

def convert_to_consent_o_matic(input_file, output_file=None):
    """Convert CMP Mapper rule to Consent O Matic format."""
    
    # Read the CMP Mapper rule
    with open(input_file, 'r') as f:
        cmp_rule = json.load(f)
    
    # Extract the most specific accept button selector
    accept_selectors = cmp_rule['selectors']['acceptButton'].split(', ')
    
    # Find the most specific selector (longest one)
    most_specific_accept = max(accept_selectors, key=len)
    
    # Create Consent O Matic format
    consent_o_matic_rule = {
        "domain": cmp_rule['site'],
        "rules": [
            {
                "selector": cmp_rule['selectors']['banner'].split(', ')[0],  # Use first banner selector
                "action": "hide"
            },
            {
                "selector": most_specific_accept,
                "action": "click"
            }
        ],
        "metadata": {
            "created_by": "CMP Mapper",
            "created_at": datetime.now().isoformat(),
            "original_confidence": cmp_rule['metadata']['confidence_score'],
            "banner_type": cmp_rule['metadata']['banner_type']
        }
    }
    
    # Generate output filename if not provided
    if not output_file:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_consent_o_matic.json"
    
    # Write the converted rule
    with open(output_file, 'w') as f:
        json.dump(consent_o_matic_rule, f, indent=2)
    
    print(f"✅ Converted rule saved to: {output_file}")
    print(f"🎯 Banner selector: {consent_o_matic_rule['rules'][0]['selector']}")
    print(f"🔘 Accept button selector: {consent_o_matic_rule['rules'][1]['selector']}")
    
    return output_file

def main():
    """Main function to convert rules."""
    print("🔄 CMP Mapper to Consent O Matic Converter")
    print("=" * 50)
    
    # Find all rule files
    rules_dir = "data/rules"
    if not os.path.exists(rules_dir):
        print("❌ No rules directory found")
        return
    
    rule_files = [f for f in os.listdir(rules_dir) if f.endswith('.json')]
    
    if not rule_files:
        print("❌ No rule files found")
        return
    
    print(f"📁 Found {len(rule_files)} rule files:")
    for i, file in enumerate(rule_files, 1):
        print(f"  {i}. {file}")
    
    # Convert all rules
    converted_files = []
    for rule_file in rule_files:
        input_path = os.path.join(rules_dir, rule_file)
        print(f"\n🔄 Converting: {rule_file}")
        try:
            output_file = convert_to_consent_o_matic(input_path)
            converted_files.append(output_file)
        except Exception as e:
            print(f"❌ Error converting {rule_file}: {e}")
    
    print(f"\n🎉 Conversion complete! {len(converted_files)} files converted.")
    print("\n📋 Next steps:")
    print("1. Copy the converted JSON files to Consent O Matic")
    print("2. Import them in Consent O Matic settings")
    print("3. Test on the target website")

if __name__ == '__main__':
    main()
