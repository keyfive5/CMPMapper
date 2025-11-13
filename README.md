# CMP Mapper - Auto-Detection for Cookie Consent Platforms

A prototype module for detecting new or custom cookie consent platforms (CMPs) and automatically generating rule templates for Consent O Matic.

## Features

- **Data Collection**: Gather HTML/JS from pharmacy and municipal sites with consent banners
- **Feature Extraction**: Extract key banner features (HTML structure, button labels, DOM placement)
- **Auto-Detection**: Pattern recognition for consent-related elements
- **Rule Generation**: Auto-generate Consent O Matic compatible JSON rules
- **Testing Framework**: Validate generated rules against target sites
- **LLM Integration**: Use AI to extract selectors and improve detection
- **Web Interface**: Beautiful, modern web UI for easy access
- **Excel/CSV Upload**: Upload files with URLs for batch testing
- **Rules Management**: View and manage all your Consent O Matic rules
- **Batch Testing**: Test multiple URLs against your rules simultaneously
- **Cloud Deployment**: Ready for deployment to Railway, Render, Vercel, and more

## Project Structure

```
CMPMapper/
├── src/
│   ├── collectors/          # Data collection utilities
│   ├── extractors/          # Feature extraction logic
│   ├── detectors/           # Auto-detection algorithms
│   ├── generators/          # Rule template generation
│   ├── testers/             # Testing framework
│   └── llm/                 # LLM integration
├── data/
│   ├── examples/            # Example HTML/JS files
│   ├── rules/               # Generated rule templates
│   └── test_results/        # Testing results
├── docs/                    # Documentation
└── tests/                   # Unit tests
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Quick Start

### Web Interface (Recommended)

1. **Start the web server:**
   ```bash
   python web_ui.py
   ```

2. **Open your browser:**
   Navigate to `http://127.0.0.1:5000`

3. **Features available:**
   - **Single URL Analysis**: Analyze individual websites
   - **Multiple URLs**: Analyze multiple websites at once
   - **HTML Analysis**: Paste HTML directly for analysis
   - **Excel/CSV Upload**: Upload files with URLs for batch testing
   - **Rules Manager**: View and manage your Consent O Matic rules
   - **Batch Testing**: Test URLs against your rules

### Excel/CSV Upload

1. Create an Excel or CSV file with URLs in the first column (or a column named "URL")
2. Use the "Upload Excel/CSV" tab to upload your file
3. The system will extract all URLs automatically
4. Use the extracted URLs for batch testing

### Batch Testing

1. Go to the "Batch Testing" tab
2. Enter URLs (one per line) or use the Excel/CSV upload feature
3. Select which rules to test against (or test against all rules)
4. Click "Start Batch Test" to see which rules match which websites

## Usage

### Basic Detection
```python
from src.detectors.banner_detector import BannerDetector
from src.collectors.web_scraper import WebScraper

# Collect page data
scraper = WebScraper()
page_data = scraper.collect_page("https://example.com")

# Detect consent banner
detector = BannerDetector()
banner_info = detector.detect_banner(page_data)

# Generate rule template
from src.generators.rule_generator import RuleGenerator
generator = RuleGenerator()
rule = generator.generate_rule(banner_info, "example.com")
```

### LLM-Assisted Detection
```python
from src.llm.selector_extractor import LLMSelectorExtractor

extractor = LLMSelectorExtractor()
selectors = extractor.extract_selectors(html_content)
```

## Deployment

CMP Mapper is ready for cloud deployment. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on deploying to:

- **Railway** (Recommended - Free tier available)
- **Render** (Free tier with limitations)
- **Vercel** (Serverless)
- **Heroku** (Paid)

### Quick Deploy to Railway

1. Sign up at [railway.app](https://railway.app)
2. Create a new project and connect your GitHub repository
3. Railway will automatically detect and deploy your app
4. Your app will be live at `https://your-app-name.railway.app`

## Project Status

This is a working prototype that has been tested with multiple CMP groups:
- OneTrust
- GoDaddy
- Shopify Privacy Center
- Custom pharmacy websites
- And more...

The system includes 5 groups of Consent O Matic rules that have been tested and validated.

## Contributing

1. Add new example pages to `data/examples/`
2. Improve detection patterns in `src/detectors/`
3. Test generated rules with `src/testers/`
4. Document findings in `docs/`
5. Add new Consent O Matic rules to `custom-consent-o-matic-rules/rules/`

## License

MIT License
