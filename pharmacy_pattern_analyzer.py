#!/usr/bin/env python3
"""
Pharmacy Website Pattern Analyzer
Tests multiple pharmacy websites and identifies common patterns
"""

import os
import sys
import json
import time
from typing import List, Dict, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.collectors.web_scraper import WebScraper
from src.detectors.banner_detector import BannerDetector
from src.generators.rule_generator import RuleGenerator


class PharmacyPatternAnalyzer:
    def __init__(self):
        self.pharmacy_sites = [
            "https://www.margispharmacy.com/",
            "https://beyondrx.ca/",
            "https://www.midtowncompoundingpharmacy.ca/",
            "https://hchcfamilyhealth.org/",
            "https://www.arkellmedical.ca/",
            "https://eramosapharmacy.ca",
            "https://blendrx.ca/",
            "https://www.westmountmedicalpharmacy.ca/",
            "https://www.doctr.ca/app/clinics/744319/McMaster-Drugstore/fr",
            "https://primecarepharmacy.ca/"
        ]
        
        self.results = []
        self.patterns = {
            'cmp_types': {},
            'container_selectors': {},
            'button_patterns': {},
            'common_selectors': []
        }
        
    def analyze_single_site(self, url: str) -> Dict[str, Any]:
        """Analyze a single pharmacy website."""
        result = {
            'url': url,
            'banner_detected': False,
            'confidence': 0.0,
            'cmp_type': None,
            'rule': None,
            'error': None
        }
        
        print(f"\n[{len(self.results) + 1}/{len(self.pharmacy_sites)}] Analyzing: {url}")
        
        try:
            # Collect page data
            with WebScraper(headless=True, timeout=30) as scraper:
                page_data = scraper.collect_page(url)
            
            if not page_data or not page_data.html_content:
                result['error'] = 'Failed to collect page data'
                print(f"  [FAIL] {result['error']}")
                return result
            
            # Detect banner
            detector = BannerDetector()
            banner_info = detector.detect_banner(page_data)
            
            if banner_info:
                result['banner_detected'] = True
                result['confidence'] = banner_info.detection_confidence
                result['cmp_type'] = banner_info.cmp_type
                
                # Generate rule
                generator = RuleGenerator()
                rule = generator.generate_consent_o_matic_json(banner_info)
                result['rule'] = rule
                
                print(f"  [OK] Banner detected (confidence: {result['confidence']:.2f})")
                if result['cmp_type']:
                    print(f"  [OK] CMP Type: {result['cmp_type']}")
            else:
                result['error'] = 'No banner detected'
                print(f"  [FAIL] {result['error']}")
                
        except Exception as e:
            result['error'] = str(e)
            print(f"  [ERROR] {result['error']}")
        
        return result
    
    def identify_patterns(self):
        """Identify common patterns across all successful detections."""
        successful = [r for r in self.results if r['banner_detected']]
        
        if not successful:
            print("\n[WARN] No successful detections to analyze patterns")
            return
        
        print("\n" + "="*80)
        print("PATTERN ANALYSIS")
        print("="*80)
        
        # CMP Type patterns
        cmp_counts = {}
        for r in successful:
            if r['cmp_type']:
                cmp_counts[r['cmp_type']] = cmp_counts.get(r['cmp_type'], 0) + 1
        
        if cmp_counts:
            print("\n[1] CMP Types Found:")
            for cmp_type, count in sorted(cmp_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(successful)) * 100
                print(f"  - {cmp_type}: {count} sites ({percentage:.1f}%)")
                self.patterns['cmp_types'][cmp_type] = count
        
        # Container selector patterns
        container_patterns = {}
        for r in successful:
            if r['rule'] and 'detectors' in r['rule']:
                detectors = r['rule']['detectors']
                for detector in detectors:
                    if 'showing' in detector:
                        selector = detector['showing']
                        container_patterns[selector] = container_patterns.get(selector, 0) + 1
        
        if container_patterns:
            print("\n[2] Container Selector Patterns:")
            for selector, count in sorted(container_patterns.items(), key=lambda x: x[1], reverse=True)[:5]:
                percentage = (count / len(successful)) * 100
                print(f"  - '{selector}': {count} sites ({percentage:.1f}%)")
                self.patterns['container_selectors'][selector] = count
        
        # Button selector patterns
        button_patterns = {}
        for r in successful:
            if r['rule'] and 'methods' in r['rule']:
                methods = r['rule']['methods']
                for method in methods:
                    if 'selector' in method:
                        selector = method['selector']
                        # Extract pattern (e.g., ".cky-btn" from ".cky-btn.cky-btn-accept")
                        pattern = selector.split('.')[1] if selector.startswith('.') else selector.split('#')[1] if selector.startswith('#') else selector
                        button_patterns[pattern] = button_patterns.get(pattern, 0) + 1
        
        if button_patterns:
            print("\n[3] Button Selector Patterns:")
            for pattern, count in sorted(button_patterns.items(), key=lambda x: x[1], reverse=True)[:10]:
                percentage = (count / len(successful)) * 100
                print(f"  - '{pattern}': {count} sites ({percentage:.1f}%)")
                self.patterns['button_patterns'][pattern] = count
        
        print("\n" + "="*80)
    
    def save_results(self, filename='pharmacy_analysis_results.json'):
        """Save analysis results to JSON file."""
        output = {
            'total_sites': len(self.pharmacy_sites),
            'successful_detections': sum(1 for r in self.results if r['banner_detected']),
            'failed_detections': sum(1 for r in self.results if not r['banner_detected']),
            'patterns': self.patterns,
            'individual_results': self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n[INFO] Results saved to {filename}")
        return filename
    
    def save_rules(self, output_dir='generated_rules'):
        """Save individual rules to JSON files."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        saved_rules = []
        for r in self.results:
            if r['banner_detected'] and r['rule']:
                # Generate filename from URL
                site_name = r['url'].replace('https://', '').replace('http://', '').split('/')[0]
                filename = f"{site_name}.json"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(r['rule'], f, indent=2, ensure_ascii=False)
                
                saved_rules.append(filepath)
                print(f"  [SAVED] {filepath}")
        
        print(f"\n[INFO] Saved {len(saved_rules)} rules to {output_dir}/")
        return saved_rules
    
    def run_analysis(self):
        """Run complete analysis on all pharmacy sites."""
        print("="*80)
        print("PHARMACY WEBSITE PATTERN ANALYZER")
        print("="*80)
        print(f"Analyzing {len(self.pharmacy_sites)} pharmacy websites...")
        print("="*80)
        
        start_time = time.time()
        
        # Analyze each site
        for url in self.pharmacy_sites:
            result = self.analyze_single_site(url)
            self.results.append(result)
            time.sleep(1)  # Be respectful
        
        end_time = time.time()
        
        # Summary
        successful = sum(1 for r in self.results if r['banner_detected'])
        failed = len(self.results) - successful
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total sites analyzed: {len(self.results)}")
        print(f"Successful detections: {successful} ({successful/len(self.results)*100:.1f}%)")
        print(f"Failed detections: {failed} ({failed/len(self.results)*100:.1f}%)")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        print("="*80)
        
        # Identify patterns
        self.identify_patterns()
        
        # Save results
        self.save_results()
        self.save_rules()
        
        return self.results


if __name__ == '__main__':
    analyzer = PharmacyPatternAnalyzer()
    
    try:
        analyzer.run_analysis()
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)

