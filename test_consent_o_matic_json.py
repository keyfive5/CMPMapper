#!/usr/bin/env python3
"""
Test Consent O Matic JSON generator
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models import BannerInfo, BannerType, ConsentButton, ButtonType

def create_margis_pharmacy_json():
    """Create Consent O Matic JSON for Margis Pharmacy based on the correlation you found."""
    
    # Based on your discovery, create the proper JSON structure
    margis_rule = {
        "$schema": "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules.schema.json",
        "MargisPharmacy": {
            "detectors": {
                "presentMatcher": {
                    "type": "css",
                    "target": {
                        "selector": ".ideocookie-banner"  # From your CMP Mapper detection
                    }
                },
                "showingMatcher": {
                    "type": "css",
                    "target": {
                        "selector": ".ideocookie-banner"  # Same as presentMatcher
                    }
                }
            },
            "methods": {
                "HIDE_CMP": {
                    "action": {
                        "type": "hide",
                        "target": {
                            "selector": ".ideocookie-banner"  # Hide the banner
                        }
                    }
                },
                "DO_CONSENT": {
                    "action": {
                        "type": "click",
                        "target": {
                            "selector": "#ideocookie-selectall"  # Click Accept button
                        }
                    }
                },
                "SAVE_CONSENT": {
                    "action": {
                        "type": "click", 
                        "target": {
                            "selector": "#ideocookie-selectall"  # Same as DO_CONSENT
                        }
                    }
                }
            }
        }
    }
    
    # Save the rule
    os.makedirs("data/consent_o_matic_rules", exist_ok=True)
    filepath = "data/consent_o_matic_rules/margispharmacy_consent_o_matic.json"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(margis_rule, f, indent=2, ensure_ascii=False)
    
    print("✅ Generated Consent O Matic JSON for Margis Pharmacy:")
    print(json.dumps(margis_rule, indent=2))
    print(f"\n📁 Saved to: {filepath}")
    
    print(f"\n🎯 How to Use:")
    print(f"1. Copy the JSON content from: {filepath}")
    print(f"2. Open Consent O Matic extension")
    print(f"3. Go to 'GDPR Consent Rules Editor'")
    print(f"4. Click 'From Pasted JSON'")
    print(f"5. Paste the JSON and click 'Load'")
    print(f"6. Click 'Save Custom Rule'")
    print(f"7. Test by visiting: https://margispharmacy.com")
    
    return filepath

def create_beyondrx_json():
    """Create Consent O Matic JSON for BeyondRX based on the correlation."""
    
    beyondrx_rule = {
        "$schema": "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules.schema.json",
        "Beyondrx": {
            "detectors": {
                "presentMatcher": {
                    "type": "css",
                    "target": {
                        "selector": "#shopify-pc__banner, .shopify-pc__banner__dialog, [role='alertdialog']"
                    }
                },
                "showingMatcher": {
                    "type": "css",
                    "target": {
                        "selector": "#shopify-pc__banner, .shopify-pc__banner__dialog, [role='alertdialog']"
                    }
                }
            },
            "methods": {
                "HIDE_CMP": {
                    "action": {
                        "type": "hide",
                        "target": {
                            "selector": "#shopify-pc__banner, .shopify-pc__banner__dialog, [role='alertdialog']"
                        }
                    }
                },
                "DO_CONSENT": {
                    "action": {
                        "type": "click",
                        "target": {
                            "selector": "#shopify-pc__banner__btn-accept, .shopify-pc__banner__btn-accept"
                        }
                    }
                },
                "OPEN_OPTIONS": {
                    "action": {
                        "type": "click",
                        "target": {
                            "selector": "#shopify-pc__banner__btn-manage-prefs, .shopify-pc__banner__btn-manage-prefs"
                        }
                    }
                },
                "SAVE_CONSENT": {
                    "action": {
                        "type": "click",
                        "target": {
                            "selector": "#shopify-pc__banner__btn-accept, .shopify-pc__banner__btn-accept"
                        }
                    }
                }
            }
        }
    }
    
    # Save the rule
    filepath = "data/consent_o_matic_rules/beyondrx_consent_o_matic.json"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(beyondrx_rule, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Generated Consent O Matic JSON for BeyondRX:")
    print(f"📁 Saved to: {filepath}")
    
    return filepath

if __name__ == "__main__":
    print("🍪 Creating Consent O Matic JSON Rules")
    print("=" * 50)
    
    margis_file = create_margis_pharmacy_json()
    beyondrx_file = create_beyondrx_json()
    
    print(f"\n🎉 Success! Created Consent O Matic JSON rules:")
    print(f"   • Margis Pharmacy: {margis_file}")
    print(f"   • BeyondRX: {beyondrx_file}")
    print(f"\nThese JSON files can be directly imported into Consent O Matic!")
