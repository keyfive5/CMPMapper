"""
LLM-based banner analysis for consent banner understanding.
"""

import json
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

try:
    import openai
except ImportError:
    openai = None

from ..models import BannerInfo, BannerType, ButtonType


class LLMBannerAnalyzer:
    """Uses LLM to analyze consent banners and provide insights."""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the LLM banner analyzer.
        
        Args:
            api_key: OpenAI API key
            model: LLM model to use
        """
        self.api_key = api_key
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
    
    def analyze_banner(self, html_content: str, banner_info: BannerInfo = None) -> Dict[str, Any]:
        """
        Analyze a consent banner using LLM.
        
        Args:
            html_content: HTML content containing the banner
            banner_info: Optional BannerInfo object for context
            
        Returns:
            Analysis results
        """
        if not self.client:
            return self._fallback_analysis(html_content, banner_info)
        
        try:
            prompt = self._build_banner_analysis_prompt(html_content, banner_info)
            response = self._call_llm(prompt)
            
            # Parse response
            analysis = self._parse_analysis_response(response)
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing banner with LLM: {e}")
            return self._fallback_analysis(html_content, banner_info)
    
    def _build_banner_analysis_prompt(self, html_content: str, banner_info: BannerInfo = None) -> str:
        """Build prompt for banner analysis."""
        prompt = """
You are an expert in web privacy and cookie consent management. Analyze the HTML content below and provide a comprehensive analysis of the cookie consent banner.

HTML Content:
```
{html_content}
```

Please analyze and provide:
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
        "container": "description of banner container",
        "layout": "description of banner layout",
        "styling": "description of banner styling approach"
    }},
    "buttons": {{
        "accept": "description of accept button",
        "reject": "description of reject button", 
        "manage": "description of manage button",
        "close": "description of close button"
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
    "recommendations": [
        "recommendation1",
        "recommendation2"
    ],
    "overall_score": 0-100
}}
"""
        
        # Add context if banner info is available
        if banner_info:
            prompt += f"\n\nAdditional Context:\n"
            prompt += f"- Detected banner type: {banner_info.banner_type.value}\n"
            prompt += f"- Confidence score: {banner_info.detection_confidence}\n"
            prompt += f"- Found buttons: {[b.button_type.value for b in banner_info.buttons]}\n"
            prompt += f"- Container selector: {banner_info.container_selector}\n"
        
        return prompt.format(html_content=html_content[:4000])
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the given prompt."""
        try:
            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in web privacy, cookie consent management, and user experience."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return ""
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response to extract analysis."""
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            
        except json.JSONDecodeError:
            pass
        
        # Fallback: return basic analysis
        return {
            "banner_type": "unknown",
            "structure": {"container": "unknown", "layout": "unknown", "styling": "unknown"},
            "buttons": {},
            "compliance": {"gdpr_compliant": False, "ccpa_compliant": False, "compliance_level": "low", "issues": []},
            "user_experience": {"clarity": "low", "accessibility": "low", "usability": "low", "issues": []},
            "technical_quality": {"implementation": "poor", "performance": "poor", "maintainability": "poor", "issues": []},
            "recommendations": ["Manual review required"],
            "overall_score": 0
        }
    
    def _fallback_analysis(self, html_content: str, banner_info: BannerInfo = None) -> Dict[str, Any]:
        """Fallback analysis when LLM is not available."""
        analysis = {
            "banner_type": "unknown",
            "structure": {"container": "unknown", "layout": "unknown", "styling": "unknown"},
            "buttons": {},
            "compliance": {"gdpr_compliant": False, "ccpa_compliant": False, "compliance_level": "low", "issues": []},
            "user_experience": {"clarity": "low", "accessibility": "low", "usability": "low", "issues": []},
            "technical_quality": {"implementation": "poor", "performance": "poor", "maintainability": "poor", "issues": []},
            "recommendations": ["LLM analysis not available"],
            "overall_score": 0
        }
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Basic banner type detection
            if banner_info:
                analysis["banner_type"] = banner_info.banner_type.value
                
                # Analyze buttons
                for button in banner_info.buttons:
                    button_type = button.button_type.value
                    analysis["buttons"][button_type] = {
                        "text": button.text,
                        "selector": button.selector,
                        "visible": button.is_visible
                    }
                
                # Basic compliance assessment
                has_reject = any(b.button_type == ButtonType.REJECT for b in banner_info.buttons)
                has_manage = any(b.button_type == ButtonType.MANAGE for b in banner_info.buttons)
                
                if has_reject and has_manage:
                    analysis["compliance"]["compliance_level"] = "high"
                    analysis["compliance"]["gdpr_compliant"] = True
                elif has_reject:
                    analysis["compliance"]["compliance_level"] = "medium"
                else:
                    analysis["compliance"]["compliance_level"] = "low"
                
                # Basic UX assessment
                if len(banner_info.buttons) >= 2:
                    analysis["user_experience"]["usability"] = "medium"
                
                # Calculate overall score
                score = 0
                if banner_info.detection_confidence > 0.8:
                    score += 30
                if analysis["compliance"]["compliance_level"] == "high":
                    score += 25
                elif analysis["compliance"]["compliance_level"] == "medium":
                    score += 15
                if analysis["user_experience"]["usability"] != "low":
                    score += 20
                if banner_info.overlay_selectors:
                    score += 10
                
                analysis["overall_score"] = score
            
        except Exception as e:
            print(f"Error in fallback analysis: {e}")
        
        return analysis
    
    def compare_banners(self, banner1_info: BannerInfo, banner2_info: BannerInfo) -> Dict[str, Any]:
        """
        Compare two consent banners using LLM analysis.
        
        Args:
            banner1_info: First banner info
            banner2_info: Second banner info
            
        Returns:
            Comparison results
        """
        if not self.client:
            return self._fallback_comparison(banner1_info, banner2_info)
        
        try:
            prompt = f"""
Compare these two cookie consent banners and provide a detailed comparison:

Banner 1:
- Type: {banner1_info.banner_type.value}
- Confidence: {banner1_info.detection_confidence}
- Buttons: {[b.button_type.value for b in banner1_info.buttons]}
- Selector: {banner1_info.container_selector}

Banner 2:
- Type: {banner2_info.banner_type.value}
- Confidence: {banner2_info.detection_confidence}
- Buttons: {[b.button_type.value for b in banner2_info.buttons]}
- Selector: {banner2_info.container_selector}

Provide comparison in JSON format:
{{
    "similarities": ["similarity1", "similarity2"],
    "differences": ["difference1", "difference2"],
    "better_banner": "banner1|banner2|tie",
    "reasons": ["reason1", "reason2"],
    "recommendations": ["recommendation1", "recommendation2"]
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
            print(f"Error comparing banners: {e}")
        
        return self._fallback_comparison(banner1_info, banner2_info)
    
    def _fallback_comparison(self, banner1_info: BannerInfo, banner2_info: BannerInfo) -> Dict[str, Any]:
        """Fallback comparison when LLM is not available."""
        comparison = {
            "similarities": [],
            "differences": [],
            "better_banner": "tie",
            "reasons": [],
            "recommendations": []
        }
        
        # Basic comparison logic
        if banner1_info.banner_type == banner2_info.banner_type:
            comparison["similarities"].append("Same banner type")
        
        if banner1_info.detection_confidence != banner2_info.detection_confidence:
            comparison["differences"].append("Different confidence scores")
        
        button1_types = {b.button_type for b in banner1_info.buttons}
        button2_types = {b.button_type for b in banner2_info.buttons}
        
        if button1_types == button2_types:
            comparison["similarities"].append("Same button types")
        else:
            comparison["differences"].append("Different button types")
        
        # Determine better banner
        if banner1_info.detection_confidence > banner2_info.detection_confidence:
            comparison["better_banner"] = "banner1"
            comparison["reasons"].append("Higher confidence score")
        elif banner2_info.detection_confidence > banner1_info.detection_confidence:
            comparison["better_banner"] = "banner2"
            comparison["reasons"].append("Higher confidence score")
        
        return comparison
    
    def generate_improvement_suggestions(self, banner_info: BannerInfo) -> List[str]:
        """
        Generate suggestions for improving banner detection and handling.
        
        Args:
            banner_info: BannerInfo object
            
        Returns:
            List of improvement suggestions
        """
        if not self.client:
            return self._fallback_suggestions(banner_info)
        
        try:
            prompt = f"""
Based on this cookie consent banner information, provide specific suggestions for improving banner detection and handling:

Banner Type: {banner_info.banner_type.value}
Confidence Score: {banner_info.detection_confidence}
Container Selector: {banner_info.container_selector}
Buttons Found: {[b.button_type.value for b in banner_info.buttons]}
Button Selectors: {[b.selector for b in banner_info.buttons]}

Provide practical suggestions for:
1. Improving selector reliability
2. Enhancing detection accuracy
3. Better user interaction handling
4. Performance optimization
5. Edge case handling

Respond as a JSON array of suggestions:
[
    "suggestion1",
    "suggestion2",
    "suggestion3"
]
"""
            
            response = self._call_llm(prompt)
            
            # Try to parse JSON response
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            
        except Exception as e:
            print(f"Error generating suggestions: {e}")
        
        return self._fallback_suggestions(banner_info)
    
    def _fallback_suggestions(self, banner_info: BannerInfo) -> List[str]:
        """Fallback suggestions when LLM is not available."""
        suggestions = []
        
        # Basic suggestions based on banner info
        if banner_info.detection_confidence < 0.8:
            suggestions.append("Improve banner detection patterns for higher confidence")
        
        if not any(b.button_type == ButtonType.REJECT for b in banner_info.buttons):
            suggestions.append("Add reject button detection patterns")
        
        if not any(b.button_type == ButtonType.MANAGE for b in banner_info.buttons):
            suggestions.append("Add manage button detection patterns")
        
        if not banner_info.overlay_selectors:
            suggestions.append("Consider adding overlay detection for modal banners")
        
        if banner_info.banner_type == BannerType.MODAL and not banner_info.overlay_selectors:
            suggestions.append("Add overlay hiding functionality for modal banners")
        
        if not suggestions:
            suggestions.append("Manual review and testing recommended")
        
        return suggestions
