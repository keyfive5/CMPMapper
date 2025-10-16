"""
Web scraper for collecting HTML content and consent banners.
"""

import os
import time
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from ..models import PageData


class WebScraper:
    """Web scraper for collecting page data and consent banners."""
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        """
        Initialize the web scraper.
        
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
        
        # Add options for better scraping
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
            print("Falling back to requests-based scraping")
            self.driver = None
    
    def collect_page(self, url: str, wait_for_banner: bool = True) -> PageData:
        """
        Collect page data including HTML content and potential consent banners.
        
        Args:
            url: URL to scrape
            wait_for_banner: Whether to wait for consent banners to load
            
        Returns:
            PageData object with collected information
        """
        if self.driver:
            return self._collect_with_selenium(url, wait_for_banner)
        else:
            return self._collect_with_requests(url)
    
    def _collect_with_selenium(self, url: str, wait_for_banner: bool = True) -> PageData:
        """Collect page data using Selenium."""
        try:
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            if wait_for_banner:
                # Wait a bit more for potential consent banners
                time.sleep(3)
                
                # Try to find common consent banner selectors
                self._wait_for_consent_banners()
            
            # Get page source
            html_content = self.driver.page_source
            
            # Extract JavaScript content
            js_content = self._extract_javascript()
            
            # Extract CSS content
            css_content = self._extract_css()
            
            # Take screenshot if needed
            screenshot_path = self._take_screenshot(url)
            
            return PageData(
                url=url,
                html_content=html_content,
                javascript_content=js_content,
                css_content=css_content,
                screenshot_path=screenshot_path,
                collected_at=datetime.now().isoformat(),
                metadata={
                    "user_agent": self.driver.execute_script("return navigator.userAgent;"),
                    "viewport_size": self.driver.get_window_size(),
                    "page_title": self.driver.title
                }
            )
            
        except Exception as e:
            print(f"Error collecting page {url}: {e}")
            return self._collect_with_requests(url)
    
    def _collect_with_requests(self, url: str) -> PageData:
        """Fallback collection using requests."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            return PageData(
                url=url,
                html_content=response.text,
                javascript_content=[],
                css_content=[],
                collected_at=datetime.now().isoformat(),
                metadata={
                    "status_code": response.status_code,
                    "content_type": response.headers.get('content-type', ''),
                    "response_size": len(response.content)
                }
            )
            
        except Exception as e:
            print(f"Error with requests fallback for {url}: {e}")
            return PageData(
                url=url,
                html_content="",
                collected_at=datetime.now().isoformat(),
                metadata={"error": str(e)}
            )
    
    def _wait_for_consent_banners(self):
        """Wait for common consent banner patterns to appear."""
        common_selectors = [
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
            "#cookie-notice",
            "#consent-notice"
        ]
        
        for selector in common_selectors:
            try:
                WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"Found potential consent banner with selector: {selector}")
                break
            except TimeoutException:
                continue
    
    def _extract_javascript(self) -> List[str]:
        """Extract JavaScript content from the page."""
        js_content = []
        if self.driver:
            try:
                # Get inline scripts
                scripts = self.driver.find_elements(By.TAG_NAME, "script")
                for script in scripts:
                    src = script.get_attribute("src")
                    if src:
                        js_content.append(src)
                    else:
                        content = script.get_attribute("innerHTML")
                        if content:
                            js_content.append(content)
            except Exception as e:
                print(f"Error extracting JavaScript: {e}")
        
        return js_content
    
    def _extract_css(self) -> List[str]:
        """Extract CSS content from the page."""
        css_content = []
        if self.driver:
            try:
                # Get stylesheets
                links = self.driver.find_elements(By.CSS_SELECTOR, "link[rel='stylesheet']")
                for link in links:
                    href = link.get_attribute("href")
                    if href:
                        css_content.append(href)
                
                # Get inline styles
                styles = self.driver.find_elements(By.TAG_NAME, "style")
                for style in styles:
                    content = style.get_attribute("innerHTML")
                    if content:
                        css_content.append(content)
            except Exception as e:
                print(f"Error extracting CSS: {e}")
        
        return css_content
    
    def _take_screenshot(self, url: str) -> Optional[str]:
        """Take a screenshot of the page."""
        try:
            if self.driver:
                # Create screenshots directory
                os.makedirs("data/test_results/screenshots", exist_ok=True)
                
                # Generate filename
                domain = urlparse(url).netloc
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{domain}_{timestamp}.png"
                filepath = f"data/test_results/screenshots/{filename}"
                
                self.driver.save_screenshot(filepath)
                return filepath
        except Exception as e:
            print(f"Error taking screenshot: {e}")
        
        return None
    
    def save_page_data(self, page_data: PageData, filename: Optional[str] = None):
        """Save page data to a JSON file."""
        try:
            os.makedirs("data/examples", exist_ok=True)
            
            if not filename:
                domain = urlparse(page_data.url).netloc
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{domain}_{timestamp}.json"
            
            filepath = f"data/examples/{filename}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(page_data.dict(), f, indent=2, ensure_ascii=False)
            
            print(f"Page data saved to: {filepath}")
            
        except Exception as e:
            print(f"Error saving page data: {e}")
    
    def close(self):
        """Close the web driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
