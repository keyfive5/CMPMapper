"""
Error handling and troubleshooting utilities for CMP detection.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ErrorType(str, Enum):
    """Types of errors that can occur during CMP detection."""
    SCRAPING_ERROR = "scraping_error"
    BOT_DETECTION = "bot_detection"
    TIMEOUT_ERROR = "timeout_error"
    NETWORK_ERROR = "network_error"
    PARSING_ERROR = "parsing_error"
    DETECTION_ERROR = "detection_error"
    RULE_GENERATION_ERROR = "rule_generation_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class ErrorReport:
    """Detailed error report with troubleshooting information."""
    error_type: ErrorType
    error_message: str
    url: str
    timestamp: str
    context: Dict[str, Any]
    suggested_fixes: List[str]
    manual_steps: List[str]
    error_severity: str  # "low", "medium", "high", "critical"


class ErrorHandler:
    """Handles errors and provides troubleshooting guidance."""
    
    def __init__(self):
        """Initialize the error handler."""
        self.logger = logging.getLogger(__name__)
        self.error_patterns = self._initialize_error_patterns()
    
    def _initialize_error_patterns(self) -> Dict[str, Dict]:
        """Initialize error detection patterns."""
        return {
            'bot_detection': {
                'patterns': [
                    '403 forbidden', 'access denied', 'bot detected', 'automated request',
                    'cloudflare', 'recaptcha', 'captcha', 'blocked', 'rate limited',
                    'too many requests', 'suspicious activity', 'security check'
                ],
                'suggestions': [
                    'Try using a different user agent',
                    'Add delays between requests',
                    'Use residential proxy',
                    'Disable JavaScript automation flags',
                    'Try accessing the site manually first'
                ]
            },
            'timeout_error': {
                'patterns': [
                    'timeout', 'connection timeout', 'read timeout', 'request timeout',
                    'server timeout', 'gateway timeout', 'service unavailable'
                ],
                'suggestions': [
                    'Increase timeout settings',
                    'Check network connectivity',
                    'Try again later',
                    'Use a different server location'
                ]
            },
            'network_error': {
                'patterns': [
                    'connection refused', 'connection reset', 'network unreachable',
                    'dns resolution failed', 'ssl error', 'certificate error'
                ],
                'suggestions': [
                    'Check internet connection',
                    'Verify URL is correct',
                    'Try using HTTP instead of HTTPS',
                    'Check firewall settings'
                ]
            },
            'parsing_error': {
                'patterns': [
                    'parsing error', 'invalid html', 'malformed content',
                    'encoding error', 'decode error', 'syntax error'
                ],
                'suggestions': [
                    'Try different HTML parser',
                    'Check content encoding',
                    'Validate HTML structure',
                    'Use alternative extraction method'
                ]
            }
        }
    
    def handle_scraping_error(self, error: Exception, url: str, context: Dict[str, Any] = None) -> ErrorReport:
        """
        Handle scraping errors and provide detailed troubleshooting.
        
        Args:
            error: The exception that occurred
            url: URL being scraped
            context: Additional context about the error
            
        Returns:
            ErrorReport with troubleshooting information
        """
        error_message = str(error).lower()
        error_type = self._classify_error_type(error_message)
        
        # Extract error context
        error_context = {
            'url': url,
            'error_class': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        
        # Generate suggestions based on error type
        suggested_fixes = self._generate_suggestions(error_type, error_message)
        manual_steps = self._generate_manual_steps(error_type, url)
        
        # Determine error severity
        severity = self._determine_severity(error_type, error_message)
        
        return ErrorReport(
            error_type=error_type,
            error_message=str(error),
            url=url,
            timestamp=self._get_timestamp(),
            context=error_context,
            suggested_fixes=suggested_fixes,
            manual_steps=manual_steps,
            error_severity=severity
        )
    
    def _classify_error_type(self, error_message: str) -> ErrorType:
        """Classify error type based on error message."""
        error_message_lower = error_message.lower()
        
        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns['patterns']:
                if pattern in error_message_lower:
                    return ErrorType(error_type.upper())
        
        return ErrorType.UNKNOWN_ERROR
    
    def _generate_suggestions(self, error_type: ErrorType, error_message: str) -> List[str]:
        """Generate automated suggestions based on error type."""
        suggestions = []
        
        if error_type == ErrorType.BOT_DETECTION:
            suggestions.extend([
                "Update user agent to mimic a real browser",
                "Add random delays between requests",
                "Disable automation flags in browser",
                "Use residential proxy services",
                "Try accessing during off-peak hours"
            ])
        elif error_type == ErrorType.TIMEOUT_ERROR:
            suggestions.extend([
                "Increase timeout settings to 30+ seconds",
                "Check if the website is experiencing high traffic",
                "Try accessing the site manually to verify availability",
                "Use a different server location or VPN"
            ])
        elif error_type == ErrorType.NETWORK_ERROR:
            suggestions.extend([
                "Verify the URL is correct and accessible",
                "Check internet connection and DNS settings",
                "Try using a different network or VPN",
                "Verify SSL certificate is valid"
            ])
        elif error_type == ErrorType.PARSING_ERROR:
            suggestions.extend([
                "Try different HTML parsing libraries",
                "Check for encoding issues in the content",
                "Validate HTML structure before parsing",
                "Use alternative content extraction methods"
            ])
        else:
            suggestions.extend([
                "Check the website manually for any issues",
                "Try again in a few minutes",
                "Contact support if the issue persists",
                "Review error logs for more details"
            ])
        
        return suggestions
    
    def _generate_manual_steps(self, error_type: ErrorType, url: str) -> List[str]:
        """Generate manual troubleshooting steps."""
        steps = []
        
        if error_type == ErrorType.BOT_DETECTION:
            steps.extend([
                f"1. Open {url} in a regular browser",
                "2. Check if the site loads normally",
                "3. Look for any bot detection messages",
                "4. Try accessing from a different device/network",
                "5. Check if the site requires manual verification"
            ])
        elif error_type == ErrorType.TIMEOUT_ERROR:
            steps.extend([
                f"1. Test {url} in a browser to check loading speed",
                "2. Try accessing from different locations",
                "3. Check if the site is experiencing issues",
                "4. Verify the URL is correct and accessible"
            ])
        elif error_type == ErrorType.NETWORK_ERROR:
            steps.extend([
                f"1. Verify {url} is accessible from your network",
                "2. Check if the site is down",
                "3. Try accessing from a different network",
                "4. Verify DNS resolution is working"
            ])
        else:
            steps.extend([
                f"1. Manually visit {url} to check for issues",
                "2. Look for any error messages on the page",
                "3. Check if the site requires special access",
                "4. Verify the site is not under maintenance"
            ])
        
        return steps
    
    def _determine_severity(self, error_type: ErrorType, error_message: str) -> str:
        """Determine error severity level."""
        if error_type == ErrorType.BOT_DETECTION:
            return "high"
        elif error_type == ErrorType.TIMEOUT_ERROR:
            return "medium"
        elif error_type == ErrorType.NETWORK_ERROR:
            return "high"
        elif error_type == ErrorType.PARSING_ERROR:
            return "low"
        else:
            return "medium"
    
    def suggest_manual_steps(self, error_type: ErrorType) -> List[str]:
        """Provide user-friendly manual intervention steps."""
        manual_steps = {
            ErrorType.BOT_DETECTION: [
                "The website has detected automated access. Try these steps:",
                "• Access the site manually in a regular browser first",
                "• Look for any consent banners or cookie notices",
                "• Note the exact selectors and button text",
                "• Use the manual rule creation feature if available"
            ],
            ErrorType.TIMEOUT_ERROR: [
                "The website is taking too long to respond. Try these steps:",
                "• Check if the site is accessible manually",
                "• Try again during off-peak hours",
                "• Use a different network or VPN if available",
                "• Consider the site may be experiencing issues"
            ],
            ErrorType.NETWORK_ERROR: [
                "Network connectivity issues detected. Try these steps:",
                "• Verify the URL is correct and accessible",
                "• Check your internet connection",
                "• Try accessing from a different network",
                "• Contact your network administrator if issues persist"
            ],
            ErrorType.PARSING_ERROR: [
                "Content parsing issues detected. Try these steps:",
                "• The website may have unusual HTML structure",
                "• Try using the manual rule creation feature",
                "• Check if the site requires JavaScript to load content",
                "• Consider using a different analysis method"
            ]
        }
        
        return manual_steps.get(error_type, [
            "An unexpected error occurred. Try these steps:",
            "• Check if the website is accessible manually",
            "• Try again in a few minutes",
            "• Contact support if the issue persists"
        ])
    
    def create_troubleshooting_report(self, errors: List[ErrorReport]) -> Dict[str, Any]:
        """Create a comprehensive troubleshooting report."""
        if not errors:
            return {"status": "no_errors", "message": "No errors to report"}
        
        # Group errors by type
        error_groups = {}
        for error in errors:
            error_type = error.error_type.value
            if error_type not in error_groups:
                error_groups[error_type] = []
            error_groups[error_type].append(error)
        
        # Calculate statistics
        total_errors = len(errors)
        critical_errors = len([e for e in errors if e.error_severity == "critical"])
        high_errors = len([e for e in errors if e.error_severity == "high"])
        
        # Generate recommendations
        recommendations = self._generate_recommendations(error_groups)
        
        return {
            "status": "errors_detected",
            "total_errors": total_errors,
            "critical_errors": critical_errors,
            "high_errors": high_errors,
            "error_breakdown": error_groups,
            "recommendations": recommendations,
            "next_steps": self._generate_next_steps(error_groups)
        }
    
    def _generate_recommendations(self, error_groups: Dict[str, List[ErrorReport]]) -> List[str]:
        """Generate recommendations based on error patterns."""
        recommendations = []
        
        if 'bot_detection' in error_groups:
            recommendations.append(
                "Consider implementing more sophisticated bot detection avoidance techniques"
            )
        
        if 'timeout_error' in error_groups:
            recommendations.append(
                "Increase timeout settings and implement retry logic"
            )
        
        if 'network_error' in error_groups:
            recommendations.append(
                "Implement network error recovery and alternative connection methods"
            )
        
        if 'parsing_error' in error_groups:
            recommendations.append(
                "Add more robust HTML parsing and content validation"
            )
        
        return recommendations
    
    def _generate_next_steps(self, error_groups: Dict[str, List[ErrorReport]]) -> List[str]:
        """Generate next steps for error resolution."""
        next_steps = []
        
        if error_groups:
            next_steps.append("Review the error details and suggested fixes")
            next_steps.append("Try the manual troubleshooting steps")
            next_steps.append("Consider using alternative analysis methods")
            next_steps.append("Contact support if issues persist")
        
        return next_steps
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def log_error(self, error_report: ErrorReport) -> None:
        """Log error report to file."""
        log_message = f"""
        Error Report:
        Type: {error_report.error_type}
        URL: {error_report.url}
        Message: {error_report.error_message}
        Severity: {error_report.error_severity}
        Timestamp: {error_report.timestamp}
        Context: {error_report.context}
        Suggested Fixes: {error_report.suggested_fixes}
        Manual Steps: {error_report.manual_steps}
        """
        
        self.logger.error(log_message)
    
    def get_error_statistics(self, errors: List[ErrorReport]) -> Dict[str, Any]:
        """Get statistics about errors."""
        if not errors:
            return {"total": 0, "by_type": {}, "by_severity": {}}
        
        by_type = {}
        by_severity = {}
        
        for error in errors:
            # Count by type
            error_type = error.error_type.value
            by_type[error_type] = by_type.get(error_type, 0) + 1
            
            # Count by severity
            severity = error.error_severity
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            "total": len(errors),
            "by_type": by_type,
            "by_severity": by_severity,
            "most_common_type": max(by_type.items(), key=lambda x: x[1])[0] if by_type else None,
            "most_common_severity": max(by_severity.items(), key=lambda x: x[1])[0] if by_severity else None
        }
