"""
Basic functionality tests for CMP Mapper.

These tests verify the core functionality of the CMP Mapper components.
"""

import unittest
import sys
import os
import tempfile
import shutil

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.models import PageData, BannerInfo, ConsentRule, BannerType, ButtonType, ConsentButton
from src.extractors import BannerExtractor, ButtonExtractor
from src.generators import RuleGenerator
from src.detectors import PatternMatcher


class TestModels(unittest.TestCase):
    """Test data models."""
    
    def test_page_data_creation(self):
        """Test PageData model creation."""
        page_data = PageData(
            url="https://example.com",
            html_content="<html><body>Test</body></html>",
            collected_at="2023-12-01T10:00:00"
        )
        
        self.assertEqual(page_data.url, "https://example.com")
        self.assertIn("Test", page_data.html_content)
        self.assertEqual(page_data.collected_at, "2023-12-01T10:00:00")
    
    def test_banner_info_creation(self):
        """Test BannerInfo model creation."""
        button = ConsentButton(
            text="Accept",
            button_type=ButtonType.ACCEPT,
            selector="#accept-btn",
            is_visible=True
        )
        
        banner_info = BannerInfo(
            site="example.com",
            banner_type=BannerType.MODAL,
            container_selector="#cookie-banner",
            buttons=[button],
            html_content="<div id='cookie-banner'>...</div>",
            detection_confidence=0.8
        )
        
        self.assertEqual(banner_info.site, "example.com")
        self.assertEqual(banner_info.banner_type, BannerType.MODAL)
        self.assertEqual(len(banner_info.buttons), 1)
        self.assertEqual(banner_info.buttons[0].button_type, ButtonType.ACCEPT)
    
    def test_consent_rule_creation(self):
        """Test ConsentRule model creation."""
        rule = ConsentRule(
            site="example.com",
            selectors={
                "banner": "#cookie-banner",
                "acceptButton": "#accept-btn"
            },
            actions=["clickRejectIfPossible", "hideBanner"],
            metadata={"confidence_score": 0.8}
        )
        
        self.assertEqual(rule.site, "example.com")
        self.assertIn("banner", rule.selectors)
        self.assertIn("clickRejectIfPossible", rule.actions)


class TestExtractors(unittest.TestCase):
    """Test feature extractors."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.banner_extractor = BannerExtractor()
        self.button_extractor = ButtonExtractor()
    
    def test_banner_extraction(self):
        """Test banner extraction from HTML."""
        html_content = """
        <div id="cookie-banner" class="modal">
            <h3>Cookie Consent</h3>
            <button id="accept-btn">Accept All</button>
            <button id="reject-btn">Reject All</button>
        </div>
        """
        
        banner_info = self.banner_extractor.extract_banner_info(html_content, "test.com")
        
        self.assertIsNotNone(banner_info)
        self.assertEqual(banner_info.site, "test.com")
        self.assertGreater(banner_info.detection_confidence, 0)
    
    def test_button_extraction(self):
        """Test button extraction from HTML."""
        html_content = """
        <div class="cookie-banner">
            <button class="accept-btn">Accept All</button>
            <button class="reject-btn">Reject All</button>
            <button class="manage-btn">Manage Cookies</button>
        </div>
        """
        
        buttons = self.button_extractor.extract_buttons_from_html(html_content)
        
        self.assertGreater(len(buttons), 0)
        
        button_types = [button.button_type for button in buttons]
        self.assertIn(ButtonType.ACCEPT, button_types)
        self.assertIn(ButtonType.REJECT, button_types)
    
    def test_button_classification(self):
        """Test button type classification."""
        test_cases = [
            ("Accept All", ButtonType.ACCEPT),
            ("Reject All", ButtonType.REJECT),
            ("Manage Preferences", ButtonType.MANAGE),
            ("Close", ButtonType.CLOSE)
        ]
        
        for text, expected_type in test_cases:
            button_type = self.button_extractor._classify_button_type(text)
            self.assertEqual(button_type, expected_type)


class TestGenerators(unittest.TestCase):
    """Test rule generators."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = RuleGenerator()
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_rule_generation(self):
        """Test rule generation from banner info."""
        button = ConsentButton(
            text="Accept",
            button_type=ButtonType.ACCEPT,
            selector="#accept-btn",
            is_visible=True
        )
        
        banner_info = BannerInfo(
            site="example.com",
            banner_type=BannerType.MODAL,
            container_selector="#cookie-banner",
            buttons=[button],
            html_content="<div id='cookie-banner'>...</div>",
            detection_confidence=0.8
        )
        
        rule = self.generator.generate_rule(banner_info)
        
        self.assertIsNotNone(rule)
        self.assertEqual(rule.site, "example.com")
        self.assertIn("banner", rule.selectors)
        self.assertIn("hideBanner", rule.actions)
    
    def test_rule_validation(self):
        """Test rule validation."""
        rule = ConsentRule(
            site="example.com",
            selectors={"banner": "#cookie-banner"},
            actions=["hideBanner"],
            metadata={"confidence_score": 0.8}
        )
        
        validation = self.generator.validate_rule(rule)
        
        self.assertIsInstance(validation, dict)
        self.assertIn("valid", validation)
        self.assertIn("score", validation)
    
    def test_rule_optimization(self):
        """Test rule optimization."""
        rule = ConsentRule(
            site="example.com",
            selectors={"banner": "#cookie-banner"},
            actions=["hideBanner", "hideBanner"],  # Duplicate action
            metadata={"confidence_score": 0.8}
        )
        
        optimized = self.generator.optimize_rule(rule)
        
        self.assertEqual(len(optimized.actions), 1)  # Duplicate removed
        self.assertIn("optimized", optimized.metadata)


class TestDetectors(unittest.TestCase):
    """Test detection components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.pattern_matcher = PatternMatcher()
    
    def test_pattern_matching(self):
        """Test pattern matching functionality."""
        from bs4 import BeautifulSoup
        
        html = """
        <div class="cookie-banner">
            <p>We use cookies to improve your experience.</p>
            <button>Accept All</button>
            <button>Reject All</button>
        </div>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('div', class_='cookie-banner')
        
        scores = self.pattern_matcher.match_banner_patterns(element)
        
        self.assertIsInstance(scores, dict)
        self.assertIn('overall_score', scores)
        self.assertGreater(scores['overall_score'], 0)
    
    def test_button_pattern_matching(self):
        """Test button pattern matching."""
        from bs4 import BeautifulSoup
        
        html = """
        <button>Accept All Cookies</button>
        <button>Reject All</button>
        <button>Manage Preferences</button>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        
        accept_button = soup.find('button', string=lambda text: text and 'Accept' in text)
        reject_button = soup.find('button', string=lambda text: text and 'Reject' in text)
        
        accept_type, accept_confidence = self.pattern_matcher.match_button_patterns(accept_button)
        reject_type, reject_confidence = self.pattern_matcher.match_button_patterns(reject_button)
        
        self.assertEqual(accept_type, ButtonType.ACCEPT)
        self.assertEqual(reject_type, ButtonType.REJECT)
        self.assertGreater(accept_confidence, 0)
        self.assertGreater(reject_confidence, 0)
    
    def test_language_detection(self):
        """Test language detection."""
        english_text = "We use cookies to improve your experience. Accept all cookies."
        spanish_text = "Utilizamos cookies para mejorar su experiencia. Aceptar todas las cookies."
        
        english_lang = self.pattern_matcher.detect_language(english_text)
        spanish_lang = self.pattern_matcher.detect_language(spanish_text)
        
        self.assertEqual(english_lang, "english")
        self.assertEqual(spanish_lang, "spanish")


class TestIntegration(unittest.TestCase):
    """Test integration between components."""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from HTML to rule."""
        html_content = """
        <div id="cookie-consent-modal" class="modal-overlay">
            <div class="cookie-banner">
                <h3>Cookie Consent</h3>
                <p>We use cookies to improve your experience.</p>
                <button id="accept-btn" class="btn-accept">Accept All</button>
                <button id="reject-btn" class="btn-reject">Reject All</button>
                <button id="manage-btn" class="btn-manage">Manage Preferences</button>
            </div>
        </div>
        """
        
        # Step 1: Extract banner info
        banner_extractor = BannerExtractor()
        banner_info = banner_extractor.extract_banner_info(html_content, "test.com")
        
        self.assertIsNotNone(banner_info)
        
        # Step 2: Generate rule
        generator = RuleGenerator()
        rule = generator.generate_rule(banner_info)
        
        self.assertIsNotNone(rule)
        self.assertEqual(rule.site, "test.com")
        self.assertIn("banner", rule.selectors)
        self.assertIn("acceptButton", rule.selectors)
        self.assertIn("rejectButton", rule.selectors)
        
        # Step 3: Validate rule
        validation = generator.validate_rule(rule)
        self.assertTrue(validation["valid"])
        self.assertGreater(validation["score"], 0)


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestModels,
        TestExtractors,
        TestGenerators,
        TestDetectors,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
