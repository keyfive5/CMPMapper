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
from ..utils.error_handler import ErrorHandler, ErrorType, ErrorReport


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
        self.error_handler = ErrorHandler()
        self.error_reports = []
        self._setup_driver()
    
    def _setup_driver(self):
        """Set up the Chrome WebDriver."""
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        
        # Add options for better scraping and bot avoidance
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Enhanced bot detection avoidance (keeping JavaScript enabled for banner detection)
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-features=VizDisplayCompositor")
        
        # More realistic browser behavior
        options.add_argument("--lang=en-US,en;q=0.9")
        options.add_argument("--accept-language=en-US,en;q=0.9")
        options.add_argument("--accept-encoding=gzip, deflate, br")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(self.timeout)
            
            # Additional bot detection avoidance
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
            })
            
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
        try:
            if self.driver:
                return self._collect_with_selenium(url, wait_for_banner)
            else:
                return self._collect_with_requests(url)
        except Exception as e:
            # Handle errors and provide troubleshooting information
            error_report = self.error_handler.handle_scraping_error(e, url, {
                'wait_for_banner': wait_for_banner,
                'driver_available': self.driver is not None
            })
            self.error_reports.append(error_report)
            self.error_handler.log_error(error_report)
            
            # Return error page data with troubleshooting info
            return PageData(
                url=url,
                html_content="",
                collected_at=datetime.now().isoformat(),
                metadata={
                    'error': True,
                    'error_type': error_report.error_type.value,
                    'error_message': error_report.error_message,
                    'suggested_fixes': error_report.suggested_fixes,
                    'manual_steps': error_report.manual_steps,
                    'error_severity': error_report.error_severity
                }
            )
    
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
            
            # Check if we got a blocked/error page
            if self._is_blocked_page(html_content):
                print(f"Warning: Bot protection page detected")
                return PageData(
                    url=url,
                    html_content=html_content,
                    collected_at=datetime.now().isoformat(),
                    metadata={'blocked': True, 'error': 'Bot protection detected'}
                )
            
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
    
    def _is_blocked_page(self, html_content: str) -> bool:
        """Check if the page content indicates we're blocked."""
        html_lower = html_content.lower()
        
        # Common indicators of blocked/bot protection pages
        blocked_indicators = [
            '403', 'forbidden', 'access denied', 'blocked', 'bot detection',
            'captcha', 'cloudflare', 'ddos protection', 'security check',
            'please verify', 'verify you are human', 'robot check'
        ]
        
        for indicator in blocked_indicators:
            if indicator in html_lower:
                return True
        
        return False
    
    def close(self):
        """Close the web driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def get_error_reports(self) -> List[ErrorReport]:
        """Get all error reports from scraping attempts."""
        return self.error_reports
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics and troubleshooting information."""
        return self.error_handler.get_error_statistics(self.error_reports)
    
    def get_troubleshooting_report(self) -> Dict[str, Any]:
        """Get comprehensive troubleshooting report."""
        return self.error_handler.create_troubleshooting_report(self.error_reports)
    
    def clear_error_reports(self):
        """Clear all error reports."""
        self.error_reports = []
    
    def retry_with_different_strategy(self, url: str) -> PageData:
        """Retry scraping with different strategies based on error patterns."""
        error_stats = self.get_error_statistics()
        
        if error_stats.get('by_type', {}).get('bot_detection', 0) > 0:
            # Try with different user agent and settings
            return self._retry_with_bot_avoidance(url)
        elif error_stats.get('by_type', {}).get('timeout_error', 0) > 0:
            # Try with longer timeout
            return self._retry_with_extended_timeout(url)
        elif error_stats.get('by_type', {}).get('network_error', 0) > 0:
            # Try with requests instead of Selenium
            return self._retry_with_requests(url)
        else:
            # Default retry
            return self.collect_page(url)
    
    def _retry_with_bot_avoidance(self, url: str) -> PageData:
        """Retry with enhanced bot avoidance techniques."""
        try:
            # Update user agent
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
            })
            
            # Add random delay
            time.sleep(2)
            
            return self.collect_page(url)
        except Exception as e:
            error_report = self.error_handler.handle_scraping_error(e, url, {'retry_strategy': 'bot_avoidance'})
            self.error_reports.append(error_report)
            return PageData(
                url=url,
                html_content="",
                collected_at=datetime.now().isoformat(),
                metadata={'error': True, 'retry_failed': True, 'error_message': str(e)}
            )
    
    def _retry_with_extended_timeout(self, url: str) -> PageData:
        """Retry with extended timeout."""
        try:
            original_timeout = self.timeout
            self.timeout = 60  # Double the timeout
            self.driver.set_page_load_timeout(self.timeout)
            
            result = self.collect_page(url)
            
            # Restore original timeout
            self.timeout = original_timeout
            self.driver.set_page_load_timeout(self.timeout)
            
            return result
        except Exception as e:
            error_report = self.error_handler.handle_scraping_error(e, url, {'retry_strategy': 'extended_timeout'})
            self.error_reports.append(error_report)
            return PageData(
                url=url,
                html_content="",
                collected_at=datetime.now().isoformat(),
                metadata={'error': True, 'retry_failed': True, 'error_message': str(e)}
            )
    
    def _retry_with_requests(self, url: str) -> PageData:
        """Retry using requests instead of Selenium."""
        try:
            return self._collect_with_requests(url)
        except Exception as e:
            error_report = self.error_handler.handle_scraping_error(e, url, {'retry_strategy': 'requests_fallback'})
            self.error_reports.append(error_report)
            return PageData(
                url=url,
                html_content="",
                collected_at=datetime.now().isoformat(),
                metadata={'error': True, 'retry_failed': True, 'error_message': str(e)}
            )
