"""
Pattern analyzer for finding common patterns across multiple consent banners.
"""

import re
from typing import List, Dict, Any, Tuple, Set
from collections import Counter, defaultdict
from dataclasses import dataclass
from ..models import BannerInfo


@dataclass
class PatternGroup:
    """Represents a group of similar patterns."""
    pattern_id: str
    pattern_type: str
    common_elements: List[str]
    sites: List[str]
    similarity_score: float
    confidence: float
    examples: List[Dict[str, Any]]


@dataclass
class PatternMatch:
    """Represents a pattern match between banners."""
    banner1: str
    banner2: str
    similarity_score: float
    common_selectors: List[str]
    common_button_texts: List[str]
    common_attributes: List[str]


class PatternAnalyzer:
    """Analyzes patterns across multiple consent banners to find commonalities."""
    
    def __init__(self):
        """Initialize the pattern analyzer."""
        self.selector_patterns = self._initialize_selector_patterns()
        self.button_patterns = self._initialize_button_patterns()
        self.structural_patterns = self._initialize_structural_patterns()
    
    def _initialize_selector_patterns(self) -> Dict[str, List[str]]:
        """Initialize common selector patterns."""
        return {
            'id_patterns': [
                r'cookie', r'consent', r'gdpr', r'privacy', r'banner', r'notice',
                r'accept', r'decline', r'settings', r'preferences'
            ],
            'class_patterns': [
                r'cookie', r'consent', r'gdpr', r'privacy', r'banner', r'notice',
                r'modal', r'overlay', r'popup', r'dialog', r'widget'
            ],
            'data_attribute_patterns': [
                r'data-consent', r'data-cookie', r'data-gdpr', r'data-privacy',
                r'data-banner', r'data-notice', r'data-accept', r'data-decline'
            ]
        }
    
    def _initialize_button_patterns(self) -> Dict[str, List[str]]:
        """Initialize common button text patterns."""
        return {
            'accept_patterns': [
                r'accept', r'agree', r'allow', r'ok', r'continue', r'proceed',
                r'got it', r'understood', r'accept all', r'allow all'
            ],
            'decline_patterns': [
                r'decline', r'reject', r'deny', r'no', r'refuse', r'block',
                r'necessary only', r'essential only', r'decline all'
            ],
            'manage_patterns': [
                r'manage', r'preferences', r'settings', r'options', r'customize',
                r'choose', r'select', r'configure', r'control'
            ]
        }
    
    def _initialize_structural_patterns(self) -> Dict[str, List[str]]:
        """Initialize structural patterns."""
        return {
            'container_patterns': [
                r'modal', r'overlay', r'popup', r'dialog', r'banner', r'bar',
                r'notice', r'widget', r'container', r'wrapper'
            ],
            'positioning_patterns': [
                r'fixed', r'absolute', r'sticky', r'top', r'bottom', r'center',
                r'overlay', r'floating', r'z-index'
            ],
            'visibility_patterns': [
                r'visible', r'hidden', r'show', r'hide', r'display', r'opacity'
            ]
        }
    
    def find_common_patterns(self, banners: List[BannerInfo]) -> List[PatternGroup]:
        """
        Find common patterns across multiple banners.
        
        Args:
            banners: List of BannerInfo objects to analyze
            
        Returns:
            List of PatternGroup objects representing common patterns
        """
        if len(banners) < 2:
            return []
        
        pattern_groups = []
        
        # Analyze selector patterns
        selector_groups = self._analyze_selector_patterns(banners)
        pattern_groups.extend(selector_groups)
        
        # Analyze button patterns
        button_groups = self._analyze_button_patterns(banners)
        pattern_groups.extend(button_groups)
        
        # Analyze structural patterns
        structural_groups = self._analyze_structural_patterns(banners)
        pattern_groups.extend(structural_groups)
        
        # Analyze CMP-specific patterns
        cmp_groups = self._analyze_cmp_patterns(banners)
        pattern_groups.extend(cmp_groups)
        
        return pattern_groups
    
    def _analyze_selector_patterns(self, banners: List[BannerInfo]) -> List[PatternGroup]:
        """Analyze common selector patterns."""
        groups = []
        
        # Group banners by similar selectors
        selector_groups = defaultdict(list)
        
        for banner in banners:
            # Extract selector patterns
            container_selector = banner.container_selector
            selector_patterns = self._extract_selector_patterns(container_selector)
            
            for pattern in selector_patterns:
                selector_groups[pattern].append(banner)
        
        # Create pattern groups for selectors with multiple matches
        for pattern, matching_banners in selector_groups.items():
            if len(matching_banners) >= 2:
                group = PatternGroup(
                    pattern_id=f"selector_{pattern}",
                    pattern_type="selector",
                    common_elements=[pattern],
                    sites=[banner.site for banner in matching_banners],
                    similarity_score=self._calculate_selector_similarity(matching_banners),
                    confidence=self._calculate_confidence(matching_banners),
                    examples=self._get_selector_examples(matching_banners, pattern)
                )
                groups.append(group)
        
        return groups
    
    def _analyze_button_patterns(self, banners: List[BannerInfo]) -> List[PatternGroup]:
        """Analyze common button patterns."""
        groups = []
        
        # Group banners by button text patterns
        button_groups = defaultdict(list)
        
        for banner in banners:
            for button in banner.buttons:
                button_text = button.text.lower()
                button_patterns = self._extract_button_patterns(button_text)
                
                for pattern in button_patterns:
                    button_groups[pattern].append((banner, button))
        
        # Create pattern groups for button patterns with multiple matches
        for pattern, button_matches in button_groups.items():
            if len(button_matches) >= 2:
                matching_banners = [match[0] for match in button_matches]
                
                group = PatternGroup(
                    pattern_id=f"button_{pattern}",
                    pattern_type="button",
                    common_elements=[pattern],
                    sites=[banner.site for banner in matching_banners],
                    similarity_score=self._calculate_button_similarity(button_matches),
                    confidence=self._calculate_confidence(matching_banners),
                    examples=self._get_button_examples(button_matches, pattern)
                )
                groups.append(group)
        
        return groups
    
    def _analyze_structural_patterns(self, banners: List[BannerInfo]) -> List[PatternGroup]:
        """Analyze common structural patterns."""
        groups = []
        
        # Group banners by structural similarities
        structural_groups = defaultdict(list)
        
        for banner in banners:
            structural_features = self._extract_structural_features(banner)
            
            for feature in structural_features:
                structural_groups[feature].append(banner)
        
        # Create pattern groups for structural patterns with multiple matches
        for feature, matching_banners in structural_groups.items():
            if len(matching_banners) >= 2:
                group = PatternGroup(
                    pattern_id=f"structural_{feature}",
                    pattern_type="structural",
                    common_elements=[feature],
                    sites=[banner.site for banner in matching_banners],
                    similarity_score=self._calculate_structural_similarity(matching_banners),
                    confidence=self._calculate_confidence(matching_banners),
                    examples=self._get_structural_examples(matching_banners, feature)
                )
                groups.append(group)
        
        return groups
    
    def _analyze_cmp_patterns(self, banners: List[BannerInfo]) -> List[PatternGroup]:
        """Analyze CMP-specific patterns."""
        groups = []
        
        # Group banners by CMP type
        cmp_groups = defaultdict(list)
        
        for banner in banners:
            cmp_type = getattr(banner, 'cmp_type', 'unknown')
            if cmp_type and cmp_type != 'unknown':
                cmp_groups[cmp_type].append(banner)
        
        # Create pattern groups for CMP types with multiple banners
        for cmp_type, matching_banners in cmp_groups.items():
            if len(matching_banners) >= 2:
                group = PatternGroup(
                    pattern_id=f"cmp_{cmp_type}",
                    pattern_type="cmp",
                    common_elements=[cmp_type],
                    sites=[banner.site for banner in matching_banners],
                    similarity_score=self._calculate_cmp_similarity(matching_banners),
                    confidence=self._calculate_confidence(matching_banners),
                    examples=self._get_cmp_examples(matching_banners, cmp_type)
                )
                groups.append(group)
        
        return groups
    
    def _extract_selector_patterns(self, selector: str) -> List[str]:
        """Extract patterns from a CSS selector."""
        patterns = []
        
        # Check for ID patterns
        for pattern in self.selector_patterns['id_patterns']:
            if re.search(pattern, selector, re.IGNORECASE):
                patterns.append(f"id_{pattern}")
        
        # Check for class patterns
        for pattern in self.selector_patterns['class_patterns']:
            if re.search(pattern, selector, re.IGNORECASE):
                patterns.append(f"class_{pattern}")
        
        # Check for data attribute patterns
        for pattern in self.selector_patterns['data_attribute_patterns']:
            if re.search(pattern, selector, re.IGNORECASE):
                patterns.append(f"data_{pattern}")
        
        return patterns
    
    def _extract_button_patterns(self, button_text: str) -> List[str]:
        """Extract patterns from button text."""
        patterns = []
        
        # Check for accept patterns
        for pattern in self.button_patterns['accept_patterns']:
            if re.search(pattern, button_text, re.IGNORECASE):
                patterns.append(f"accept_{pattern}")
        
        # Check for decline patterns
        for pattern in self.button_patterns['decline_patterns']:
            if re.search(pattern, button_text, re.IGNORECASE):
                patterns.append(f"decline_{pattern}")
        
        # Check for manage patterns
        for pattern in self.button_patterns['manage_patterns']:
            if re.search(pattern, button_text, re.IGNORECASE):
                patterns.append(f"manage_{pattern}")
        
        return patterns
    
    def _extract_structural_features(self, banner: BannerInfo) -> List[str]:
        """Extract structural features from a banner."""
        features = []
        
        # Banner type
        features.append(f"type_{banner.banner_type.value}")
        
        # Overlay selectors
        if banner.overlay_selectors:
            features.append("has_overlay")
        
        # Button count
        button_count = len(banner.buttons)
        if button_count <= 2:
            features.append("simple_buttons")
        elif button_count <= 4:
            features.append("moderate_buttons")
        else:
            features.append("complex_buttons")
        
        # Button types
        button_types = {button.button_type.value for button in banner.buttons}
        for button_type in button_types:
            features.append(f"has_{button_type}_button")
        
        return features
    
    def _calculate_selector_similarity(self, banners: List[BannerInfo]) -> float:
        """Calculate similarity score for selector patterns."""
        if len(banners) < 2:
            return 0.0
        
        # Extract all selectors
        selectors = [banner.container_selector for banner in banners]
        
        # Calculate similarity based on common patterns
        common_patterns = 0
        total_patterns = 0
        
        for selector in selectors:
            patterns = self._extract_selector_patterns(selector)
            total_patterns += len(patterns)
        
        # Find common patterns across all selectors
        all_patterns = []
        for selector in selectors:
            all_patterns.extend(self._extract_selector_patterns(selector))
        
        pattern_counts = Counter(all_patterns)
        common_patterns = sum(1 for count in pattern_counts.values() if count > 1)
        
        return common_patterns / total_patterns if total_patterns > 0 else 0.0
    
    def _calculate_button_similarity(self, button_matches: List[Tuple[BannerInfo, Any]]) -> float:
        """Calculate similarity score for button patterns."""
        if len(button_matches) < 2:
            return 0.0
        
        # Extract button texts
        button_texts = [match[1].text.lower() for match in button_matches]
        
        # Calculate similarity based on common patterns
        common_patterns = 0
        total_patterns = 0
        
        for button_text in button_texts:
            patterns = self._extract_button_patterns(button_text)
            total_patterns += len(patterns)
        
        # Find common patterns
        all_patterns = []
        for button_text in button_texts:
            all_patterns.extend(self._extract_button_patterns(button_text))
        
        pattern_counts = Counter(all_patterns)
        common_patterns = sum(1 for count in pattern_counts.values() if count > 1)
        
        return common_patterns / total_patterns if total_patterns > 0 else 0.0
    
    def _calculate_structural_similarity(self, banners: List[BannerInfo]) -> float:
        """Calculate similarity score for structural patterns."""
        if len(banners) < 2:
            return 0.0
        
        # Extract structural features
        all_features = []
        for banner in banners:
            all_features.extend(self._extract_structural_features(banner))
        
        # Calculate similarity based on common features
        feature_counts = Counter(all_features)
        common_features = sum(1 for count in feature_counts.values() if count > 1)
        total_features = len(all_features)
        
        return common_features / total_features if total_features > 0 else 0.0
    
    def _calculate_cmp_similarity(self, banners: List[BannerInfo]) -> float:
        """Calculate similarity score for CMP patterns."""
        if len(banners) < 2:
            return 0.0
        
        # All banners should have the same CMP type
        cmp_types = [getattr(banner, 'cmp_type', 'unknown') for banner in banners]
        unique_cmp_types = set(cmp_types)
        
        # Higher similarity if all banners use the same CMP
        if len(unique_cmp_types) == 1:
            return 1.0
        else:
            return 0.5  # Partial similarity for mixed CMPs
    
    def _calculate_confidence(self, banners: List[BannerInfo]) -> float:
        """Calculate confidence score for a pattern group."""
        if not banners:
            return 0.0
        
        # Base confidence on number of matching banners
        base_confidence = min(len(banners) / 5.0, 1.0)  # Max confidence at 5+ banners
        
        # Boost confidence for high-quality banners
        avg_confidence = sum(banner.detection_confidence for banner in banners) / len(banners)
        quality_boost = avg_confidence * 0.3
        
        return min(base_confidence + quality_boost, 1.0)
    
    def _get_selector_examples(self, banners: List[BannerInfo], pattern: str) -> List[Dict[str, Any]]:
        """Get examples of selector patterns."""
        examples = []
        
        for banner in banners:
            if pattern in banner.container_selector:
                examples.append({
                    "site": banner.site,
                    "selector": banner.container_selector,
                    "confidence": banner.detection_confidence
                })
        
        return examples
    
    def _get_button_examples(self, button_matches: List[Tuple[BannerInfo, Any]], pattern: str) -> List[Dict[str, Any]]:
        """Get examples of button patterns."""
        examples = []
        
        for banner, button in button_matches:
            if pattern in button.text.lower():
                examples.append({
                    "site": banner.site,
                    "button_text": button.text,
                    "button_type": button.button_type.value,
                    "selector": button.selector
                })
        
        return examples
    
    def _get_structural_examples(self, banners: List[BannerInfo], feature: str) -> List[Dict[str, Any]]:
        """Get examples of structural patterns."""
        examples = []
        
        for banner in banners:
            if feature in self._extract_structural_features(banner):
                examples.append({
                    "site": banner.site,
                    "banner_type": banner.banner_type.value,
                    "button_count": len(banner.buttons),
                    "has_overlay": len(banner.overlay_selectors) > 0
                })
        
        return examples
    
    def _get_cmp_examples(self, banners: List[BannerInfo], cmp_type: str) -> List[Dict[str, Any]]:
        """Get examples of CMP patterns."""
        examples = []
        
        for banner in banners:
            banner_cmp_type = getattr(banner, 'cmp_type', 'unknown')
            if banner_cmp_type == cmp_type:
                examples.append({
                    "site": banner.site,
                    "cmp_type": banner_cmp_type,
                    "confidence": getattr(banner, 'cmp_confidence', 0.0),
                    "indicators": getattr(banner, 'cmp_indicators', [])
                })
        
        return examples
    
    def generate_pattern_report(self, pattern_groups: List[PatternGroup]) -> Dict[str, Any]:
        """Generate a comprehensive pattern analysis report."""
        report = {
            "total_patterns": len(pattern_groups),
            "patterns_by_type": {},
            "high_confidence_patterns": [],
            "recommendations": [],
            "coverage_analysis": {}
        }
        
        # Group patterns by type
        for group in pattern_groups:
            pattern_type = group.pattern_type
            if pattern_type not in report["patterns_by_type"]:
                report["patterns_by_type"][pattern_type] = []
            report["patterns_by_type"][pattern_type].append(group)
        
        # Find high-confidence patterns
        report["high_confidence_patterns"] = [
            group for group in pattern_groups 
            if group.confidence >= 0.8
        ]
        
        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(pattern_groups)
        
        # Coverage analysis
        report["coverage_analysis"] = self._analyze_coverage(pattern_groups)
        
        return report
    
    def _generate_recommendations(self, pattern_groups: List[PatternGroup]) -> List[str]:
        """Generate recommendations based on pattern analysis."""
        recommendations = []
        
        # Check for high-confidence patterns
        high_confidence_count = len([g for g in pattern_groups if g.confidence >= 0.8])
        if high_confidence_count > 0:
            recommendations.append(f"Found {high_confidence_count} high-confidence patterns that can be used for multi-site rules")
        
        # Check for CMP-specific patterns
        cmp_patterns = [g for g in pattern_groups if g.pattern_type == "cmp"]
        if cmp_patterns:
            recommendations.append("Consider creating CMP-specific rule templates for better accuracy")
        
        # Check for common button patterns
        button_patterns = [g for g in pattern_groups if g.pattern_type == "button"]
        if button_patterns:
            recommendations.append("Common button patterns found - can be used for generic button detection")
        
        return recommendations
    
    def _analyze_coverage(self, pattern_groups: List[PatternGroup]) -> Dict[str, Any]:
        """Analyze pattern coverage across sites."""
        coverage = {
            "total_sites": set(),
            "sites_with_patterns": set(),
            "pattern_density": {},
            "gaps": []
        }
        
        # Collect all sites
        for group in pattern_groups:
            coverage["total_sites"].update(group.sites)
            coverage["sites_with_patterns"].update(group.sites)
        
        # Calculate pattern density per site
        for site in coverage["total_sites"]:
            site_patterns = [g for g in pattern_groups if site in g.sites]
            coverage["pattern_density"][site] = len(site_patterns)
        
        # Convert sets to lists for JSON serialization
        coverage["total_sites"] = list(coverage["total_sites"])
        coverage["sites_with_patterns"] = list(coverage["sites_with_patterns"])
        
        return coverage
