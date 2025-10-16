# Getting Started with CMP Mapper

This guide will help you get started with CMP Mapper for detecting and analyzing cookie consent banners.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Basic Usage](#basic-usage)
- [Configuration](#configuration)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8 or higher
- Chrome browser (for Selenium WebDriver)
- ChromeDriver (automatically managed by Selenium)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Optional: LLM Integration

For advanced features using AI, install OpenAI:

```bash
pip install openai
```

Then set your API key:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

## Quick Start

### 1. Basic Banner Detection

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.collectors import WebScraper
from src.detectors import BannerDetector

# Collect page data
with WebScraper(headless=True) as scraper:
    page_data = scraper.collect_page("https://example.com")

# Detect banner
detector = BannerDetector()
banner_info = detector.detect_banner(page_data)

if banner_info:
    print(f"Banner detected! Type: {banner_info.banner_type.value}")
    print(f"Confidence: {banner_info.detection_confidence:.2f}")
else:
    print("No banner detected")
```

### 2. Generate Consent O Matic Rule

```python
from src.generators import RuleGenerator

if banner_info:
    # Generate rule
    generator = RuleGenerator()
    rule = generator.generate_rule(banner_info)
    
    # Save rule
    filepath = generator.save_rule(rule)
    print(f"Rule saved to: {filepath}")
```

### 3. Test the Rule

```python
from src.testers import TestRunner

with TestRunner(headless=True) as runner:
    test_result = runner.run_comprehensive_test(
        banner_info, rule, "https://example.com"
    )
    
    print(f"Test result: {'Success' if test_result['overall_success'] else 'Failed'}")
```

## Basic Usage

### Collecting Data from Multiple Sites

```python
from src.collectors import BannerCollector

urls = [
    "https://example.com",
    "https://httpbin.org",
    "https://test.com"
]

with BannerCollector(headless=True) as collector:
    page_data_list = collector.collect_from_sites(urls)
    
    # Save collection summary
    collector.save_collection_summary(page_data_list)
```

### Batch Processing

```python
from src.detectors import BannerDetector
from src.generators import RuleGenerator

detector = BannerDetector()
generator = RuleGenerator()

banner_info_list = []
rules = []

for page_data in page_data_list:
    # Detect banner
    banner_info = detector.detect_banner(page_data)
    if banner_info:
        banner_info_list.append(banner_info)
        
        # Generate rule
        rule = generator.generate_rule(banner_info)
        rules.append(rule)

# Save all rules
if rules:
    summary = generator.create_rule_summary(rules)
    generator.save_rule_summary(summary)
```

### Using Predefined Site Collections

```python
from src.collectors import BannerCollector

with BannerCollector(headless=True) as collector:
    # Collect from pharmacy sites
    pharmacy_data = collector.collect_from_pharmacy_sites()
    
    # Collect from municipal sites
    municipal_data = collector.collect_from_municipal_sites()
```

## Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# OpenAI API Key for LLM features
OPENAI_API_KEY=your_openai_api_key_here

# Selenium WebDriver settings
CHROME_DRIVER_PATH=./drivers/chromedriver.exe
HEADLESS_BROWSER=true

# Testing settings
TEST_TIMEOUT=30
MAX_RETRIES=3
```

### Custom Configuration

```python
from src.collectors import WebScraper
from src.detectors import BannerDetector

# Custom scraper settings
scraper = WebScraper(headless=False, timeout=60)

# Custom detector settings
detector = BannerDetector()
```

## Examples

### Example 1: Complete Workflow

```python
def complete_workflow(url):
    """Complete workflow from URL to tested rule."""
    
    # Step 1: Collect page data
    with WebScraper(headless=True) as scraper:
        page_data = scraper.collect_page(url)
    
    # Step 2: Detect banner
    detector = BannerDetector()
    banner_info = detector.detect_banner(page_data)
    
    if not banner_info:
        print("No banner detected")
        return None
    
    # Step 3: Generate rule
    generator = RuleGenerator()
    rule = generator.generate_rule(banner_info)
    
    # Step 4: Test rule
    with TestRunner(headless=True) as runner:
        test_result = runner.run_comprehensive_test(banner_info, rule, url)
        
        if test_result['overall_success']:
            print("✓ Rule test passed")
            return rule
        else:
            print("✗ Rule test failed")
            return None

# Usage
rule = complete_workflow("https://example.com")
if rule:
    print(f"Successfully generated rule for: {rule.site}")
```

### Example 2: LLM-Enhanced Analysis

```python
import os
from src.llm import LLMSelectorExtractor, LLMBannerAnalyzer

# Check if API key is available
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    # LLM selector extraction
    llm_extractor = LLMSelectorExtractor(api_key=api_key)
    selectors = llm_extractor.extract_selectors(html_content, banner_info)
    
    # LLM banner analysis
    llm_analyzer = LLMBannerAnalyzer(api_key=api_key)
    analysis = llm_analyzer.analyze_banner(html_content, banner_info)
    
    print(f"LLM Analysis: {analysis.get('overall_score', 0)}/100")
else:
    print("OpenAI API key not found. LLM features disabled.")
```

### Example 3: Custom Banner Analysis

```python
def analyze_custom_banner(html_content, site_url):
    """Analyze a custom banner from HTML content."""
    
    # Detect banner from HTML
    detector = BannerDetector()
    banner_info = detector.detect_banner_from_html(html_content, site_url)
    
    if not banner_info:
        print("No banner detected in HTML")
        return
    
    print(f"Banner Analysis for {site_url}:")
    print(f"  Type: {banner_info.banner_type.value}")
    print(f"  Confidence: {banner_info.detection_confidence:.2f}")
    print(f"  Container: {banner_info.container_selector}")
    
    print("  Buttons:")
    for button in banner_info.buttons:
        print(f"    {button.button_type.value}: {button.text}")
    
    # Generate rule
    generator = RuleGenerator()
    rule = generator.generate_rule(banner_info)
    
    # Validate rule
    validation = generator.validate_rule(rule)
    print(f"  Rule valid: {validation['valid']}")
    print(f"  Rule score: {validation['score']:.2f}")
    
    return rule

# Usage with custom HTML
html_content = """
<div id="cookie-consent" class="modal">
    <h3>Cookie Consent</h3>
    <p>We use cookies to improve your experience.</p>
    <button id="accept">Accept All</button>
    <button id="reject">Reject All</button>
</div>
"""

rule = analyze_custom_banner(html_content, "custom-site.com")
```

### Example 4: Batch Processing with Error Handling

```python
def batch_process_urls(urls, output_dir="results"):
    """Process multiple URLs with comprehensive error handling."""
    
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    results = {
        'successful': [],
        'failed': [],
        'no_banner': []
    }
    
    detector = BannerDetector()
    generator = RuleGenerator()
    
    for i, url in enumerate(urls):
        print(f"Processing {i+1}/{len(urls)}: {url}")
        
        try:
            # Collect page data
            with WebScraper(headless=True) as scraper:
                page_data = scraper.collect_page(url)
            
            # Detect banner
            banner_info = detector.detect_banner(page_data)
            
            if not banner_info:
                results['no_banner'].append(url)
                print("  No banner detected")
                continue
            
            # Generate rule
            rule = generator.generate_rule(banner_info)
            
            # Save rule
            filename = f"rule_{i+1}_{rule.site}.json"
            filepath = os.path.join(output_dir, filename)
            generator.save_rule(rule, filepath)
            
            results['successful'].append({
                'url': url,
                'rule_file': filepath,
                'confidence': banner_info.detection_confidence
            })
            
            print(f"  ✓ Rule generated (confidence: {banner_info.detection_confidence:.2f})")
            
        except Exception as e:
            results['failed'].append({
                'url': url,
                'error': str(e)
            })
            print(f"  ✗ Error: {e}")
    
    # Save batch results
    import json
    results_file = os.path.join(output_dir, "batch_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nBatch processing complete:")
    print(f"  Successful: {len(results['successful'])}")
    print(f"  Failed: {len(results['failed'])}")
    print(f"  No banner: {len(results['no_banner'])}")
    
    return results

# Usage
urls = [
    "https://example.com",
    "https://httpbin.org",
    "https://test.com"
]

results = batch_process_urls(urls)
```

## Troubleshooting

### Common Issues

#### 1. ChromeDriver Issues

**Error:** `WebDriverException: 'chromedriver' executable needs to be in PATH`

**Solution:** Install ChromeDriver or let Selenium manage it:

```bash
# Let Selenium manage ChromeDriver (recommended)
pip install webdriver-manager

# Or install manually
# Download ChromeDriver from https://chromedriver.chromium.org/
# Add to PATH or set CHROME_DRIVER_PATH environment variable
```

#### 2. Import Errors

**Error:** `ModuleNotFoundError: No module named 'src'`

**Solution:** Add the src directory to your Python path:

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
```

#### 3. Permission Errors

**Error:** `PermissionError: [Errno 13] Permission denied`

**Solution:** Check file permissions and ensure you have write access to the output directories:

```python
import os
os.makedirs("data/examples", exist_ok=True)
os.makedirs("data/rules", exist_ok=True)
os.makedirs("data/test_results", exist_ok=True)
```

#### 4. LLM API Errors

**Error:** `openai.error.AuthenticationError`

**Solution:** Verify your OpenAI API key:

```python
import os
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("Please set OPENAI_API_KEY environment variable")
else:
    print("API key found")
```

### Debug Mode

Enable debug mode for more verbose output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or set specific logger levels
logging.getLogger('src.detectors').setLevel(logging.DEBUG)
logging.getLogger('src.collectors').setLevel(logging.DEBUG)
```

### Performance Issues

#### Slow Collection

- Use headless mode: `WebScraper(headless=True)`
- Reduce timeout: `WebScraper(timeout=15)`
- Limit content size: `html_content[:4000]`

#### Memory Issues

- Process URLs in smaller batches
- Close WebDriver instances properly using context managers
- Clear page data after processing

### Getting Help

1. Check the [API Reference](API_REFERENCE.md) for detailed documentation
2. Look at the [examples](examples/) directory for more usage examples
3. Review error messages and stack traces for specific issues
4. Ensure all dependencies are properly installed

### Support

For additional help:

1. Check the project repository for issues and discussions
2. Review the code comments and docstrings
3. Test with simple examples first before complex workflows
4. Use the built-in validation and testing features
