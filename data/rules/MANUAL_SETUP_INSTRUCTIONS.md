# Manual Consent O Matic Setup for Margis Pharmacy

## Step 1: Add New Rule
1. Open Consent O Matic extension
2. Go to Settings -> Rules -> Custom Rules
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
