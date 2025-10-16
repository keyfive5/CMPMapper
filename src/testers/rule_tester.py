"""
Rule testing framework for validating generated Consent O Matic rules.
"""

import time
import os
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

from ..models import ConsentRule, TestResult


class RuleTester:
    """Tests generated rules against target websites."""
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        """
        Initialize the rule tester.
        
        Args:
            headless: Run browser in headless mode
            timeout: Timeout for page loads in seconds
        """
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self._setup_driver()
    
    def _setup_driver(self):
        """Set up the Chrome WebDriver."""
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        
        # Add options for better testing
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(self.timeout)
        except Exception as e:
            print(f"Warning: Could not initialize Chrome driver: {e}")
            self.driver = None
    
    def test_rule(self, rule: ConsentRule, test_url: str = None) -> TestResult:
        """
        Test a rule against a target website.
        
        Args:
            rule: ConsentRule object to test
            test_url: Optional test URL (defaults to rule.site)
            
        Returns:
            TestResult object with test outcomes
        """
        if not self.driver:
            return TestResult(
                rule=rule,
                success=False,
                error_message="WebDriver not available",
                test_duration=0.0
            )
        
        start_time = time.time()
        test_url = test_url or f"https://{rule.site}"
        
        try:
            # Load the page
            self.driver.get(test_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Take initial screenshot
            initial_screenshot = self._take_screenshot(f"initial_{rule.site}")
            
            # Test banner detection
            banner_detected = self._test_banner_detection(rule)
            
            # Test button interactions
            button_results = self._test_button_interactions(rule)
            
            # Test banner hiding
            banner_hidden = self._test_banner_hiding(rule)
            
            # Take final screenshot
            final_screenshot = self._take_screenshot(f"final_{rule.site}")
            
            # Determine overall success
            success = banner_detected and banner_hidden and any(button_results.values())
            
            # Calculate test duration
            test_duration = time.time() - start_time
            
            # Create test result
            result = TestResult(
                rule=rule,
                success=success,
                test_duration=test_duration,
                screenshots=[initial_screenshot, final_screenshot] if initial_screenshot and final_screenshot else [],
                logs=self._get_test_logs()
            )
            
            # Add detailed results to metadata
            result.rule.metadata.update({
                'test_results': {
                    'banner_detected': banner_detected,
                    'button_results': button_results,
                    'banner_hidden': banner_hidden,
                    'test_url': test_url,
                    'test_timestamp': datetime.now().isoformat()
                }
            })
            
            return result
            
        except Exception as e:
            test_duration = time.time() - start_time
            return TestResult(
                rule=rule,
                success=False,
                error_message=str(e),
                test_duration=test_duration,
                logs=self._get_test_logs()
            )
    
    def _test_banner_detection(self, rule: ConsentRule) -> bool:
        """Test if the banner can be detected using the rule's selectors."""
        try:
            banner_selector = rule.selectors.get('banner', '')
            if not banner_selector:
                return False
            
            # Wait for banner to appear
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, banner_selector))
            )
            
            return True
            
        except TimeoutException:
            return False
        except Exception:
            return False
    
    def _test_button_interactions(self, rule: ConsentRule) -> Dict[str, bool]:
        """Test button interactions."""
        results = {}
        
        # Test each button type
        button_types = ['acceptButton', 'rejectButton', 'manageButton', 'closeButton']
        
        for button_type in button_types:
            if button_type in rule.selectors:
                try:
                    selector = rule.selectors[button_type]
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if button and button.is_displayed():
                        # Try to click the button
                        self.driver.execute_script("arguments[0].click();", button)
                        results[button_type] = True
                    else:
                        results[button_type] = False
                        
                except (NoSuchElementException, WebDriverException):
                    results[button_type] = False
        
        return results
    
    def _test_banner_hiding(self, rule: ConsentRule) -> bool:
        """Test if the banner can be hidden."""
        try:
            banner_selector = rule.selectors.get('banner', '')
            if not banner_selector:
                return False
            
            # Find the banner element
            banner = self.driver.find_element(By.CSS_SELECTOR, banner_selector)
            
            # Hide the banner using JavaScript
            self.driver.execute_script("arguments[0].style.display = 'none';", banner)
            
            # Check if banner is hidden
            return not banner.is_displayed()
            
        except Exception:
            return False
    
    def _take_screenshot(self, filename: str) -> Optional[str]:
        """Take a screenshot of the current page."""
        try:
            os.makedirs("data/test_results/screenshots", exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            full_filename = f"{filename}_{timestamp}.png"
            filepath = f"data/test_results/screenshots/{full_filename}"
            
            self.driver.save_screenshot(filepath)
            return filepath
            
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return None
    
    def _get_test_logs(self) -> List[str]:
        """Get browser logs for debugging."""
        try:
            logs = self.driver.get_log('browser')
            return [log['message'] for log in logs]
        except Exception:
            return []
    
    def test_multiple_rules(self, rules: List[ConsentRule], test_urls: List[str] = None) -> List[TestResult]:
        """
        Test multiple rules.
        
        Args:
            rules: List of ConsentRule objects
            test_urls: Optional list of test URLs
            
        Returns:
            List of TestResult objects
        """
        results = []
        
        for i, rule in enumerate(rules):
            test_url = test_urls[i] if test_urls and i < len(test_urls) else None
            result = self.test_rule(rule, test_url)
            results.append(result)
        
        return results
    
    def validate_rule_selectors(self, rule: ConsentRule, test_url: str = None) -> Dict[str, bool]:
        """
        Validate that rule selectors work on the target page.
        
        Args:
            rule: ConsentRule object
            test_url: Optional test URL
            
        Returns:
            Dictionary of selector validation results
        """
        if not self.driver:
            return {}
        
        validation_results = {}
        test_url = test_url or f"https://{rule.site}"
        
        try:
            self.driver.get(test_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Test each selector
            for selector_name, selector in rule.selectors.items():
                try:
                    if isinstance(selector, list):
                        # Test list of selectors
                        found = False
                        for s in selector:
                            try:
                                self.driver.find_element(By.CSS_SELECTOR, s)
                                found = True
                                break
                            except NoSuchElementException:
                                continue
                        validation_results[selector_name] = found
                    else:
                        # Test single selector
                        self.driver.find_element(By.CSS_SELECTOR, selector)
                        validation_results[selector_name] = True
                        
                except NoSuchElementException:
                    validation_results[selector_name] = False
                except Exception:
                    validation_results[selector_name] = False
            
        except Exception as e:
            print(f"Error validating selectors: {e}")
            return {}
        
        return validation_results
    
    def generate_test_report(self, results: List[TestResult]) -> Dict[str, Any]:
        """
        Generate a test report from test results.
        
        Args:
            results: List of TestResult objects
            
        Returns:
            Test report dictionary
        """
        report = {
            'total_tests': len(results),
            'successful_tests': sum(1 for r in results if r.success),
            'failed_tests': sum(1 for r in results if not r.success),
            'success_rate': 0.0,
            'average_duration': 0.0,
            'test_details': [],
            'generated_at': datetime.now().isoformat()
        }
        
        if results:
            report['success_rate'] = report['successful_tests'] / report['total_tests']
            report['average_duration'] = sum(r.test_duration for r in results) / len(results)
        
        for result in results:
            test_detail = {
                'site': result.rule.site,
                'success': result.success,
                'duration': result.test_duration,
                'error': result.error_message,
                'screenshots': result.screenshots,
                'metadata': result.rule.metadata
            }
            report['test_details'].append(test_detail)
        
        return report
    
    def save_test_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """
        Save test report to a JSON file.
        
        Args:
            report: Test report dictionary
            filename: Optional filename
            
        Returns:
            Path to saved file
        """
        try:
            import json
            
            os.makedirs("data/test_results", exist_ok=True)
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"test_report_{timestamp}.json"
            
            if not filename.endswith('.json'):
                filename += '.json'
            
            filepath = f"data/test_results/{filename}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"Test report saved to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error saving test report: {e}")
            return ""
    
    def close(self):
        """Close the web driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
