# CMP Mapper - Auto-Detection for Cookie Consent Platforms

A prototype module for detecting new or custom cookie consent platforms (CMPs) and automatically generating rule templates for Consent O Matic.

## Features

- **Data Collection**: Gather HTML/JS from pharmacy and municipal sites with consent banners
- **Feature Extraction**: Extract key banner features (HTML structure, button labels, DOM placement)
- **Auto-Detection**: Pattern recognition for consent-related elements
- **Rule Generation**: Auto-generate Consent O Matic compatible JSON rules
- **Testing Framework**: Validate generated rules against target sites
- **LLM Integration**: Use AI to extract selectors and improve detection

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

## Contributing

1. Add new example pages to `data/examples/`
2. Improve detection patterns in `src/detectors/`
3. Test generated rules with `src/testers/`
4. Document findings in `docs/`

## License

MIT License
