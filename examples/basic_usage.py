"""
Basic usage examples for CMP Mapper.

This file demonstrates how to use the CMP Mapper components
for detecting consent banners and generating rules.
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.collectors import WebScraper, BannerCollector
from src.detectors import BannerDetector
from src.generators import RuleGenerator
from src.testers import TestRunner
from src.models import PageData, BannerInfo, ConsentRule


def example_1_basic_detection():
    """Example 1: Basic banner detection from a single URL."""
    print("Example 1: Basic Banner Detection")
    print("-" * 40)
    
    url = "https://example.com"
    
    # Collect page data
    with WebScraper(headless=True) as scraper:
        page_data = scraper.collect_page(url)
        print(f"Collected data from: {page_data.url}")
    
    # Detect banner
    detector = BannerDetector()
    banner_info = detector.detect_banner(page_data)
    
    if banner_info:
        print(f"Banner detected!")
        print(f"  Type: {banner_info.banner_type.value}")
        print(f"  Confidence: {banner_info.detection_confidence:.2f}")
        print(f"  Buttons: {len(banner_info.buttons)}")
        print(f"  Container: {banner_info.container_selector}")
    else:
        print("No banner detected")


def example_2_batch_collection():
    """Example 2: Batch collection from multiple URLs."""
    print("\nExample 2: Batch Collection")
    print("-" * 40)
    
    urls = [
        "https://example.com",
        "https://httpbin.org",
        # Add more URLs as needed
    ]
    
    with BannerCollector(headless=True) as collector:
        page_data_list = collector.collect_from_sites(urls)
        
        print(f"Collected data from {len(page_data_list)} sites")
        
        # Save collection summary
        collector.save_collection_summary(page_data_list)


def example_3_rule_generation():
    """Example 3: Generate Consent O Matic rules."""
    print("\nExample 3: Rule Generation")
    print("-" * 40)
    
    # Mock banner info for demonstration
    banner_info = BannerInfo(
        site="example.com",
        banner_type="modal",
        container_selector="#cookie-banner",
        buttons=[],
        html_content="<div id='cookie-banner'>...</div>",
        detection_confidence=0.85
    )
    
    # Generate rule
    generator = RuleGenerator()
    rule = generator.generate_rule(banner_info)
    
    print(f"Generated rule for: {rule.site}")
    print(f"  Selectors: {rule.selectors}")
    print(f"  Actions: {rule.actions}")
    
    # Save rule
    filepath = generator.save_rule(rule)
    print(f"  Saved to: {filepath}")


def example_4_comprehensive_workflow():
    """Example 4: Complete workflow from URL to tested rule."""
    print("\nExample 4: Comprehensive Workflow")
    print("-" * 40)
    
    url = "https://example.com"
    
    # Step 1: Collect page data
    print("Step 1: Collecting page data...")
    with WebScraper(headless=True) as scraper:
        page_data = scraper.collect_page(url)
    
    # Step 2: Detect banner
    print("Step 2: Detecting banner...")
    detector = BannerDetector()
    banner_info = detector.detect_banner(page_data)
    
    if not banner_info:
        print("No banner detected. Stopping workflow.")
        return
    
    # Step 3: Generate rule
    print("Step 3: Generating rule...")
    generator = RuleGenerator()
    rule = generator.generate_rule(banner_info)
    
    # Step 4: Test rule
    print("Step 4: Testing rule...")
    with TestRunner(headless=True) as runner:
        test_result = runner.run_comprehensive_test(banner_info, rule, url)
        
        print(f"Test result: {'Success' if test_result['overall_success'] else 'Failed'}")
        if test_result.get('banner_validation'):
            print(f"Banner validation: {test_result['banner_validation']['overall_success']}")
        if test_result.get('rule_validation'):
            print(f"Rule validation: {test_result['rule_validation']['overall_success']}")
    
    print("Workflow completed!")


def example_5_custom_banner_analysis():
    """Example 5: Custom banner analysis with detailed inspection."""
    print("\nExample 5: Custom Banner Analysis")
    print("-" * 40)
    
    # Example HTML content
    html_content = """
    <div id="cookie-consent-modal" class="modal-overlay">
        <div class="cookie-banner">
            <h3>Cookie Consent</h3>
            <p>We use cookies to improve your experience.</p>
            <div class="buttons">
                <button id="accept-btn" class="btn-accept">Accept All</button>
                <button id="reject-btn" class="btn-reject">Reject All</button>
                <button id="manage-btn" class="btn-manage">Manage Preferences</button>
            </div>
        </div>
    </div>
    """
    
    # Detect banner from HTML
    detector = BannerDetector()
    banner_info = detector.detect_banner_from_html(html_content, "example.com")
    
    if banner_info:
        print(f"Banner detected:")
        print(f"  Type: {banner_info.banner_type.value}")
        print(f"  Confidence: {banner_info.detection_confidence:.2f}")
        print(f"  Container: {banner_info.container_selector}")
        
        print(f"  Buttons:")
        for button in banner_info.buttons:
            print(f"    {button.button_type.value}: {button.text} ({button.selector})")
        
        # Generate and save rule
        generator = RuleGenerator()
        rule = generator.generate_rule(banner_info)
        filepath = generator.save_rule(rule)
        print(f"  Rule saved to: {filepath}")
    else:
        print("No banner detected in HTML content")


def example_6_pharmacy_sites():
    """Example 6: Analyze pharmacy sites for consent banners."""
    print("\nExample 6: Pharmacy Sites Analysis")
    print("-" * 40)
    
    with BannerCollector(headless=True) as collector:
        # Collect from pharmacy sites
        page_data_list = collector.collect_from_pharmacy_sites()
        
        print(f"Collected data from {len(page_data_list)} pharmacy sites")
        
        # Detect banners
        detector = BannerDetector()
        banner_info_list = []
        
        for page_data in page_data_list:
            banner_info = detector.detect_banner(page_data)
            if banner_info:
                banner_info_list.append(banner_info)
                print(f"  Banner found on: {banner_info.site}")
        
        # Generate rules for all detected banners
        if banner_info_list:
            generator = RuleGenerator()
            rules = generator.generate_multiple_rules(banner_info_list)
            
            # Save rules
            saved_files = generator.save_rules_batch(rules, "pharmacy_sites")
            print(f"  Generated {len(rules)} rules")
            print(f"  Saved to {len(saved_files)} files")


def example_7_municipal_sites():
    """Example 7: Analyze municipal/government sites for consent banners."""
    print("\nExample 7: Municipal Sites Analysis")
    print("-" * 40)
    
    with BannerCollector(headless=True) as collector:
        # Collect from municipal sites
        page_data_list = collector.collect_from_municipal_sites()
        
        print(f"Collected data from {len(page_data_list)} municipal sites")
        
        # Detect banners and generate rules
        detector = BannerDetector()
        generator = RuleGenerator()
        
        successful_rules = 0
        
        for page_data in page_data_list:
            banner_info = detector.detect_banner(page_data)
            if banner_info:
                rule = generator.generate_rule(banner_info)
                filepath = generator.save_rule(rule)
                successful_rules += 1
                print(f"  Rule generated for: {rule.site}")
        
        print(f"  Successfully generated {successful_rules} rules")


def run_all_examples():
    """Run all examples."""
    print("CMP Mapper - Usage Examples")
    print("=" * 50)
    
    try:
        example_1_basic_detection()
        example_2_batch_collection()
        example_3_rule_generation()
        example_4_comprehensive_workflow()
        example_5_custom_banner_analysis()
        example_6_pharmacy_sites()
        example_7_municipal_sites()
        
        print("\n" + "=" * 50)
        print("All examples completed!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
