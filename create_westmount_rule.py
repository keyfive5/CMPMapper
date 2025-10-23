#!/usr/bin/env python3
"""
Create Consent O Matic rule for Westmount Medical Pharmacy
"""

import json
from datetime import datetime

def create_westmount_consent_o_matic_rule():
    """Create Consent O Matic JSON rule for Westmount Medical Pharmacy."""
    
    # Based on the detection results, create the rule
    rule = {
        "$schema": "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules.schema.json",
        "WestmountMedicalPharmacy": {
            "detectors": {
                "presentMatcher": {
                    "type": "css",
                    "target": {
                        "selector": ".cky-modal"
                    }
                },
                "showingMatcher": {
                    "type": "css",
                    "target": {
                        "selector": ".cky-modal"
                    }
                }
            },
            "methods": {
                "HIDE_CMP": {
                    "action": {
                        "type": "hide",
                        "target": {
                            "selector": ".cky-modal"
                        }
                    }
                },
                "DO_CONSENT": {
                    "action": {
                        "type": "click",
                        "target": {
                            "selector": ".cky-btn.cky-btn-accept, [data-cky-tag='detail-accept-button']"
                        }
                    }
                },
                "DO_REJECT": {
                    "action": {
                        "type": "click",
                        "target": {
                            "selector": ".cky-btn.cky-btn-reject, [data-cky-tag='detail-reject-button']"
                        }
                    }
                },
                "OPEN_OPTIONS": {
                    "action": {
                        "type": "click",
                        "target": {
                            "selector": ".cky-show-desc-btn, [data-cky-tag='show-desc-button']"
                        }
                    }
                },
                "SAVE_CONSENT": {
                    "action": {
                        "type": "click",
                        "target": {
                            "selector": ".cky-btn.cky-btn-preferences, [data-cky-tag='detail-save-button']"
                        }
                    }
                }
            }
        }
    }
    
    return rule

def main():
    """Create and save the Consent O Matic rule."""
    
    print("🍪 Creating Consent O Matic Rule for Westmount Medical Pharmacy")
    print("=" * 70)
    
    # Create the rule
    rule = create_westmount_consent_o_matic_rule()
    
    # Save the rule
    import os
    os.makedirs("data/consent_o_matic_rules", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/consent_o_matic_rules/westmount_medical_pharmacy_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(rule, f, indent=2, ensure_ascii=False)
    
    print("✅ Consent O Matic JSON Rule Created!")
    print(f"📁 Saved to: {filename}")
    
    print("\n📋 Rule Summary:")
    print(f"   - Site: westmountmedicalpharmacy.ca")
    print(f"   - Banner: .cky-modal (CookieYes banner)")
    print(f"   - Accept Button: .cky-btn.cky-btn-accept")
    print(f"   - Reject Button: .cky-btn.cky-btn-reject")
    print(f"   - Manage Button: .cky-show-desc-btn")
    print(f"   - Save Button: .cky-btn.cky-btn-preferences")
    
    print(f"\n🎯 How to Use:")
    print(f"1. Copy the JSON content from: {filename}")
    print(f"2. Open Consent O Matic extension")
    print(f"3. Go to 'GDPR Consent Rules Editor'")
    print(f"4. Click 'From Pasted JSON'")
    print(f"5. Paste the JSON and click 'Load'")
    print(f"6. Click 'Save Custom Rule'")
    print(f"7. Test by visiting: https://www.westmountmedicalpharmacy.ca/")
    
    print(f"\n🔧 What This Rule Does:")
    print(f"   • Detects CookieYes banner (.cky-modal)")
    print(f"   • Hides the banner when present")
    print(f"   • Clicks 'Accept All' button for quick consent")
    print(f"   • Clicks 'Reject All' button to reject cookies")
    print(f"   • Opens cookie preferences for customization")
    print(f"   • Saves preferences when customized")
    
    # Show the JSON content
    print(f"\n📄 JSON Content:")
    print(json.dumps(rule, indent=2))
    
    return filename

if __name__ == "__main__":
    main()
