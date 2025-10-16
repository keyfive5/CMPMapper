"""
LLM-based selector extraction for consent banners.
"""

import os
import json
from typing import Dict, List, Optional, Any, Tuple
from bs4 import BeautifulSoup

try:
    import openai
except ImportError:
    openai = None

from ..models import BannerInfo, ButtonType


class LLMSelectorExtractor:
    """Uses LLM to extract and improve CSS selectors for consent banners."""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the LLM selector extractor.
        
        Args:
            api_key: OpenAI API key
            model: LLM model to use
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.client = None
        
        if openai and self.api_key:
            try:
                openai.api_key = self.api_key
                self.client = openai
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
        else:
            print("Warning: OpenAI not available or API key not provided")
    
    def extract_selectors(self, html_content: str, banner_info: BannerInfo = None) -> Dict[str, str]:
        """
        Extract CSS selectors using LLM analysis.
        
        Args:
            html_content: HTML content to analyze
            banner_info: Optional BannerInfo object for context
            
        Returns:
            Dictionary of extracted selectors
        """
        if not self.client:
            return self._fallback_extraction(html_content)
        
        try:
            # Prepare prompt
            prompt = self._build_selector_extraction_prompt(html_content, banner_info)
            
            # Call LLM
            response = self._call_llm(prompt)
            
            # Parse response
            selectors = self._parse_selector_response(response)
            
            return selectors
            
        except Exception as e:
            print(f"Error extracting selectors with LLM: {e}")
            return self._fallback_extraction(html_content)
    
    def _build_selector_extraction_prompt(self, html_content: str, banner_info: BannerInfo = None) -> str:
        """Build prompt for selector extraction."""
        prompt = """
You are an expert web developer specializing in cookie consent banner detection. 
I need you to analyze the HTML content below and extract CSS selectors for consent banner elements.

Please identify and provide CSS selectors for:
1. Banner container (the main consent popup/banner)
2. Accept button (button to accept all cookies)
3. Reject button (button to reject non-essential cookies)
4. Manage button (button to access cookie preferences)
5. Close button (button to close/dismiss the banner)
6. Overlay elements (background overlays that should be hidden)

Requirements:
- Use specific, reliable selectors (prefer IDs, data attributes, ARIA labels)
- Avoid overly generic selectors like just "button" or "div"
- Provide multiple selector options separated by commas when possible
- Focus on selectors that are likely to be stable across page loads

HTML Content:
```
{html_content}
```

Please respond with a JSON object in this format:
{{
    "banner": "CSS selector for banner container",
    "acceptButton": "CSS selector for accept button",
    "rejectButton": "CSS selector for reject button", 
    "manageButton": "CSS selector for manage button",
    "closeButton": "CSS selector for close button",
    "overlay": ["CSS selector for overlay 1", "CSS selector for overlay 2"]
}}
"""
        
        # Add context if banner info is available
        if banner_info:
            prompt += f"\n\nAdditional Context:\n"
            prompt += f"- Detected banner type: {banner_info.banner_type.value}\n"
            prompt += f"- Confidence score: {banner_info.detection_confidence}\n"
            prompt += f"- Found buttons: {[b.button_type.value for b in banner_info.buttons]}\n"
        
        return prompt.format(html_content=html_content[:4000])  # Limit content size
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the given prompt."""
        try:
            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert web developer specializing in cookie consent banner detection."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return ""
    
    def _parse_selector_response(self, response: str) -> Dict[str, str]:
        """Parse LLM response to extract selectors."""
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                selectors = json.loads(json_str)
                
                # Validate and clean selectors
                cleaned_selectors = {}
                for key, value in selectors.items():
                    if isinstance(value, list):
                        cleaned_selectors[key] = value
                    elif isinstance(value, str) and value.strip():
                        cleaned_selectors[key] = value.strip()
                
                return cleaned_selectors
            
        except json.JSONDecodeError:
            pass
        
        # Fallback: try to extract selectors using text parsing
        return self._extract_selectors_from_text(response)
    
    def _extract_selectors_from_text(self, text: str) -> Dict[str, str]:
        """Extract selectors from text when JSON parsing fails."""
        selectors = {}
        
        # Look for common selector patterns
        import re
        
        patterns = {
            'banner': r'banner[:\s]*["\']([^"\']+)["\']',
            'acceptButton': r'accept[^:]*[:\s]*["\']([^"\']+)["\']',
            'rejectButton': r'reject[^:]*[:\s]*["\']([^"\']+)["\']',
            'manageButton': r'manage[^:]*[:\s]*["\']([^"\']+)["\']',
            'closeButton': r'close[^:]*[:\s]*["\']([^"\']+)["\']'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                selectors[key] = match.group(1)
        
        return selectors
    
    def _fallback_extraction(self, html_content: str) -> Dict[str, str]:
        """Fallback selector extraction when LLM is not available."""
        selectors = {}
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find banner container
            banner_selectors = [
                "[id*='cookie']", "[class*='cookie']", "[id*='consent']", "[class*='consent']",
                "[id*='gdpr']", "[class*='gdpr']", ".cc-banner", ".cookie-banner", ".consent-banner"
            ]
            
            for selector in banner_selectors:
                try:
                    element = soup.select_one(selector)
                    if element:
                        selectors['banner'] = selector
                        break
                except Exception:
                    continue
            
            # Find buttons
            buttons = soup.find_all(['button', 'a', 'input'])
            for button in buttons:
                text = button.get_text().lower()
                
                if 'accept' in text or 'agree' in text:
                    if 'acceptButton' not in selectors:
                        selectors['acceptButton'] = self._generate_selector(button)
                
                if 'reject' in text or 'decline' in text:
                    if 'rejectButton' not in selectors:
                        selectors['rejectButton'] = self._generate_selector(button)
                
                if 'manage' in text or 'settings' in text:
                    if 'manageButton' not in selectors:
                        selectors['manageButton'] = self._generate_selector(button)
                
                if 'close' in text or '×' in text:
                    if 'closeButton' not in selectors:
                        selectors['closeButton'] = self._generate_selector(button)
            
        except Exception as e:
            print(f"Error in fallback extraction: {e}")
        
        return selectors
    
    def _generate_selector(self, element) -> str:
        """Generate a CSS selector for an element."""
        selectors = []
        
        # Try ID first
        if element.get('id'):
            selectors.append(f"#{element['id']}")
        
        # Try classes
        if element.get('class'):
            classes = '.'.join(element['class'])
            selectors.append(f".{classes}")
        
        # Try data attributes
        for attr, value in element.attrs.items():
            if attr.startswith('data-'):
                selectors.append(f"[{attr}='{value}']")
        
        # Fallback to tag
        if not selectors:
            selectors.append(element.name)
        
        return ', '.join(selectors)
    
    def improve_selectors(self, selectors: Dict[str, str], html_content: str) -> Dict[str, str]:
        """
        Use LLM to improve existing selectors.
        
        Args:
            selectors: Current selectors
            html_content: HTML content for analysis
            
        Returns:
            Improved selectors
        """
        if not self.client:
            return selectors
        
        try:
            prompt = self._build_selector_improvement_prompt(selectors, html_content)
            response = self._call_llm(prompt)
            improved_selectors = self._parse_selector_response(response)
            
            # Merge with original selectors
            merged_selectors = selectors.copy()
            for key, value in improved_selectors.items():
                if key in merged_selectors:
                    # Combine selectors
                    original = merged_selectors[key]
                    if isinstance(original, list):
                        if isinstance(value, list):
                            merged_selectors[key] = original + value
                        else:
                            merged_selectors[key] = original + [value]
                    else:
                        if isinstance(value, list):
                            merged_selectors[key] = [original] + value
                        else:
                            merged_selectors[key] = [original, value]
                else:
                    merged_selectors[key] = value
            
            return merged_selectors
            
        except Exception as e:
            print(f"Error improving selectors: {e}")
            return selectors
    
    def _build_selector_improvement_prompt(self, selectors: Dict[str, str], html_content: str) -> str:
        """Build prompt for selector improvement."""
        return f"""
You are an expert web developer. I have CSS selectors for a cookie consent banner, but I need you to improve them for better reliability and specificity.

Current selectors:
{json.dumps(selectors, indent=2)}

HTML content to analyze:
```
{html_content[:4000]}
```

Please provide improved selectors that are:
1. More specific and reliable
2. Less likely to break with minor page changes
3. Prefer IDs, data attributes, and ARIA labels over generic classes
4. Include fallback options when possible

Respond with a JSON object in the same format as the current selectors.
"""
    
    def analyze_banner_structure(self, html_content: str) -> Dict[str, Any]:
        """
        Use LLM to analyze banner structure and provide insights.
        
        Args:
            html_content: HTML content to analyze
            
        Returns:
            Analysis results
        """
        if not self.client:
            return {}
        
        try:
            prompt = f"""
Analyze this HTML content and identify the cookie consent banner structure:

```html
{html_content[:4000]}
```

Please provide:
1. Banner type (modal, bottom bar, top bar, etc.)
2. Key structural elements
3. Button functionality
4. Potential issues with the banner
5. Recommendations for selector reliability

Respond in JSON format:
{{
    "banner_type": "modal|bottom_bar|top_bar|sidebar",
    "structure": {{
        "container": "description",
        "buttons": ["button1", "button2"],
        "overlays": ["overlay1", "overlay2"]
    }},
    "functionality": {{
        "accept_action": "description",
        "reject_action": "description",
        "manage_action": "description"
    }},
    "issues": ["issue1", "issue2"],
    "recommendations": ["rec1", "rec2"]
}}
"""
            
            response = self._call_llm(prompt)
            
            # Try to parse JSON response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            
        except Exception as e:
            print(f"Error analyzing banner structure: {e}")
        
        return {}
    
    def generate_test_scenarios(self, banner_info: BannerInfo) -> List[Dict[str, Any]]:
        """
        Generate test scenarios for banner validation.
        
        Args:
            banner_info: BannerInfo object
            
        Returns:
            List of test scenarios
        """
        if not self.client:
            return []
        
        try:
            prompt = f"""
Based on this cookie consent banner information, generate comprehensive test scenarios:

Banner Type: {banner_info.banner_type.value}
Confidence Score: {banner_info.detection_confidence}
Buttons Found: {[b.button_type.value for b in banner_info.buttons]}
Container Selector: {banner_info.container_selector}

Generate test scenarios that cover:
1. Banner detection
2. Button interactions
3. Banner hiding
4. Edge cases
5. Performance testing

Respond in JSON format:
{{
    "test_scenarios": [
        {{
            "name": "scenario_name",
            "description": "scenario_description",
            "steps": ["step1", "step2"],
            "expected_result": "expected_outcome",
            "priority": "high|medium|low"
        }}
    ]
}}
"""
            
            response = self._call_llm(prompt)
            
            # Try to parse JSON response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                result = json.loads(json_str)
                return result.get('test_scenarios', [])
            
        except Exception as e:
            print(f"Error generating test scenarios: {e}")
        
        return []
