#!/usr/bin/env python3
"""
Comprehensive Pharmacy Website Tester for CMP Mapper
Tests 22 pharmacy websites that are known to have consent banners
"""

import sys
import os
import time
import json
from datetime import datetime
from typing import List, Dict, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.collectors.web_scraper import WebScraper
from src.detectors.banner_detector import BannerDetector
from src.generators.rule_generator import RuleGenerator

class PharmacyWebsiteTester:
    def __init__(self):
        self.test_results = []
        self.pharmacy_sites = [
            "https://pharmasave.com/store/pharmasave-allandale/",
            "https://www.guardian-ida-remedysrx.ca/en/ontario/barrie/primary-care-pharmacy-7022839",
            "https://pharmasave.com/store/pharmasave-royal-medical/",
            "https://shoppersdrugmart.ca",
            "https://beyondrx.ca/",
            "https://www.pharmachoice.com/locations/apex-compounding-pharmacy/",
            "https://pharmasave.com/store/pharmasave-balmoral/",
            "https://www.villageofislington.com/business/dunbloor-medical-pharmacy-and-walk-in-clinic/",
            "https://emeryvillagepharmacy.com/",
            "https://www.guardian-ida-remedysrx.ca/en/ontario/barrie/little-lake-pharmacy-7016243",
            "https://www.pharmachoice.com/locations/little-avenue-pharmacy/",
            "https://www.innomar-strategies.com/",
            "https://www.foodbasics.ca/services/pharmacy",
            "https://www.midtowncompoundingpharmacy.ca/",
            "https://www.medsexpert.ca/",
            "https://www.margispharmacy.com/",
            "https://www.prepclinic.ca/",
            "https://www.medicineshoppe.ca/",
            "https://homewoodhealthcentre.com/",
            "https://www.greenshield.ca/en-ca/health/pharmacy",
            "https://www.ottawahospital.on.ca/en/"
        ]
        
    def test_single_site(self, url: str) -> Dict[str, Any]:
        """Test a single website for consent banner detection"""
        print(f"Testing: {url}")
        
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'banner_detected': False,
            'confidence': 0.0,
            'error': None,
            'html_size': 0,
            'banner_info': None,
            'rule_generated': False
        }
        
        try:
            # Collect page data
            with WebScraper(headless=True, timeout=30) as scraper:
                page_data = scraper.collect_page(url)
            
            if not page_data or not page_data.html_content:
                result['error'] = 'Failed to collect page data'
                return result
            
            result['html_size'] = len(page_data.html_content)
            result['success'] = True
            
            # Detect banner
            detector = BannerDetector()
            banner_info = detector.detect_banner(page_data)
            
            if banner_info:
                result['banner_detected'] = True
                result['confidence'] = banner_info.detection_confidence
                result['banner_info'] = {
                    'banner_type': banner_info.banner_type.value,
                    'buttons_count': len(banner_info.buttons),
                    'container_selector': banner_info.container_selector,
                    'cmp_type': getattr(banner_info, 'cmp_type', None),
                    'cmp_confidence': getattr(banner_info, 'cmp_confidence', 0.0)
                }
                
                # Generate rule
                try:
                    generator = RuleGenerator()
                    rule = generator.generate_consent_o_matic_json(banner_info)
                    if rule:
                        result['rule_generated'] = True
                except Exception as e:
                    result['error'] = f'Rule generation failed: {str(e)}'
            else:
                result['banner_detected'] = False
                result['error'] = 'No banner detected (FALSE NEGATIVE)'
                
        except Exception as e:
            result['error'] = f'Test failed: {str(e)}'
            result['success'] = False
        
        return result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run tests on all pharmacy websites"""
        print("=" * 80)
        print("PHARMACY WEBSITE CONSENT BANNER TESTER")
        print("=" * 80)
        print(f"Testing {len(self.pharmacy_sites)} pharmacy websites...")
        print("All sites are known to have consent banners")
        print("=" * 80)
        
        start_time = time.time()
        
        for i, url in enumerate(self.pharmacy_sites, 1):
            print(f"\n[{i}/{len(self.pharmacy_sites)}] Testing: {url}")
            result = self.test_single_site(url)
            self.test_results.append(result)
            
            # Print result
            if result['banner_detected']:
                print(f"  [OK] Banner detected (confidence: {result['confidence']:.2f})")
                if result['rule_generated']:
                    print(f"  [OK] Rule generated successfully")
                else:
                    print(f"  [WARN] Rule generation failed")
            else:
                print(f"  [FAIL] NO BANNER DETECTED - FALSE NEGATIVE!")
                if result['error']:
                    print(f"  Error: {result['error']}")
            
            # Small delay to be respectful
            time.sleep(1)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Generate summary
        summary = self.generate_summary(duration)
        
        return {
            'summary': summary,
            'results': self.test_results,
            'test_duration': duration
        }
    
    def generate_summary(self, duration: float) -> Dict[str, Any]:
        """Generate test summary"""
        total_sites = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['success'])
        banners_detected = sum(1 for r in self.test_results if r['banner_detected'])
        rules_generated = sum(1 for r in self.test_results if r['rule_generated'])
        
        false_negatives = total_sites - banners_detected
        detection_rate = (banners_detected / total_sites) * 100 if total_sites > 0 else 0
        
        # Group by error types
        error_types = {}
        for result in self.test_results:
            if result['error']:
                error_type = result['error'].split(':')[0] if ':' in result['error'] else result['error']
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        summary = {
            'total_sites': total_sites,
            'successful_tests': successful_tests,
            'banners_detected': banners_detected,
            'rules_generated': rules_generated,
            'false_negatives': false_negatives,
            'detection_rate': round(detection_rate, 2),
            'test_duration': round(duration, 2),
            'error_types': error_types,
            'failed_sites': [r['url'] for r in self.test_results if not r['banner_detected']]
        }
        
        return summary
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print formatted test summary"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Sites Tested: {summary['total_sites']}")
        print(f"Successful Tests: {summary['successful_tests']}")
        print(f"Banners Detected: {summary['banners_detected']}")
        print(f"Rules Generated: {summary['rules_generated']}")
        print(f"False Negatives: {summary['false_negatives']}")
        print(f"Detection Rate: {summary['detection_rate']}%")
        print(f"Test Duration: {summary['test_duration']} seconds")
        
        if summary['error_types']:
            print(f"\nError Types:")
            for error_type, count in summary['error_types'].items():
                print(f"  - {error_type}: {count}")
        
        if summary['failed_sites']:
            print(f"\nSites with FALSE NEGATIVES:")
            for site in summary['failed_sites']:
                print(f"  - {site}")
        
        print("=" * 80)
    
    def save_results(self, filename: str = None):
        """Save test results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pharmacy_test_results_{timestamp}.json"
        
        results = {
            'test_info': {
                'timestamp': datetime.now().isoformat(),
                'total_sites': len(self.pharmacy_sites),
                'tester_version': '1.0'
            },
            'summary': self.generate_summary(0),
            'results': self.test_results
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to: {filename}")
        return filename

def main():
    """Main function to run the pharmacy website tester"""
    tester = PharmacyWebsiteTester()
    
    try:
        results = tester.run_all_tests()
        tester.print_summary(results['summary'])
        
        # Save results
        filename = tester.save_results()
        
        # Return exit code based on detection rate
        detection_rate = results['summary']['detection_rate']
        if detection_rate >= 90:
            print(f"\n[EXCELLENT] Detection rate: {detection_rate}%")
            return 0
        elif detection_rate >= 70:
            print(f"\n[GOOD] Detection rate: {detection_rate}% - needs improvement")
            return 1
        else:
            print(f"\n[POOR] Detection rate: {detection_rate}% - Major issues!")
            return 2
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        return 3
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        return 4

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
