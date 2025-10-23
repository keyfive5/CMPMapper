# 🍪 Consent O Matic Workflow Explained

## What is Consent O Matic?

Consent O Matic is a browser extension that automatically handles cookie consent banners on websites. It works by:

1. **Detecting** cookie banners on websites you visit
2. **Applying rules** to automatically click "Accept" or "Reject" buttons
3. **Hiding** the banners so they don't bother you

## How Your CMP Mapper Fits In

Your CMP Mapper is designed to **automatically generate rules** for Consent O Matic when it encounters **new or custom cookie banners** that aren't already in Consent O Matic's database.

## The Complete Workflow

### Step 1: CMP Mapper Detects New Banner
```
Website with unknown cookie banner → CMP Mapper analyzes → Generates JSON rule
```

### Step 2: Import Rule into Consent O Matic
1. Open Consent O Matic extension
2. Go to "GDPR Consent Rules Editor"
3. Click "From Pasted JSON"
4. Paste the JSON rule from CMP Mapper
5. Click "Load"

### Step 3: Configure the Rule
After loading JSON, you'll see the "GDPR Consent Rules Editor" interface:

#### Left Sidebar - Draggable Elements:
- **Matchers** (Blue/Purple): How to detect the banner
  - `Detector`: Main detection logic
  - `CssMatcher`: CSS selector matching
  - `UrlMatcher`: URL pattern matching
- **Actions** (Green/Yellow/Pink): What to do with the banner
  - `ClickAction`: Click buttons
  - `HideAction`: Hide the banner
  - `ConsentAction`: Handle consent

#### Main Area - Rule Configuration:
- **Detectors**: Drag matchers here to define how to find the banner
- **Methods**: Define what actions to take
  - `HIDE_CMP`: Hide the banner
  - `DO_CONSENT`: Auto-accept cookies
  - `SAVE_CONSENT`: Save preferences

### Step 4: Test the Rule
1. Click "Save Custom Rule" in the left menu
2. Give it a name (e.g., "MargisPharmacy")
3. The rule is now saved and will be applied automatically

### Step 5: Verify It Works
1. Visit the website with the cookie banner
2. Consent O Matic should automatically:
   - Detect the banner
   - Apply your rule
   - Hide the banner or click the appropriate buttons

## What Happens After Loading JSON?

When you paste JSON and click "Load":

1. **Consent O Matic parses the JSON** and creates a rule structure
2. **The editor interface appears** with your rule loaded
3. **You can modify the rule** by dragging elements around
4. **Click "Save Custom Rule"** to make it permanent
5. **The rule becomes active** and will work on future visits

## Why Rules Disappear on Refresh

- **Temporary rules** (loaded from JSON) are not saved until you click "Save Custom Rule"
- **Saved rules** persist and work automatically
- **Your CMP Mapper generates the initial JSON**, but you need to save it in Consent O Matic

## Testing Your Rules

1. **Save the rule** in Consent O Matic
2. **Visit the target website**
3. **Check if the banner is handled automatically**
4. **If not working**, go back to the editor and adjust the rule

## Your CMP Mapper's Role

Your prototype automates the **hardest part**: figuring out the right CSS selectors and button patterns for new cookie banners. Instead of manually creating rules, your tool:

1. **Analyzes the website** automatically
2. **Finds the banner elements** and buttons
3. **Generates the JSON rule** with the right selectors
4. **Provides instructions** on how to use it

This makes it much easier to add support for new cookie banners to Consent O Matic!

## Next Steps

1. **Test your CMP Mapper** on the three pharmacy websites
2. **Generate JSON rules** for each site
3. **Import them into Consent O Matic**
4. **Save and test** the rules
5. **Document the results** and any issues

The goal is to show that your tool can automatically detect new banners and generate working rules with minimal manual work!
