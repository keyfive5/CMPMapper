# 🧪 CMP Mapper Testing Guide

## 🚀 Quick Start Testing

### Option 1: Interactive Testing Interface (Recommended)
```bash
python test_cmp_mapper.py
```

This launches an interactive menu where you can:
- Test single URLs
- Test multiple URLs in batch
- View recent generated rules
- Get detailed results with confidence scores

### Option 2: Direct Python Testing
```bash
python test_real_sites.py
```

This runs predefined tests on pharmacy websites.

### Option 3: Main Application
```bash
python main.py
```

This runs the full application with example URLs.

## 🎯 Testing Workflow

### 1. **Single URL Test**
Perfect for testing one website at a time:
```
Enter URL to test: https://www.margispharmacy.com/
```

**Expected Output:**
```
🎉 BANNER DETECTED!
   📋 Type: modal
   🎯 Confidence: 1.00
   📦 Container: #PAGE_L7BJVDNL9Z, .homeTop.ideocookie-widget__open
   🔘 Buttons: 43
```

### 2. **Batch Testing**
Test multiple URLs at once:
- Use default pharmacy URLs (recommended for first test)
- Or enter your own comma-separated URLs

### 3. **View Results**
- Generated rules are saved in `data/rules/`
- Each rule includes confidence scores and metadata
- Rules are compatible with Consent O Matic

## 📊 Understanding Results

### Confidence Scores
- **0.8-1.0**: High confidence - Banner clearly detected
- **0.6-0.8**: Medium confidence - Banner likely detected
- **0.4-0.6**: Low confidence - Possible banner
- **<0.4**: Very low confidence - Unlikely to be a banner

### Banner Types
- **modal**: Popup/overlay banner
- **bottom_bar**: Fixed banner at bottom of page
- **top_bar**: Fixed banner at top of page
- **inline**: Banner within page content

### Button Types
- **accept**: Accept/Agree buttons
- **reject**: Reject/Decline buttons
- **manage**: Manage preferences buttons
- **close**: Close/Dismiss buttons

## 🔧 Troubleshooting

### No Banner Detected
If a site shows "No banner detected" but you know it has one:

1. **Check for consent keywords**: The analyzer will show found keywords
2. **Manual inspection**: Look for cookie-related elements in browser dev tools
3. **Pattern matching**: Check if the banner uses uncommon class names

### Low Confidence Scores
- Banners with unusual structures may get lower scores
- Complex nested elements can confuse detection
- Dynamic content loading may affect detection

### Common Issues
- **Timeout errors**: Increase timeout in WebScraper
- **JavaScript-heavy sites**: Some banners load dynamically
- **Anti-bot measures**: Some sites block automated tools

## 📁 Generated Files

### Rules Directory: `data/rules/`
```
test_rule_20250116_191500.json
batch_rule_1_20250116_191500.json
batch_rule_2_20250116_191500.json
```

### Page Data Directory: `data/examples/`
```
pharmacy_test_1.json
pharmacy_test_2.json
pharmacy_test_3.json
```

## 🎯 Test URLs

### Known Working Sites
- ✅ `https://www.margispharmacy.com/` (ideocookie-widget)
- ✅ `https://midtowncompoundingpharmacy.ca/` (widget-cookie-banner)
- ❓ `https://beyondrx.ca/` (complex consent patterns)

### Additional Test Sites
Try these for more testing:
- `https://www.cnn.com/`
- `https://www.bbc.com/`
- `https://www.theguardian.com/`
- `https://www.reddit.com/`

## 🔍 Debug Mode

For detailed debugging, modify the test files:
```python
# In test_cmp_mapper.py, add:
with WebScraper(headless=False, timeout=60) as scraper:  # headless=False to see browser
```

## 📈 Success Metrics

### Good Results
- **Success Rate**: >50% for general websites
- **Confidence**: >0.6 for reliable detections
- **Button Detection**: At least Accept button found
- **Rule Generation**: Valid JSON rules created

### Performance
- **Detection Time**: 10-30 seconds per site
- **Memory Usage**: ~100-200MB per test
- **Browser Requirements**: Chrome/Chromium with Selenium

## 🆘 Getting Help

### Check Version
```bash
python -c "from version import print_version_info; print_version_info()"
```

### View Recent Updates
The version info shows latest changes and improvements.

### Log Files
Check console output for detailed error messages and debugging info.

---

## 🎉 Success Examples

### Margis Pharmacy
```
🎉 BANNER DETECTED!
   📋 Type: modal
   🎯 Confidence: 1.00
   📦 Container: #PAGE_L7BJVDNL9Z, .homeTop.ideocookie-widget__open
   🔘 Buttons: 43
```

### Midtown Compounding Pharmacy
```
🎉 BANNER DETECTED!
   📋 Type: modal
   🎯 Confidence: 0.65
   📦 Container: .widget.widget-cookie-banner.widget-cookie-banner-cookie-1
   🔘 Buttons: 1
```

These examples show the CMP Mapper successfully detecting real-world consent banners and generating working Consent O Matic rules!
