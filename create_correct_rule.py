#!/usr/bin/env python3
"""
Create the correct Consent O Matic rule for Margis Pharmacy.
"""

import json
from datetime import datetime

def create_correct_margis_rule():
    """Create the correct rule for Margis Pharmacy."""
    
    # The correct rule based on our analysis
    correct_rule = {
        "domain": "margispharmacy.com",
        "rules": [
            {
                "selector": "#PAGE_L7BJVDNL9Z",
                "action": "hide"
            },
            {
                "selector": "#ideocookie-selectall",
                "action": "click"
            }
        ],
        "metadata": {
            "created_by": "CMP Mapper - Corrected",
            "created_at": datetime.now().isoformat(),
            "confidence": "High - Tested with specific selectors",
            "banner_type": "modal",
            "notes": "Corrected accept button selector found through HTML analysis"
        }
    }
    
    # Save the correct rule
    with open('data/rules/margispharmacy_corrected_rule.json', 'w') as f:
        json.dump(correct_rule, f, indent=2)
    
    print("✅ Created corrected rule for Margis Pharmacy!")
    print(f"🎯 Banner selector: {correct_rule['rules'][0]['selector']}")
    print(f"🔘 Accept button selector: {correct_rule['rules'][1]['selector']}")
    
    return correct_rule

def create_manual_instructions():
    """Create manual instructions for Consent O Matic."""
    
    instructions = """
# 🎯 Manual Consent O Matic Setup for Margis Pharmacy

## Step 1: Add New Rule
1. Open Consent O Matic extension
2. Go to Settings → Rules → Custom Rules
3. Click "Add New Rule"

## Step 2: Configure Rule
- **Domain**: `margispharmacy.com`
- **Rule Name**: `Margis Pharmacy Cookie Banner`

## Step 3: Add Actions
Add these two actions:

### Action 1: Hide Banner
- **Action Type**: Hide Element
- **Selector**: `#PAGE_L7BJVDNL9Z`
- **Description**: Hide the cookie banner

### Action 2: Click Accept
- **Action Type**: Click Element
- **Selector**: `#ideocookie-selectall`
- **Description**: Click the "Accept All" button

## Step 4: Test
1. Visit https://margispharmacy.com
2. Check if the banner disappears automatically
3. If not, try these alternative selectors:

### Alternative Accept Button Selectors:
- `.ideocookie-button.ideocookie-button__primary`
- `.ideocookie-button__primary`
- `[id*='ideocookie']`

### Alternative Banner Selectors:
- `.ideocookie-widget`
- `[class*='ideocookie']`
- `[id*='PAGE_']`

## Troubleshooting
If the banner still doesn't disappear:
1. Check if selectors are correct using browser dev tools
2. Try the alternative selectors listed above
3. Make sure the rule is enabled for margispharmacy.com
"""
    
    with open('data/rules/MANUAL_SETUP_INSTRUCTIONS.md', 'w') as f:
        f.write(instructions)
    
    print("📋 Created manual setup instructions!")

if __name__ == '__main__':
    print("🔧 Creating Corrected Rules for Consent O Matic")
    print("=" * 50)
    
    # Create the correct rule
    rule = create_correct_margis_rule()
    
    # Create manual instructions
    create_manual_instructions()
    
    print("\n🎉 Setup Complete!")
    print("\n📁 Files created:")
    print("  - data/rules/margispharmacy_corrected_rule.json")
    print("  - data/rules/MANUAL_SETUP_INSTRUCTIONS.md")
    
    print("\n🚀 Next Steps:")
    print("1. Use the manual instructions to set up Consent O Matic")
    print("2. Test on https://margispharmacy.com")
    print("3. The banner should now disappear automatically!")
