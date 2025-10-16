"""
Main application for CMP Mapper - Auto-Detection for Cookie Consent Platforms

This script demonstrates the complete workflow for detecting consent banners
and generating Consent O Matic compatible rules.
"""

import os
import sys
from typing import List, Dict, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import version info
from version import print_version_info

from src.collectors import WebScraper, BannerCollector
from src.detectors import BannerDetector
from src.generators import RuleGenerator
from src.testers import TestRunner
from src.llm import LLMSelectorExtractor, LLMBannerAnalyzer
from src.models import PageData, BannerInfo, ConsentRule


def main():
    """Main application entry point."""
    print_version_info()
    print("=" * 70)
    
    # Example URLs to test
    test_urls = [
        "https://example.com",
        "https://httpbin.org",
        # Add more URLs as needed
    ]
    
    try:
        # Step 1: Collect page data
        print("\n1. Collecting page data...")
        page_data_list = collect_page_data(test_urls)
        
        if not page_data_list:
            print("No page data collected. Exiting.")
            return
        
        # Step 2: Detect consent banners
        print("\n2. Detecting consent banners...")
        banner_info_list = detect_banners(page_data_list)
        
        if not banner_info_list:
            print("No consent banners detected. Exiting.")
            return
        
        # Step 3: Generate rules
        print("\n3. Generating Consent O Matic rules...")
        rules = generate_rules(banner_info_list)
        
        # Step 4: Test rules (optional)
        print("\n4. Testing generated rules...")
        test_results = test_rules(rules, page_data_list)
        
        # Step 5: Generate summary
        print("\n5. Generating summary...")
        generate_summary(banner_info_list, rules, test_results)
        
        print("\nProcess completed successfully!")
        
    except Exception as e:
        print(f"Error in main process: {e}")
        import traceback
        traceback.print_exc()


def collect_page_data(urls: List[str]) -> List[PageData]:
    """Collect page data from URLs."""
    page_data_list = []
    
    with BannerCollector(headless=True) as collector:
        for url in urls:
            print(f"  Collecting from: {url}")
            try:
                page_data = collector.scraper.collect_page(url)
                if page_data and page_data.html_content:
                    page_data_list.append(page_data)
                    collector.scraper.save_page_data(page_data)
                    print(f"    [OK] Successfully collected data")
                else:
                    print(f"    [FAIL] Failed to collect data")
            except Exception as e:
                print(f"    [ERROR] Error: {e}")
    
    return page_data_list


def detect_banners(page_data_list: List[PageData]) -> List[BannerInfo]:
    """Detect consent banners in page data."""
    detector = BannerDetector()
    banner_info_list = []
    
    for page_data in page_data_list:
        print(f"  Analyzing: {page_data.url}")
        try:
            banner_info = detector.detect_banner(page_data)
            if banner_info:
                banner_info_list.append(banner_info)
                print(f"    [OK] Banner detected (confidence: {banner_info.detection_confidence:.2f})")
            else:
                print(f"    [NO BANNER] No banner detected")
        except Exception as e:
            print(f"    [ERROR] Error: {e}")
    
    return banner_info_list


def generate_rules(banner_info_list: List[BannerInfo]) -> List[ConsentRule]:
    """Generate Consent O Matic rules from banner info."""
    generator = RuleGenerator()
    rules = []
    
    for banner_info in banner_info_list:
        print(f"  Generating rule for: {banner_info.site}")
        try:
            rule = generator.generate_rule(banner_info)
            rules.append(rule)
            
            # Save individual rule
            filepath = generator.save_rule(rule)
            print(f"    [OK] Rule generated and saved to: {filepath}")
            
        except Exception as e:
            print(f"    [ERROR] Error generating rule: {e}")
    
    # Save rule summary
    if rules:
        summary = generator.create_rule_summary(rules)
        generator.save_rule_summary(summary)
        print(f"  [OK] Rule summary saved")
    
    return rules


def test_rules(rules: List[ConsentRule], page_data_list: List[PageData]) -> Dict[str, Any]:
    """Test generated rules."""
    test_results = {"total_tests": 0, "successful_tests": 0, "failed_tests": 0}
    
    if not rules:
        return test_results
    
    # Create test cases
    test_cases = []
    for i, rule in enumerate(rules):
        if i < len(page_data_list):
            test_cases.append({
                'banner_info': None,  # Would need to reconstruct from page_data
                'rule': rule,
                'test_url': page_data_list[i].url
            })
    
    # Run tests
    with TestRunner(headless=True) as runner:
        if test_cases:
            print(f"  Running {len(test_cases)} tests...")
            batch_results = runner.run_batch_tests(test_cases)
            
            test_results = {
                'total_tests': batch_results['total_tests'],
                'successful_tests': batch_results['successful_tests'],
                'failed_tests': batch_results['failed_tests'],
                'success_rate': batch_results['successful_tests'] / batch_results['total_tests'] if batch_results['total_tests'] > 0 else 0
            }
            
            # Save test results
            runner.save_test_results(batch_results)
            print(f"    [OK] Test results saved")
    
    return test_results


def generate_summary(banner_info_list: List[BannerInfo], rules: List[ConsentRule], 
                    test_results: Dict[str, Any]) -> None:
    """Generate and display summary."""
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    print(f"Pages analyzed: {len(banner_info_list)}")
    print(f"Banners detected: {len(banner_info_list)}")
    print(f"Rules generated: {len(rules)}")
    
    if banner_info_list:
        avg_confidence = sum(b.detection_confidence for b in banner_info_list) / len(banner_info_list)
        print(f"Average confidence: {avg_confidence:.2f}")
    
    if test_results.get('total_tests', 0) > 0:
        print(f"Tests run: {test_results['total_tests']}")
        print(f"Successful tests: {test_results['successful_tests']}")
        print(f"Failed tests: {test_results['failed_tests']}")
        print(f"Success rate: {test_results.get('success_rate', 0):.2%}")
    
    # Banner type distribution
    if banner_info_list:
        banner_types = {}
        for banner in banner_info_list:
            banner_type = banner.banner_type.value
            banner_types[banner_type] = banner_types.get(banner_type, 0) + 1
        
        print(f"\nBanner types detected:")
        for banner_type, count in banner_types.items():
            print(f"  {banner_type}: {count}")


def demo_llm_integration():
    """Demonstrate LLM integration features."""
    print("\n" + "=" * 60)
    print("LLM INTEGRATION DEMO")
    print("=" * 60)
    
    # Check if OpenAI API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("OpenAI API key not found. Set OPENAI_API_KEY environment variable to enable LLM features.")
        return
    
    # Example HTML content
    example_html = """
    <div id="cookie-consent-banner" class="modal cookie-banner">
        <div class="banner-content">
            <h3>Cookie Consent</h3>
            <p>We use cookies to improve your experience. Please choose your preferences.</p>
            <div class="button-group">
                <button id="accept-all" class="btn btn-primary">Accept All</button>
                <button id="reject-all" class="btn btn-secondary">Reject All</button>
                <button id="manage-cookies" class="btn btn-link">Manage Cookies</button>
            </div>
        </div>
    </div>
    """
    
    try:
        # LLM Selector Extraction
        print("\n1. LLM Selector Extraction:")
        llm_extractor = LLMSelectorExtractor(api_key=api_key)
        selectors = llm_extractor.extract_selectors(example_html)
        print(f"   Extracted selectors: {selectors}")
        
        # LLM Banner Analysis
        print("\n2. LLM Banner Analysis:")
        llm_analyzer = LLMBannerAnalyzer(api_key=api_key)
        analysis = llm_analyzer.analyze_banner(example_html)
        print(f"   Banner type: {analysis.get('banner_type', 'unknown')}")
        print(f"   Overall score: {analysis.get('overall_score', 0)}")
        
    except Exception as e:
        print(f"Error in LLM demo: {e}")


if __name__ == "__main__":
    # Run main application
    main()
    
    # Run LLM demo if API key is available
    demo_llm_integration()
