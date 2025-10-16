"""
Prompt builder for LLM interactions in banner analysis.
"""

from typing import Dict, List, Optional, Any
from ..models import BannerInfo, ButtonType, BannerType


class PromptBuilder:
    """Builds optimized prompts for LLM interactions."""
    
    def __init__(self):
        """Initialize the prompt builder."""
        self.system_prompts = self._initialize_system_prompts()
        self.templates = self._initialize_templates()
    
    def _initialize_system_prompts(self) -> Dict[str, str]:
        """Initialize system prompts for different tasks."""
        return {
            'selector_extraction': "You are an expert web developer specializing in cookie consent banner detection and CSS selector generation.",
            'banner_analysis': "You are an expert in web privacy, cookie consent management, and user experience analysis.",
            'rule_generation': "You are an expert in creating automated consent management rules for browser extensions.",
            'testing': "You are an expert in web automation testing and consent banner validation.",
            'comparison': "You are an expert in comparing and evaluating consent banner implementations."
        }
    
    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize prompt templates for different tasks."""
        return {
            'selector_extraction': """
Analyze the HTML content below and extract reliable CSS selectors for consent banner elements.

HTML Content:
```
{html_content}
```

{context}

Extract selectors for:
1. Banner container (main consent popup/banner)
2. Accept button (accept all cookies)
3. Reject button (reject non-essential cookies)
4. Manage button (access cookie preferences)
5. Close button (close/dismiss banner)
6. Overlay elements (background overlays to hide)

Requirements:
- Use specific, stable selectors (prefer IDs, data attributes, ARIA labels)
- Avoid overly generic selectors
- Provide multiple options when possible
- Focus on reliability across page loads

Respond with JSON:
{{
    "banner": "CSS selector for banner container",
    "acceptButton": "CSS selector for accept button",
    "rejectButton": "CSS selector for reject button",
    "manageButton": "CSS selector for manage button",
    "closeButton": "CSS selector for close button",
    "overlay": ["overlay selector 1", "overlay selector 2"]
}}
""",
            
            'banner_analysis': """
Analyze this cookie consent banner and provide comprehensive insights.

HTML Content:
```
{html_content}
```

{context}

Analyze:
1. Banner type and structure
2. Button functionality and purposes
3. Compliance level (GDPR, CCPA, etc.)
4. User experience assessment
5. Technical implementation quality
6. Potential issues or concerns
7. Recommendations for improvement

Respond in JSON format:
{{
    "banner_type": "modal|bottom_bar|top_bar|sidebar|other",
    "structure": {{
        "container": "description",
        "layout": "description",
        "styling": "description"
    }},
    "buttons": {{
        "accept": "description",
        "reject": "description",
        "manage": "description",
        "close": "description"
    }},
    "compliance": {{
        "gdpr_compliant": true/false,
        "ccpa_compliant": true/false,
        "compliance_level": "high|medium|low",
        "issues": ["issue1", "issue2"]
    }},
    "user_experience": {{
        "clarity": "high|medium|low",
        "accessibility": "high|medium|low",
        "usability": "high|medium|low",
        "issues": ["issue1", "issue2"]
    }},
    "technical_quality": {{
        "implementation": "good|fair|poor",
        "performance": "good|fair|poor",
        "maintainability": "good|fair|poor",
        "issues": ["issue1", "issue2"]
    }},
    "recommendations": ["rec1", "rec2"],
    "overall_score": 0-100
}}
""",
            
            'rule_generation': """
Generate Consent O Matic compatible rules for this consent banner.

Banner Information:
{context}

Create rules that:
1. Reliably detect the banner
2. Handle button interactions appropriately
3. Hide banner and overlays effectively
4. Follow Consent O Matic best practices

Respond with JSON:
{{
    "site": "example.com",
    "selectors": {{
        "banner": "banner selector",
        "acceptButton": "accept button selector",
        "rejectButton": "reject button selector",
        "manageButton": "manage button selector",
        "closeButton": "close button selector",
        "overlay": ["overlay selectors"]
    }},
    "actions": ["action1", "action2"],
    "metadata": {{
        "confidence": 0.0-1.0,
        "banner_type": "type",
        "tested": false
    }}
}}
""",
            
            'testing': """
Generate comprehensive test scenarios for this consent banner.

Banner Information:
{context}

Create test scenarios covering:
1. Banner detection
2. Button interactions
3. Banner hiding
4. Edge cases
5. Performance testing

Respond with JSON:
{{
    "test_scenarios": [
        {{
            "name": "scenario_name",
            "description": "description",
            "steps": ["step1", "step2"],
            "expected_result": "expected outcome",
            "priority": "high|medium|low"
        }}
    ]
}}
"""
        }
    
    def build_selector_extraction_prompt(self, html_content: str, banner_info: BannerInfo = None) -> str:
        """Build prompt for selector extraction."""
        template = self.templates['selector_extraction']
        context = self._build_context_string(banner_info)
        
        return template.format(
            html_content=html_content[:4000],  # Limit content size
            context=context
        )
    
    def build_banner_analysis_prompt(self, html_content: str, banner_info: BannerInfo = None) -> str:
        """Build prompt for banner analysis."""
        template = self.templates['banner_analysis']
        context = self._build_context_string(banner_info)
        
        return template.format(
            html_content=html_content[:4000],
            context=context
        )
    
    def build_rule_generation_prompt(self, banner_info: BannerInfo, site_url: str = None) -> str:
        """Build prompt for rule generation."""
        template = self.templates['rule_generation']
        context = self._build_detailed_context_string(banner_info, site_url)
        
        return template.format(context=context)
    
    def build_testing_prompt(self, banner_info: BannerInfo) -> str:
        """Build prompt for test scenario generation."""
        template = self.templates['testing']
        context = self._build_detailed_context_string(banner_info)
        
        return template.format(context=context)
    
    def build_comparison_prompt(self, banner1_info: BannerInfo, banner2_info: BannerInfo) -> str:
        """Build prompt for banner comparison."""
        return f"""
Compare these two cookie consent banners and provide detailed analysis:

Banner 1:
{self._build_detailed_context_string(banner1_info)}

Banner 2:
{self._build_detailed_context_string(banner2_info)}

Provide comparison in JSON format:
{{
    "similarities": ["similarity1", "similarity2"],
    "differences": ["difference1", "difference2"],
    "better_banner": "banner1|banner2|tie",
    "reasons": ["reason1", "reason2"],
    "recommendations": ["recommendation1", "recommendation2"],
    "score_comparison": {{
        "banner1_score": 0-100,
        "banner2_score": 0-100,
        "winner": "banner1|banner2|tie"
    }}
}}
"""
    
    def build_improvement_prompt(self, banner_info: BannerInfo, current_selectors: Dict[str, str]) -> str:
        """Build prompt for selector improvement."""
        return f"""
Improve these CSS selectors for better reliability and specificity.

Current Banner Information:
{self._build_detailed_context_string(banner_info)}

Current Selectors:
```json
{json.dumps(current_selectors, indent=2)}
```

Improve selectors to be:
1. More specific and reliable
2. Less likely to break with minor changes
3. Prefer IDs, data attributes, ARIA labels
4. Include fallback options

Respond with improved selectors in JSON format:
{{
    "banner": "improved banner selector",
    "acceptButton": "improved accept button selector",
    "rejectButton": "improved reject button selector",
    "manageButton": "improved manage button selector",
    "closeButton": "improved close button selector",
    "overlay": ["improved overlay selectors"]
}}
"""
    
    def _build_context_string(self, banner_info: BannerInfo) -> str:
        """Build context string for prompts."""
        if not banner_info:
            return ""
        
        context_parts = []
        
        if banner_info.site:
            context_parts.append(f"Site: {banner_info.site}")
        
        if banner_info.banner_type:
            context_parts.append(f"Banner Type: {banner_info.banner_type.value}")
        
        if banner_info.detection_confidence is not None:
            context_parts.append(f"Confidence Score: {banner_info.detection_confidence:.2f}")
        
        if banner_info.buttons:
            button_types = [b.button_type.value for b in banner_info.buttons]
            context_parts.append(f"Buttons Found: {button_types}")
        
        if banner_info.container_selector:
            context_parts.append(f"Container Selector: {banner_info.container_selector}")
        
        if banner_info.overlay_selectors:
            context_parts.append(f"Overlay Selectors: {banner_info.overlay_selectors}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def _build_detailed_context_string(self, banner_info: BannerInfo, site_url: str = None) -> str:
        """Build detailed context string for prompts."""
        context_parts = []
        
        if site_url:
            context_parts.append(f"Site URL: {site_url}")
        elif banner_info.site:
            context_parts.append(f"Site: {banner_info.site}")
        
        if banner_info.banner_type:
            context_parts.append(f"Banner Type: {banner_info.banner_type.value}")
        
        if banner_info.detection_confidence is not None:
            context_parts.append(f"Detection Confidence: {banner_info.detection_confidence:.2f}")
        
        if banner_info.container_selector:
            context_parts.append(f"Container Selector: {banner_info.container_selector}")
        
        if banner_info.buttons:
            context_parts.append("Buttons:")
            for button in banner_info.buttons:
                context_parts.append(f"  - {button.button_type.value}: {button.text} (selector: {button.selector})")
        
        if banner_info.overlay_selectors:
            context_parts.append(f"Overlay Selectors: {banner_info.overlay_selectors}")
        
        if banner_info.additional_selectors:
            context_parts.append("Additional Selectors:")
            for key, value in banner_info.additional_selectors.items():
                context_parts.append(f"  - {key}: {value}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def build_system_prompt(self, task_type: str) -> str:
        """Build system prompt for a specific task type."""
        return self.system_prompts.get(task_type, self.system_prompts['banner_analysis'])
    
    def build_custom_prompt(self, template: str, **kwargs) -> str:
        """Build custom prompt using a template."""
        return template.format(**kwargs)
    
    def optimize_prompt_length(self, prompt: str, max_tokens: int = 4000) -> str:
        """Optimize prompt length to fit within token limits."""
        # This is a simplified implementation
        # In practice, you might want to use token counting libraries
        
        if len(prompt) <= max_tokens:
            return prompt
        
        # Truncate HTML content if present
        if "HTML Content:" in prompt:
            parts = prompt.split("HTML Content:")
            if len(parts) > 1:
                html_part = parts[1]
                if len(html_part) > 2000:
                    html_part = html_part[:2000] + "...\n[Content truncated]"
                    prompt = parts[0] + "HTML Content:" + html_part
        
        return prompt
    
    def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """Validate a prompt for completeness and quality."""
        validation = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Check for required elements
        if not prompt.strip():
            validation['errors'].append("Prompt is empty")
            validation['valid'] = False
        
        if len(prompt) < 100:
            validation['warnings'].append("Prompt seems too short")
        
        if len(prompt) > 8000:
            validation['warnings'].append("Prompt might be too long")
        
        # Check for JSON format requests
        if 'JSON' in prompt.upper() and 'format' in prompt.lower():
            if '{' not in prompt or '}' not in prompt:
                validation['warnings'].append("Requests JSON format but doesn't show example structure")
        
        # Check for context
        if 'html_content' in prompt.lower() and '<' not in prompt:
            validation['warnings'].append("References HTML content but none provided")
        
        return validation
