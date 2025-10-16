"""
Specialized collector for gathering consent banner data.
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime

from .web_scraper import WebScraper
from ..models import PageData, BannerInfo


class BannerCollector:
    """Specialized collector for gathering consent banner data from multiple sites."""
    
    def __init__(self, headless: bool = True):
        """
        Initialize the banner collector.
        
        Args:
            headless: Run browser in headless mode
        """
        self.scraper = WebScraper(headless=headless)
        self.collected_banners = []
    
    def collect_from_sites(self, urls: List[str]) -> List[PageData]:
        """
        Collect page data from multiple sites.
        
        Args:
            urls: List of URLs to collect from
            
        Returns:
            List of PageData objects
        """
        page_data_list = []
        
        for url in urls:
            print(f"Collecting data from: {url}")
            try:
                page_data = self.scraper.collect_page(url)
                page_data_list.append(page_data)
                
                # Save individual page data
                self.scraper.save_page_data(page_data)
                
                print(f"Successfully collected data from: {url}")
                
            except Exception as e:
                print(f"Error collecting from {url}: {e}")
                continue
        
        return page_data_list
    
    def collect_from_pharmacy_sites(self) -> List[PageData]:
        """Collect data from common pharmacy sites known to have consent banners."""
        pharmacy_urls = [
            "https://www.cvs.com",
            "https://www.walgreens.com",
            "https://www.riteaid.com",
            "https://www.pharmacy.ca.gov",
            "https://www.healthmart.com",
            "https://www.goodrx.com",
            "https://www.pharmacychecker.com"
        ]
        
        return self.collect_from_sites(pharmacy_urls)
    
    def collect_from_municipal_sites(self) -> List[PageData]:
        """Collect data from municipal/government sites known to have consent banners."""
        municipal_urls = [
            "https://www.usa.gov",
            "https://www.healthcare.gov",
            "https://www.irs.gov",
            "https://www.ssa.gov",
            "https://www.fda.gov",
            "https://www.cdc.gov",
            "https://www.nih.gov"
        ]
        
        return self.collect_from_sites(municipal_urls)
    
    def collect_from_custom_list(self, filepath: str) -> List[PageData]:
        """
        Collect data from a custom list of URLs stored in a file.
        
        Args:
            filepath: Path to file containing URLs (one per line)
            
        Returns:
            List of PageData objects
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            return self.collect_from_sites(urls)
            
        except Exception as e:
            print(f"Error reading URL file {filepath}: {e}")
            return []
    
    def save_collection_summary(self, page_data_list: List[PageData], filename: Optional[str] = None):
        """
        Save a summary of collected data.
        
        Args:
            page_data_list: List of collected PageData objects
            filename: Optional custom filename
        """
        try:
            os.makedirs("data/examples", exist_ok=True)
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"collection_summary_{timestamp}.json"
            
            filepath = f"data/examples/{filename}"
            
            summary = {
                "collection_date": datetime.now().isoformat(),
                "total_sites": len(page_data_list),
                "sites": []
            }
            
            for page_data in page_data_list:
                site_info = {
                    "url": page_data.url,
                    "collected_at": page_data.collected_at,
                    "html_size": len(page_data.html_content),
                    "js_files": len(page_data.javascript_content),
                    "css_files": len(page_data.css_content),
                    "has_screenshot": page_data.screenshot_path is not None,
                    "metadata": page_data.metadata
                }
                summary["sites"].append(site_info)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            print(f"Collection summary saved to: {filepath}")
            
        except Exception as e:
            print(f"Error saving collection summary: {e}")
    
    def extract_banner_html(self, page_data: PageData) -> Optional[str]:
        """
        Extract HTML content that might contain consent banners.
        
        Args:
            page_data: PageData object to analyze
            
        Returns:
            Extracted HTML content or None
        """
        from bs4 import BeautifulSoup
        
        try:
            soup = BeautifulSoup(page_data.html_content, 'html.parser')
            
            # Common consent banner selectors
            banner_selectors = [
                "[id*='cookie']",
                "[class*='cookie']",
                "[id*='consent']",
                "[class*='consent']",
                "[id*='gdpr']",
                "[class*='gdpr']",
                "[id*='privacy']",
                "[class*='privacy']",
                ".cc-banner",
                ".cookie-banner",
                ".consent-banner",
                ".gdpr-banner",
                ".privacy-notice",
                "#cookie-notice",
                "#consent-notice",
                "#gdpr-notice"
            ]
            
            banner_html = []
            
            for selector in banner_selectors:
                try:
                    elements = soup.select(selector)
                    for element in elements:
                        if element.get_text(strip=True):  # Only non-empty elements
                            banner_html.append(str(element))
                except Exception:
                    continue
            
            if banner_html:
                return "\n".join(banner_html)
            
        except Exception as e:
            print(f"Error extracting banner HTML: {e}")
        
        return None
    
    def close(self):
        """Close the web scraper."""
        self.scraper.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
