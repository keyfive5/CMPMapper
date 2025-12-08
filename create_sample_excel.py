#!/usr/bin/env python3
"""
Create a sample Excel file with all pharmacy website URLs for testing
"""

import pandas as pd

# All pharmacy websites organized by CMP group
pharmacy_sites = {
    'GoDaddy Group': [
        'https://pendalepharmacy.ca/',
        'https://northmedafixcompoundingpharmacy.ca/',
        'https://centerpharm.ca/',
        'https://riverviewpharmacy.ca/',
        'https://nadiasmedicalcentre.ca/',
        'https://www.midtowncompoundingpharmacy.ca/',
        'https://abundancespecialtyrx.com/',
        'https://rxottawa.ca/'
    ],
    'CookieYes Group': [
        'https://eramosapharmacy.ca/',
        'https://www.westmountmedicalpharmacy.ca/',
        'https://primecarepharmacy.ca/',
        'https://www.arkellmedical.ca/'
    ],
    'Other Sites': [
        'https://www.margispharmacy.com/',
        'https://blendrx.ca/',
        'https://www.fresenius-kabi.com/en-ca/'
    ]
}

# Flatten into a single list with group information
data = []
for group, urls in pharmacy_sites.items():
    for url in urls:
        data.append({
            'URL': url,
            'CMP Group': group,
            'Site Name': url.replace('https://', '').replace('http://', '').split('/')[0]
        })

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel('pharmacy_sites.xlsx', index=False)
print(f"Created pharmacy_sites.xlsx with {len(data)} URLs")
print(f"\nGroups:")
for group, urls in pharmacy_sites.items():
    print(f"  {group}: {len(urls)} sites")

