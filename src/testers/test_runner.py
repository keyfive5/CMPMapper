"""
Test runner for executing comprehensive banner and rule tests.
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..models import BannerInfo, ConsentRule, TestResult
from .rule_tester import RuleTester
from .banner_validator import BannerValidator


class TestRunner:
    """Runs comprehensive tests for banner detection and rule validation."""
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        """
        Initialize the test runner.
        
        Args:
            headless: Run browser in headless mode
            timeout: Timeout for page loads in seconds
        """
        self.headless = headless
        self.timeout = timeout
        self.rule_tester = None
        self.banner_validator = None
    
    def __enter__(self):
        """Context manager entry."""
        self.rule_tester = RuleTester(headless=self.headless, timeout=self.timeout)
        self.banner_validator = BannerValidator(self.rule_tester.driver)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.rule_tester:
            self.rule_tester.close()
    
    def run_comprehensive_test(self, banner_info: BannerInfo, rule: ConsentRule, 
                             test_url: str = None) -> Dict[str, Any]:
        """
        Run comprehensive tests for banner detection and rule validation.
        
        Args:
            banner_info: BannerInfo object
            rule: ConsentRule object
            test_url: Optional test URL
            
        Returns:
            Comprehensive test results
        """
        if not self.rule_tester or not self.banner_validator:
            raise RuntimeError("TestRunner not properly initialized. Use with context manager.")
        
        test_results = {
            'banner_validation': {},
            'rule_validation': {},
            'performance_metrics': {},
            'overall_success': False,
            'test_timestamp': datetime.now().isoformat()
        }
        
        try:
            # Test banner presence and functionality
            test_results['banner_validation'] = self._test_banner_functionality(banner_info, test_url)
            
            # Test rule effectiveness
            test_results['rule_validation'] = self._test_rule_effectiveness(rule, test_url)
            
            # Measure performance
            test_results['performance_metrics'] = self.banner_validator.measure_banner_performance(banner_info)
            
            # Determine overall success
            banner_success = test_results['banner_validation'].get('overall_success', False)
            rule_success = test_results['rule_validation'].get('overall_success', False)
            test_results['overall_success'] = banner_success and rule_success
            
        except Exception as e:
            test_results['error'] = str(e)
            test_results['overall_success'] = False
        
        return test_results
    
    def _test_banner_functionality(self, banner_info: BannerInfo, test_url: str = None) -> Dict[str, Any]:
        """Test banner functionality."""
        results = {
            'banner_present': False,
            'buttons_functional': {},
            'banner_hideable': False,
            'overlays_hideable': False,
            'overall_success': False
        }
        
        try:
            # Test banner presence
            results['banner_present'] = self.banner_validator.validate_banner_presence(banner_info)
            
            # Test button functionality
            button_results = self.banner_validator.validate_button_functionality(banner_info)
            results['buttons_functional'] = {k.value: v for k, v in button_results.items()}
            
            # Test banner hiding
            results['banner_hideable'] = self.banner_validator.validate_banner_hiding(banner_info)
            
            # Test overlay hiding
            results['overlays_hideable'] = self.banner_validator.validate_overlay_hiding(banner_info)
            
            # Determine overall success
            results['overall_success'] = (
                results['banner_present'] and 
                results['banner_hideable'] and
                any(results['buttons_functional'].values())
            )
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def _test_rule_effectiveness(self, rule: ConsentRule, test_url: str = None) -> Dict[str, Any]:
        """Test rule effectiveness."""
        results = {
            'selector_validation': {},
            'action_validation': {},
            'overall_success': False
        }
        
        try:
            # Validate selectors
            selector_validation = self.rule_tester.validate_rule_selectors(rule, test_url)
            results['selector_validation'] = selector_validation
            
            # Validate rule effectiveness
            rule_validation = self.banner_validator.validate_rule_effectiveness(rule)
            results['action_validation'] = rule_validation
            
            # Determine overall success
            selector_success = any(selector_validation.values()) if selector_validation else False
            action_success = any(rule_validation.values()) if rule_validation else False
            results['overall_success'] = selector_success and action_success
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def run_batch_tests(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run batch tests for multiple banner/rule combinations.
        
        Args:
            test_cases: List of test case dictionaries with 'banner_info', 'rule', and optional 'test_url'
            
        Returns:
            Batch test results
        """
        batch_results = {
            'total_tests': len(test_cases),
            'successful_tests': 0,
            'failed_tests': 0,
            'test_details': [],
            'summary': {},
            'generated_at': datetime.now().isoformat()
        }
        
        for i, test_case in enumerate(test_cases):
            try:
                banner_info = test_case['banner_info']
                rule = test_case['rule']
                test_url = test_case.get('test_url')
                
                print(f"Running test {i+1}/{len(test_cases)}: {rule.site}")
                
                # Run comprehensive test
                test_result = self.run_comprehensive_test(banner_info, rule, test_url)
                
                # Add test case info
                test_result['test_case'] = {
                    'index': i,
                    'site': rule.site,
                    'banner_type': banner_info.banner_type.value,
                    'confidence': banner_info.detection_confidence
                }
                
                batch_results['test_details'].append(test_result)
                
                # Update counters
                if test_result['overall_success']:
                    batch_results['successful_tests'] += 1
                else:
                    batch_results['failed_tests'] += 1
                
            except Exception as e:
                error_result = {
                    'test_case': {'index': i, 'site': test_case.get('rule', {}).get('site', 'unknown')},
                    'error': str(e),
                    'overall_success': False
                }
                batch_results['test_details'].append(error_result)
                batch_results['failed_tests'] += 1
        
        # Generate summary
        batch_results['summary'] = self._generate_batch_summary(batch_results)
        
        return batch_results
    
    def _generate_batch_summary(self, batch_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics for batch test results."""
        summary = {
            'success_rate': 0.0,
            'average_banner_confidence': 0.0,
            'banner_type_distribution': {},
            'common_issues': [],
            'recommendations': []
        }
        
        if batch_results['total_tests'] > 0:
            summary['success_rate'] = batch_results['successful_tests'] / batch_results['total_tests']
        
        # Analyze test details
        banner_confidences = []
        banner_types = {}
        issues = []
        
        for test_detail in batch_results['test_details']:
            # Collect banner confidence scores
            if 'test_case' in test_detail:
                banner_type = test_detail['test_case'].get('banner_type', 'unknown')
                banner_types[banner_type] = banner_types.get(banner_type, 0) + 1
            
            # Collect issues
            if not test_detail.get('overall_success', False):
                if 'error' in test_detail:
                    issues.append(test_detail['error'])
                elif 'banner_validation' in test_detail:
                    banner_validation = test_detail['banner_validation']
                    if not banner_validation.get('banner_present', False):
                        issues.append('Banner not detected')
                    elif not banner_validation.get('banner_hideable', False):
                        issues.append('Banner cannot be hidden')
        
        summary['banner_type_distribution'] = banner_types
        summary['common_issues'] = list(set(issues))
        
        # Generate recommendations
        if summary['success_rate'] < 0.8:
            summary['recommendations'].append('Consider improving banner detection patterns')
        
        if 'Banner not detected' in issues:
            summary['recommendations'].append('Review banner selector patterns')
        
        if 'Banner cannot be hidden' in issues:
            summary['recommendations'].append('Check banner hiding mechanisms')
        
        return summary
    
    def save_test_results(self, results: Dict[str, Any], filename: str = None) -> str:
        """
        Save test results to a JSON file.
        
        Args:
            results: Test results dictionary
            filename: Optional filename
            
        Returns:
            Path to saved file
        """
        try:
            os.makedirs("data/test_results", exist_ok=True)
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"comprehensive_test_results_{timestamp}.json"
            
            if not filename.endswith('.json'):
                filename += '.json'
            
            filepath = f"data/test_results/{filename}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"Test results saved to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error saving test results: {e}")
            return ""
    
    def load_test_results(self, filepath: str) -> Dict[str, Any]:
        """
        Load test results from a JSON file.
        
        Args:
            filepath: Path to test results file
            
        Returns:
            Test results dictionary
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading test results: {e}")
            return {}
    
    def compare_test_results(self, results1: Dict[str, Any], results2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two sets of test results.
        
        Args:
            results1: First test results
            results2: Second test results
            
        Returns:
            Comparison results
        """
        comparison = {
            'success_rate_change': 0.0,
            'performance_improvement': 0.0,
            'new_issues': [],
            'resolved_issues': [],
            'overall_improvement': False
        }
        
        # Compare success rates
        success_rate1 = results1.get('summary', {}).get('success_rate', 0.0)
        success_rate2 = results2.get('summary', {}).get('success_rate', 0.0)
        comparison['success_rate_change'] = success_rate2 - success_rate1
        
        # Compare issues
        issues1 = set(results1.get('summary', {}).get('common_issues', []))
        issues2 = set(results2.get('summary', {}).get('common_issues', []))
        
        comparison['new_issues'] = list(issues2 - issues1)
        comparison['resolved_issues'] = list(issues1 - issues2)
        
        # Determine overall improvement
        comparison['overall_improvement'] = (
            comparison['success_rate_change'] > 0 and
            len(comparison['new_issues']) < len(comparison['resolved_issues'])
        )
        
        return comparison
