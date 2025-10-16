"""
Banner validation utilities for testing consent banners.
"""

import time
from typing import Dict, List, Optional, Tuple, Any
from bs4 import BeautifulSoup, Tag

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..models import BannerInfo, ConsentRule, ButtonType


class BannerValidator:
    """Validates consent banners and their interactions."""
    
    def __init__(self, driver: webdriver.Chrome = None):
        """
        Initialize the banner validator.
        
        Args:
            driver: Optional WebDriver instance
        """
        self.driver = driver
    
    def validate_banner_presence(self, banner_info: BannerInfo) -> bool:
        """
        Validate that a banner is present on the page.
        
        Args:
            banner_info: BannerInfo object
            
        Returns:
            True if banner is present and valid
        """
        if not self.driver:
            return False
        
        try:
            # Find banner element
            banner_element = self.driver.find_element(By.CSS_SELECTOR, banner_info.container_selector)
            
            # Check if banner is visible
            if not banner_element.is_displayed():
                return False
            
            # Check if banner has expected content
            banner_text = banner_element.text.lower()
            consent_keywords = ['cookie', 'consent', 'gdpr', 'privacy']
            
            has_keywords = any(keyword in banner_text for keyword in consent_keywords)
            if not has_keywords:
                return False
            
            return True
            
        except NoSuchElementException:
            return False
        except Exception as e:
            print(f"Error validating banner presence: {e}")
            return False
    
    def validate_button_functionality(self, banner_info: BannerInfo) -> Dict[ButtonType, bool]:
        """
        Validate that banner buttons are functional.
        
        Args:
            banner_info: BannerInfo object
            
        Returns:
            Dictionary of button types and their functionality status
        """
        results = {}
        
        if not self.driver:
            return results
        
        for button in banner_info.buttons:
            try:
                # Find button element
                button_element = self.driver.find_element(By.CSS_SELECTOR, button.selector)
                
                # Check if button is visible and clickable
                is_visible = button_element.is_displayed()
                is_enabled = button_element.is_enabled()
                
                # Try to click the button
                if is_visible and is_enabled:
                    self.driver.execute_script("arguments[0].click();", button_element)
                    results[button.button_type] = True
                else:
                    results[button.button_type] = False
                    
            except NoSuchElementException:
                results[button.button_type] = False
            except Exception as e:
                print(f"Error validating button {button.button_type}: {e}")
                results[button.button_type] = False
        
        return results
    
    def validate_banner_hiding(self, banner_info: BannerInfo) -> bool:
        """
        Validate that the banner can be hidden.
        
        Args:
            banner_info: BannerInfo object
            
        Returns:
            True if banner can be hidden successfully
        """
        if not self.driver:
            return False
        
        try:
            # Find banner element
            banner_element = self.driver.find_element(By.CSS_SELECTOR, banner_info.container_selector)
            
            # Hide the banner
            self.driver.execute_script("arguments[0].style.display = 'none';", banner_element)
            
            # Wait a moment for changes to take effect
            time.sleep(0.5)
            
            # Check if banner is hidden
            return not banner_element.is_displayed()
            
        except NoSuchElementException:
            return False
        except Exception as e:
            print(f"Error validating banner hiding: {e}")
            return False
    
    def validate_overlay_hiding(self, banner_info: BannerInfo) -> bool:
        """
        Validate that overlay elements can be hidden.
        
        Args:
            banner_info: BannerInfo object
            
        Returns:
            True if overlays can be hidden successfully
        """
        if not self.driver or not banner_info.overlay_selectors:
            return True  # No overlays to hide
        
        try:
            all_hidden = True
            
            for overlay_selector in banner_info.overlay_selectors:
                try:
                    overlay_element = self.driver.find_element(By.CSS_SELECTOR, overlay_selector)
                    
                    # Hide the overlay
                    self.driver.execute_script("arguments[0].style.display = 'none';", overlay_element)
                    
                    # Check if overlay is hidden
                    if overlay_element.is_displayed():
                        all_hidden = False
                        
                except NoSuchElementException:
                    continue  # Overlay not found, which is fine
            
            return all_hidden
            
        except Exception as e:
            print(f"Error validating overlay hiding: {e}")
            return False
    
    def validate_rule_effectiveness(self, rule: ConsentRule) -> Dict[str, bool]:
        """
        Validate the effectiveness of a consent rule.
        
        Args:
            rule: ConsentRule object
            
        Returns:
            Dictionary of validation results
        """
        validation_results = {}
        
        if not self.driver:
            return validation_results
        
        try:
            # Test banner detection
            banner_selector = rule.selectors.get('banner', '')
            if banner_selector:
                try:
                    banner_element = self.driver.find_element(By.CSS_SELECTOR, banner_selector)
                    validation_results['banner_detected'] = banner_element.is_displayed()
                except NoSuchElementException:
                    validation_results['banner_detected'] = False
            
            # Test button interactions
            button_types = ['acceptButton', 'rejectButton', 'manageButton', 'closeButton']
            for button_type in button_types:
                if button_type in rule.selectors:
                    try:
                        button_element = self.driver.find_element(By.CSS_SELECTOR, rule.selectors[button_type])
                        validation_results[f'{button_type}_functional'] = (
                            button_element.is_displayed() and button_element.is_enabled()
                        )
                    except NoSuchElementException:
                        validation_results[f'{button_type}_functional'] = False
            
            # Test overlay hiding
            if 'overlay' in rule.selectors:
                overlay_selectors = rule.selectors['overlay']
                if isinstance(overlay_selectors, list):
                    validation_results['overlays_hidden'] = self._test_overlay_hiding(overlay_selectors)
                else:
                    validation_results['overlays_hidden'] = self._test_overlay_hiding([overlay_selectors])
            
        except Exception as e:
            print(f"Error validating rule effectiveness: {e}")
        
        return validation_results
    
    def _test_overlay_hiding(self, overlay_selectors: List[str]) -> bool:
        """Test if overlay elements can be hidden."""
        try:
            for selector in overlay_selectors:
                try:
                    overlay_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    self.driver.execute_script("arguments[0].style.display = 'none';", overlay_element)
                except NoSuchElementException:
                    continue  # Overlay not found, which is fine
            
            return True
            
        except Exception:
            return False
    
    def get_banner_state(self, banner_info: BannerInfo) -> Dict[str, Any]:
        """
        Get the current state of a banner.
        
        Args:
            banner_info: BannerInfo object
            
        Returns:
            Dictionary with banner state information
        """
        state = {
            'present': False,
            'visible': False,
            'interactable': False,
            'button_states': {},
            'overlay_states': {}
        }
        
        if not self.driver:
            return state
        
        try:
            # Check banner presence and visibility
            banner_element = self.driver.find_element(By.CSS_SELECTOR, banner_info.container_selector)
            state['present'] = True
            state['visible'] = banner_element.is_displayed()
            
            # Check button states
            for button in banner_info.buttons:
                try:
                    button_element = self.driver.find_element(By.CSS_SELECTOR, button.selector)
                    state['button_states'][button.button_type.value] = {
                        'present': True,
                        'visible': button_element.is_displayed(),
                        'enabled': button_element.is_enabled(),
                        'text': button_element.text
                    }
                except NoSuchElementException:
                    state['button_states'][button.button_type.value] = {
                        'present': False,
                        'visible': False,
                        'enabled': False,
                        'text': ''
                    }
            
            # Check overlay states
            for overlay_selector in banner_info.overlay_selectors:
                try:
                    overlay_element = self.driver.find_element(By.CSS_SELECTOR, overlay_selector)
                    state['overlay_states'][overlay_selector] = {
                        'present': True,
                        'visible': overlay_element.is_displayed()
                    }
                except NoSuchElementException:
                    state['overlay_states'][overlay_selector] = {
                        'present': False,
                        'visible': False
                    }
            
            # Determine if banner is interactable
            state['interactable'] = state['visible'] and any(
                button_state.get('visible', False) and button_state.get('enabled', False)
                for button_state in state['button_states'].values()
            )
            
        except NoSuchElementException:
            pass  # Banner not found
        except Exception as e:
            print(f"Error getting banner state: {e}")
        
        return state
    
    def simulate_user_interaction(self, banner_info: BannerInfo, interaction_type: str = 'reject') -> bool:
        """
        Simulate user interaction with the banner.
        
        Args:
            banner_info: BannerInfo object
            interaction_type: Type of interaction ('accept', 'reject', 'manage', 'close')
            
        Returns:
            True if interaction was successful
        """
        if not self.driver:
            return False
        
        try:
            # Find the appropriate button
            target_button_type = None
            if interaction_type == 'accept':
                target_button_type = ButtonType.ACCEPT
            elif interaction_type == 'reject':
                target_button_type = ButtonType.REJECT
            elif interaction_type == 'manage':
                target_button_type = ButtonType.MANAGE
            elif interaction_type == 'close':
                target_button_type = ButtonType.CLOSE
            
            if not target_button_type:
                return False
            
            # Find the button
            button = None
            for b in banner_info.buttons:
                if b.button_type == target_button_type:
                    button = b
                    break
            
            if not button:
                return False
            
            # Click the button
            button_element = self.driver.find_element(By.CSS_SELECTOR, button.selector)
            self.driver.execute_script("arguments[0].click();", button_element)
            
            # Wait for interaction to take effect
            time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"Error simulating user interaction: {e}")
            return False
    
    def measure_banner_performance(self, banner_info: BannerInfo) -> Dict[str, float]:
        """
        Measure banner performance metrics.
        
        Args:
            banner_info: BannerInfo object
            
        Returns:
            Dictionary with performance metrics
        """
        metrics = {
            'load_time': 0.0,
            'interaction_time': 0.0,
            'hide_time': 0.0
        }
        
        if not self.driver:
            return metrics
        
        try:
            # Measure banner load time
            start_time = time.time()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, banner_info.container_selector))
            )
            metrics['load_time'] = time.time() - start_time
            
            # Measure interaction time
            if banner_info.buttons:
                start_time = time.time()
                first_button = banner_info.buttons[0]
                button_element = self.driver.find_element(By.CSS_SELECTOR, first_button.selector)
                self.driver.execute_script("arguments[0].click();", button_element)
                metrics['interaction_time'] = time.time() - start_time
            
            # Measure hide time
            start_time = time.time()
            banner_element = self.driver.find_element(By.CSS_SELECTOR, banner_info.container_selector)
            self.driver.execute_script("arguments[0].style.display = 'none';", banner_element)
            metrics['hide_time'] = time.time() - start_time
            
        except Exception as e:
            print(f"Error measuring banner performance: {e}")
        
        return metrics
