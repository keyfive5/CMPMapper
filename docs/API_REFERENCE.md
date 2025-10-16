# CMP Mapper API Reference

This document provides a comprehensive reference for the CMP Mapper API.

## Table of Contents

- [Models](#models)
- [Collectors](#collectors)
- [Detectors](#detectors)
- [Extractors](#extractors)
- [Generators](#generators)
- [Testers](#testers)
- [LLM Integration](#llm-integration)

## Models

### PageData

Represents complete page data collected from a website.

```python
from src.models import PageData

page_data = PageData(
    url="https://example.com",
    html_content="<html>...</html>",
    javascript_content=["script1.js", "script2.js"],
    css_content=["style1.css"],
    screenshot_path="/path/to/screenshot.png",
    collected_at="2023-12-01T10:00:00",
    metadata={"user_agent": "...", "viewport_size": {...}}
)
```

**Fields:**
- `url` (str): The URL of the page
- `html_content` (str): Full HTML content
- `javascript_content` (List[str]): List of JavaScript files/scripts
- `css_content` (List[str]): List of CSS files/styles
- `screenshot_path` (Optional[str]): Path to screenshot file
- `collected_at` (str): ISO timestamp of collection
- `metadata` (Dict[str, Any]): Additional metadata

### BannerInfo

Represents information about a detected consent banner.

```python
from src.models import BannerInfo, BannerType, ConsentButton, ButtonType

banner_info = BannerInfo(
    site="example.com",
    banner_type=BannerType.MODAL,
    container_selector="#cookie-banner",
    buttons=[
        ConsentButton(
            text="Accept All",
            button_type=ButtonType.ACCEPT,
            selector="#accept-btn",
            is_visible=True,
            attributes={"class": "btn-accept"}
        )
    ],
    overlay_selectors=[".modal-overlay"],
    html_content="<div id='cookie-banner'>...</div>",
    detection_confidence=0.85,
    additional_selectors={"close": ".close-btn"}
)
```

**Fields:**
- `site` (str): Site domain or URL
- `banner_type` (BannerType): Type of banner (MODAL, BOTTOM_BAR, etc.)
- `container_selector` (str): CSS selector for banner container
- `buttons` (List[ConsentButton]): List of detected buttons
- `overlay_selectors` (List[str]): Selectors for overlay elements
- `html_content` (str): HTML content of the banner
- `detection_confidence` (float): Confidence score (0-1)
- `additional_selectors` (Dict[str, str]): Additional selectors

### ConsentRule

Represents a Consent O Matic compatible rule.

```python
from src.models import ConsentRule

rule = ConsentRule(
    site="example.com",
    selectors={
        "banner": "#cookie-banner",
        "acceptButton": "#accept-btn",
        "rejectButton": "#reject-btn",
        "overlay": [".modal-overlay"]
    },
    actions=["clickRejectIfPossible", "hideBanner"],
    metadata={
        "generated_at": "2023-12-01T10:00:00",
        "confidence_score": 0.85,
        "banner_type": "modal"
    }
)
```

## Collectors

### WebScraper

Collects page data using Selenium WebDriver.

```python
from src.collectors import WebScraper

# Basic usage
with WebScraper(headless=True, timeout=30) as scraper:
    page_data = scraper.collect_page("https://example.com")
    scraper.save_page_data(page_data, "example_page.json")

# Advanced usage
scraper = WebScraper(headless=False, timeout=60)
page_data = scraper.collect_page("https://example.com", wait_for_banner=True)
scraper.close()
```

**Methods:**
- `collect_page(url, wait_for_banner=True)`: Collect page data
- `save_page_data(page_data, filename=None)`: Save page data to file
- `close()`: Close the web driver

### BannerCollector

Specialized collector for gathering consent banner data.

```python
from src.collectors import BannerCollector

with BannerCollector(headless=True) as collector:
    # Collect from specific URLs
    urls = ["https://example.com", "https://test.com"]
    page_data_list = collector.collect_from_sites(urls)
    
    # Collect from pharmacy sites
    pharmacy_data = collector.collect_from_pharmacy_sites()
    
    # Collect from municipal sites
    municipal_data = collector.collect_from_municipal_sites()
    
    # Save collection summary
    collector.save_collection_summary(page_data_list)
```

## Detectors

### BannerDetector

Main detector for consent banners using pattern recognition.

```python
from src.detectors import BannerDetector

detector = BannerDetector()

# Detect single banner
banner_info = detector.detect_banner(page_data)

# Detect multiple banners
banners = detector.detect_multiple_banners(page_data)

# Get detection summary
summary = detector.get_detection_summary(page_data)
```

**Methods:**
- `detect_banner(page_data)`: Detect consent banner in page data
- `detect_multiple_banners(page_data)`: Detect all banners on page
- `get_detection_summary(page_data)`: Get summary of detection results

### PatternMatcher

Advanced pattern matching for consent banner detection.

```python
from src.detectors import PatternMatcher

matcher = PatternMatcher()

# Match banner patterns
scores = matcher.match_banner_patterns(element)

# Match button patterns
button_type, confidence = matcher.match_button_patterns(button_element)

# Detect language
language = matcher.detect_language(banner_text)

# Calculate confidence
confidence = matcher.calculate_pattern_confidence(element)
```

## Extractors

### BannerExtractor

Extracts features from consent banners.

```python
from src.extractors import BannerExtractor

extractor = BannerExtractor()
banner_info = extractor.extract_banner_info(html_content, "example.com")
```

### ButtonExtractor

Extracts and analyzes consent buttons.

```python
from src.extractors import ButtonExtractor

extractor = ButtonExtractor()
buttons = extractor.extract_buttons_from_html(html_content, "#cookie-banner")

# Group buttons by type
grouped = extractor.group_buttons_by_type(buttons)

# Find primary buttons
primary = extractor.find_primary_buttons(buttons)

# Validate selectors
validated = extractor.validate_button_selectors(buttons, html_content)
```

### SelectorExtractor

Extracts and generates CSS selectors.

```python
from src.extractors import SelectorExtractor

extractor = SelectorExtractor()

# Extract selectors
selectors = extractor.extract_selectors(banner_info)

# Generate robust selectors
robust_selectors = extractor.generate_robust_selectors(html_content, banner_info)

# Validate selectors
validation = extractor.validate_selectors(selectors, html_content)

# Generate fallback selectors
fallbacks = extractor.generate_fallback_selectors(banner_info)
```

## Generators

### RuleGenerator

Generates Consent O Matic compatible rule templates.

```python
from src.generators import RuleGenerator

generator = RuleGenerator()

# Generate single rule
rule = generator.generate_rule(banner_info, "example.com")

# Generate multiple rules
rules = generator.generate_multiple_rules(banner_info_list)

# Save rule
filepath = generator.save_rule(rule, "custom_name.json")

# Save multiple rules
saved_files = generator.save_rules_batch(rules, "batch_name")

# Create rule summary
summary = generator.create_rule_summary(rules)
generator.save_rule_summary(summary)

# Validate rule
validation = generator.validate_rule(rule)

# Optimize rule
optimized = generator.optimize_rule(rule)
```

### TemplateBuilder

Builds rule templates based on banner information.

```python
from src.generators import TemplateBuilder

builder = TemplateBuilder()

# Build template
template = builder.build_template(banner_info)

# Build fallback template
fallback = builder.build_fallback_template(banner_info)

# Enhance template with patterns
enhanced = builder.enhance_template_with_patterns(template, banner_info)

# Validate template
validation = builder.validate_template(template)

# Get template variants
variants = builder.get_template_variants(banner_info)

# Compare templates
comparison = builder.compare_templates(templates)
```

### ConsentOMaticAdapter

Adapts generated rules to Consent O Matic format.

```python
from src.generators import ConsentOMaticAdapter

adapter = ConsentOMaticAdapter()

# Convert rule
consent_o_matic_rule = adapter.convert_to_consent_o_matic(rule)

# Validate format
validation = adapter.validate_consent_o_matic_format(rule)

# Create manifest
manifest = adapter.create_consent_o_matic_manifest(rules)

# Export in different formats
json_content = adapter.export_for_consent_o_matic(rules, 'json')
js_content = adapter.export_for_consent_o_matic(rules, 'js')
ts_content = adapter.export_for_consent_o_matic(rules, 'ts')

# Create rule template
template = adapter.create_rule_template('modal')

# Merge rules
merged = adapter.merge_rules(rules, 'highest_confidence')
```

## Testers

### RuleTester

Tests generated rules against target websites.

```python
from src.testers import RuleTester

with RuleTester(headless=True, timeout=30) as tester:
    # Test single rule
    test_result = tester.test_rule(rule, "https://example.com")
    
    # Test multiple rules
    results = tester.test_multiple_rules(rules, test_urls)
    
    # Validate selectors
    validation = tester.validate_rule_selectors(rule, "https://example.com")
    
    # Generate test report
    report = tester.generate_test_report(results)
    tester.save_test_report(report)
```

### BannerValidator

Validates consent banners and their interactions.

```python
from src.testers import BannerValidator

validator = BannerValidator(driver)

# Validate banner presence
present = validator.validate_banner_presence(banner_info)

# Validate button functionality
button_results = validator.validate_button_functionality(banner_info)

# Validate banner hiding
hidden = validator.validate_banner_hiding(banner_info)

# Validate overlay hiding
overlays_hidden = validator.validate_overlay_hiding(banner_info)

# Get banner state
state = validator.get_banner_state(banner_info)

# Simulate user interaction
success = validator.simulate_user_interaction(banner_info, 'reject')

# Measure performance
metrics = validator.measure_banner_performance(banner_info)
```

### TestRunner

Runs comprehensive tests for banner detection and rule validation.

```python
from src.testers import TestRunner

with TestRunner(headless=True, timeout=30) as runner:
    # Run comprehensive test
    result = runner.run_comprehensive_test(banner_info, rule, "https://example.com")
    
    # Run batch tests
    test_cases = [
        {'banner_info': banner1, 'rule': rule1, 'test_url': url1},
        {'banner_info': banner2, 'rule': rule2, 'test_url': url2}
    ]
    batch_results = runner.run_batch_tests(test_cases)
    
    # Save results
    runner.save_test_results(batch_results)
    
    # Load results
    loaded_results = runner.load_test_results("test_results.json")
    
    # Compare results
    comparison = runner.compare_test_results(results1, results2)
```

## LLM Integration

### LLMSelectorExtractor

Uses LLM to extract and improve CSS selectors.

```python
from src.llm import LLMSelectorExtractor

extractor = LLMSelectorExtractor(api_key="your-api-key")

# Extract selectors
selectors = extractor.extract_selectors(html_content, banner_info)

# Improve selectors
improved = extractor.improve_selectors(current_selectors, html_content)

# Analyze banner structure
analysis = extractor.analyze_banner_structure(html_content)

# Generate test scenarios
scenarios = extractor.generate_test_scenarios(banner_info)
```

### LLMBannerAnalyzer

Uses LLM to analyze consent banners and provide insights.

```python
from src.llm import LLMBannerAnalyzer

analyzer = LLMBannerAnalyzer(api_key="your-api-key")

# Analyze banner
analysis = analyzer.analyze_banner(html_content, banner_info)

# Compare banners
comparison = analyzer.compare_banners(banner1_info, banner2_info)

# Generate improvement suggestions
suggestions = analyzer.generate_improvement_suggestions(banner_info)
```

### PromptBuilder

Builds optimized prompts for LLM interactions.

```python
from src.llm import PromptBuilder

builder = PromptBuilder()

# Build prompts
selector_prompt = builder.build_selector_extraction_prompt(html_content, banner_info)
analysis_prompt = builder.build_banner_analysis_prompt(html_content, banner_info)
rule_prompt = builder.build_rule_generation_prompt(banner_info)
testing_prompt = builder.build_testing_prompt(banner_info)
comparison_prompt = builder.build_comparison_prompt(banner1_info, banner2_info)

# Build system prompts
system_prompt = builder.build_system_prompt('selector_extraction')

# Optimize prompt length
optimized = builder.optimize_prompt_length(prompt, max_tokens=4000)

# Validate prompt
validation = builder.validate_prompt(prompt)
```

## Error Handling

All components include comprehensive error handling:

```python
try:
    detector = BannerDetector()
    banner_info = detector.detect_banner(page_data)
except Exception as e:
    print(f"Error detecting banner: {e}")
    # Handle error appropriately
```

## Configuration

Set environment variables for configuration:

```bash
# OpenAI API Key for LLM features
export OPENAI_API_KEY="your-api-key-here"

# Selenium WebDriver settings
export CHROME_DRIVER_PATH="./drivers/chromedriver.exe"
export HEADLESS_BROWSER=true

# Testing settings
export TEST_TIMEOUT=30
export MAX_RETRIES=3
```

## Best Practices

1. **Use context managers** for WebDriver instances to ensure proper cleanup
2. **Handle exceptions** gracefully in production code
3. **Validate results** before using them in downstream processes
4. **Save intermediate results** for debugging and analysis
5. **Use appropriate timeouts** for different operations
6. **Test rules** before deploying to production
7. **Monitor confidence scores** and adjust detection patterns as needed
