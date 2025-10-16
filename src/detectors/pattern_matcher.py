"""
Pattern matching utilities for consent banner detection.
"""

import re
from typing import List, Dict, Tuple, Optional, Set
from bs4 import BeautifulSoup, Tag

from ..models import BannerType, ButtonType


class PatternMatcher:
    """Advanced pattern matching for consent banner detection."""
    
    def __init__(self):
        """Initialize the pattern matcher."""
        self.patterns = self._initialize_detection_patterns()
        self.language_patterns = self._initialize_language_patterns()
    
    def _initialize_detection_patterns(self) -> Dict[str, Dict]:
        """Initialize comprehensive detection patterns."""
        return {
            'banner_indicators': {
                'text_patterns': [
                    r'\bcookie\b', r'\bconsent\b', r'\bgdpr\b', r'\bprivacy\b',
                    r'\btracking\b', r'\banalytics\b', r'\badvertising\b',
                    r'\bpersonalization\b', r'\bpreferences\b', r'\bsettings\b',
                    r'\bdata\s+protection\b', r'\bdata\s+privacy\b'
                ],
                'class_patterns': [
                    r'.*cookie.*', r'.*consent.*', r'.*gdpr.*', r'.*privacy.*',
                    r'.*banner.*', r'.*notice.*', r'.*popup.*', r'.*modal.*',
                    r'.*overlay.*', r'.*dialog.*'
                ],
                'id_patterns': [
                    r'.*cookie.*', r'.*consent.*', r'.*gdpr.*', r'.*privacy.*',
                    r'.*banner.*', r'.*notice.*', r'.*popup.*', r'.*modal.*'
                ],
                'attribute_patterns': [
                    'data-consent', 'data-cookie', 'data-gdpr', 'data-privacy',
                    'aria-label', 'role', 'data-testid', 'data-cy', 'data-qa'
                ]
            },
            'button_patterns': {
                'accept_patterns': [
                    r'\baccept\b', r'\bagree\b', r'\bok\b', r'\byes\b', r'\ballow\b',
                    r'\bconsent\b', r'\bcontinue\b', r'\bproceed\b', r'\bi accept\b',
                    r'\bi agree\b', r'\bgot it\b', r'\baccept all\b', r'\bagree all\b',
                    r'\ballow all\b', r'\baccept cookies\b', r'\bagree to cookies\b'
                ],
                'reject_patterns': [
                    r'\bdecline\b', r'\breject\b', r'\bdeny\b', r'\bno\b', r'\brefuse\b',
                    r'\bdisagree\b', r'\bopt.?out\b', r'\bnecessary only\b',
                    r'\brequired only\b', r'\bessential only\b', r'\breject all\b',
                    r'\bdecline all\b', r'\bdeny all\b', r'\bopt out\b'
                ],
                'manage_patterns': [
                    r'\bmanage\b', r'\bpreferences\b', r'\bsettings\b', r'\boptions\b',
                    r'\bcustomize\b', r'\bchoose\b', r'\bselect\b', r'\bconfigure\b',
                    r'\bcontrol\b', r'\badjust\b', r'\bmanage cookies\b',
                    r'\bcookie settings\b', r'\bprivacy settings\b'
                ],
                'close_patterns': [
                    r'\bclose\b', r'\bdismiss\b', r'\b×\b', r'\b✕\b', r'\b×\b'
                ]
            },
            'structural_patterns': {
                'modal_indicators': [
                    'modal', 'popup', 'overlay', 'dialog', 'lightbox',
                    'z-index', 'position: fixed', 'position: absolute'
                ],
                'banner_indicators': [
                    'banner', 'notice', 'bar', 'strip', 'header', 'footer',
                    'top', 'bottom', 'fixed', 'sticky'
                ]
            }
        }
    
    def _initialize_language_patterns(self) -> Dict[str, Dict]:
        """Initialize language-specific patterns."""
        return {
            'english': {
                'cookie': ['cookie', 'cookies', 'tracking', 'analytics'],
                'consent': ['consent', 'agree', 'accept', 'allow', 'permission'],
                'privacy': ['privacy', 'data protection', 'personal data'],
                'preferences': ['preferences', 'settings', 'options', 'customize']
            },
            'spanish': {
                'cookie': ['cookie', 'cookies', 'seguimiento', 'analíticas'],
                'consent': ['consentimiento', 'acepto', 'aceptar', 'permitir'],
                'privacy': ['privacidad', 'protección de datos', 'datos personales'],
                'preferences': ['preferencias', 'configuración', 'opciones']
            },
            'french': {
                'cookie': ['cookie', 'cookies', 'suivi', 'analytiques'],
                'consent': ['consentement', 'j\'accepte', 'accepter', 'permettre'],
                'privacy': ['confidentialité', 'protection des données', 'données personnelles'],
                'preferences': ['préférences', 'paramètres', 'options']
            },
            'german': {
                'cookie': ['cookie', 'cookies', 'tracking', 'analytik'],
                'consent': ['einverständnis', 'zustimmen', 'akzeptieren', 'erlauben'],
                'privacy': ['datenschutz', 'datenschutzbestimmungen', 'personenbezogene daten'],
                'preferences': ['einstellungen', 'präferenzen', 'optionen']
            }
        }
    
    def match_banner_patterns(self, element: Tag) -> Dict[str, float]:
        """
        Match element against banner detection patterns.
        
        Args:
            element: HTML element to analyze
            
        Returns:
            Dictionary of pattern match scores
        """
        scores = {
            'text_score': 0.0,
            'class_score': 0.0,
            'id_score': 0.0,
            'attribute_score': 0.0,
            'structural_score': 0.0,
            'overall_score': 0.0
        }
        
        # Text content analysis
        text = element.get_text().lower()
        scores['text_score'] = self._match_text_patterns(text)
        
        # Class attribute analysis
        classes = ' '.join(element.get('class', [])).lower()
        scores['class_score'] = self._match_class_patterns(classes)
        
        # ID attribute analysis
        element_id = element.get('id', '').lower()
        scores['id_score'] = self._match_id_patterns(element_id)
        
        # Other attributes analysis
        scores['attribute_score'] = self._match_attribute_patterns(element.attrs)
        
        # Structural analysis
        scores['structural_score'] = self._match_structural_patterns(element)
        
        # Calculate overall score
        weights = {'text_score': 0.3, 'class_score': 0.25, 'id_score': 0.2, 
                  'attribute_score': 0.15, 'structural_score': 0.1}
        
        scores['overall_score'] = sum(scores[key] * weight for key, weight in weights.items())
        
        return scores
    
    def _match_text_patterns(self, text: str) -> float:
        """Match text content against banner patterns."""
        patterns = self.patterns['banner_indicators']['text_patterns']
        
        matches = 0
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches += 1
        
        return min(matches / len(patterns), 1.0)
    
    def _match_class_patterns(self, classes: str) -> float:
        """Match CSS classes against banner patterns."""
        patterns = self.patterns['banner_indicators']['class_patterns']
        
        matches = 0
        for pattern in patterns:
            if re.search(pattern, classes):
                matches += 1
        
        return min(matches / len(patterns), 1.0)
    
    def _match_id_patterns(self, element_id: str) -> float:
        """Match ID attribute against banner patterns."""
        patterns = self.patterns['banner_indicators']['id_patterns']
        
        matches = 0
        for pattern in patterns:
            if re.search(pattern, element_id):
                matches += 1
        
        return min(matches / len(patterns), 1.0)
    
    def _match_attribute_patterns(self, attrs: Dict) -> float:
        """Match element attributes against banner patterns."""
        patterns = self.patterns['banner_indicators']['attribute_patterns']
        
        matches = 0
        attr_str = str(attrs).lower()
        
        for pattern in patterns:
            if pattern in attr_str:
                matches += 1
        
        return min(matches / len(patterns), 1.0)
    
    def _match_structural_patterns(self, element: Tag) -> float:
        """Match element structure against banner patterns."""
        score = 0.0
        
        # Check for modal-like structure
        style = element.get('style', '').lower()
        classes = ' '.join(element.get('class', [])).lower()
        id_attr = element.get('id', '').lower()
        
        # Modal indicators
        modal_indicators = self.patterns['structural_patterns']['modal_indicators']
        for indicator in modal_indicators:
            if indicator in style or indicator in classes or indicator in id_attr:
                score += 0.3
        
        # Banner indicators
        banner_indicators = self.patterns['structural_patterns']['banner_indicators']
        for indicator in banner_indicators:
            if indicator in classes or indicator in id_attr:
                score += 0.2
        
        # Check for button elements
        buttons = element.find_all(['button', 'a', 'input'])
        if buttons:
            score += 0.2
        
        return min(score, 1.0)
    
    def match_button_patterns(self, element: Tag) -> Tuple[ButtonType, float]:
        """
        Match button element against button patterns.
        
        Args:
            element: Button element to analyze
            
        Returns:
            Tuple of (ButtonType, confidence_score)
        """
        text = element.get_text().lower()
        confidence_scores = {}
        
        # Match against each button type pattern
        for button_type, patterns in self.patterns['button_patterns'].items():
            matches = 0
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    matches += 1
            
            confidence_scores[button_type] = matches / len(patterns)
        
        # Find the best match
        best_type = max(confidence_scores, key=confidence_scores.get)
        best_score = confidence_scores[best_type]
        
        # Map pattern names to ButtonType enum
        type_mapping = {
            'accept_patterns': ButtonType.ACCEPT,
            'reject_patterns': ButtonType.REJECT,
            'manage_patterns': ButtonType.MANAGE,
            'close_patterns': ButtonType.CLOSE
        }
        
        button_type = type_mapping.get(best_type, ButtonType.ACCEPT)
        
        return button_type, best_score
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of consent banner text.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Detected language code
        """
        text_lower = text.lower()
        
        language_scores = {}
        
        for language, keywords in self.language_patterns.items():
            score = 0
            total_keywords = sum(len(kw_list) for kw_list in keywords.values())
            
            for category, kw_list in keywords.items():
                for keyword in kw_list:
                    if keyword in text_lower:
                        score += 1
            
            language_scores[language] = score / total_keywords
        
        # Return the language with the highest score
        return max(language_scores, key=language_scores.get) if language_scores else 'english'
    
    def find_consent_keywords(self, text: str) -> List[str]:
        """
        Find consent-related keywords in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of found keywords
        """
        found_keywords = []
        text_lower = text.lower()
        
        # Flatten all patterns
        all_patterns = []
        for category in self.patterns['banner_indicators']['text_patterns']:
            all_patterns.append(category)
        
        for pattern in all_patterns:
            # Extract keyword from regex pattern
            keyword = pattern.replace(r'\b', '').replace(r'\s+', ' ')
            if keyword in text_lower and keyword not in found_keywords:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def calculate_pattern_confidence(self, element: Tag) -> float:
        """
        Calculate overall pattern matching confidence for an element.
        
        Args:
            element: Element to analyze
            
        Returns:
            Confidence score between 0 and 1
        """
        scores = self.match_banner_patterns(element)
        
        # Apply additional confidence factors
        confidence = scores['overall_score']
        
        # Boost confidence for elements with multiple indicators
        indicator_count = sum(1 for score in scores.values() if score > 0)
        confidence += (indicator_count - 1) * 0.1
        
        # Boost confidence for elements with buttons
        buttons = element.find_all(['button', 'a', 'input'])
        if buttons:
            confidence += 0.15
        
        # Boost confidence for visible elements
        if self._is_element_visible(element):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _is_element_visible(self, element: Tag) -> bool:
        """Check if an element is likely visible."""
        style = element.get('style', '')
        
        # Check for hidden styles
        hidden_styles = ['display: none', 'visibility: hidden', 'opacity: 0']
        if any(hidden in style for hidden in hidden_styles):
            return False
        
        # Check for hidden classes
        classes = element.get('class', [])
        hidden_classes = ['hidden', 'invisible', 'sr-only']
        if any(cls in hidden_classes for cls in classes):
            return False
        
        # Check for aria-hidden
        if element.get('aria-hidden') == 'true':
            return False
        
        return True
    
    def get_pattern_summary(self, element: Tag) -> Dict:
        """
        Get a summary of pattern matching results for an element.
        
        Args:
            element: Element to analyze
            
        Returns:
            Dictionary with pattern matching summary
        """
        scores = self.match_banner_patterns(element)
        
        # Find consent keywords
        text = element.get_text()
        keywords = self.find_consent_keywords(text)
        
        # Detect language
        language = self.detect_language(text)
        
        # Analyze buttons
        buttons = element.find_all(['button', 'a', 'input'])
        button_types = []
        for button in buttons:
            button_type, _ = self.match_button_patterns(button)
            button_types.append(button_type.value)
        
        return {
            'overall_confidence': scores['overall_score'],
            'pattern_scores': scores,
            'found_keywords': keywords,
            'detected_language': language,
            'button_types': button_types,
            'is_visible': self._is_element_visible(element),
            'has_buttons': len(buttons) > 0
        }
