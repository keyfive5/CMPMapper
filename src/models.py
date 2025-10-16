"""
Data models for CMP detection and rule generation.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class BannerType(str, Enum):
    """Types of consent banners."""
    MODAL = "modal"
    BOTTOM_BAR = "bottom_bar"
    TOP_BAR = "top_bar"
    SIDEBAR = "sidebar"
    OVERLAY = "overlay"


class ButtonType(str, Enum):
    """Types of consent buttons."""
    ACCEPT = "accept"
    REJECT = "reject"
    MANAGE = "manage"
    CLOSE = "close"
    MORE_INFO = "more_info"


class ConsentButton(BaseModel):
    """Represents a consent button."""
    text: str
    button_type: ButtonType
    selector: str
    is_visible: bool = True
    attributes: Dict[str, Any] = Field(default_factory=dict)


class BannerInfo(BaseModel):
    """Information about a detected consent banner."""
    site: str
    banner_type: BannerType
    container_selector: str
    buttons: List[ConsentButton]
    overlay_selectors: List[str] = Field(default_factory=list)
    html_content: str
    detection_confidence: float = Field(ge=0.0, le=1.0)
    additional_selectors: Dict[str, str] = Field(default_factory=dict)


class ConsentRule(BaseModel):
    """Consent O Matic compatible rule template."""
    site: str
    selectors: Dict[str, str]
    actions: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    version: str = "1.0"


class PageData(BaseModel):
    """Complete page data for analysis."""
    url: str
    html_content: str
    javascript_content: List[str] = Field(default_factory=list)
    css_content: List[str] = Field(default_factory=list)
    screenshot_path: Optional[str] = None
    collected_at: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TestResult(BaseModel):
    """Result of rule testing."""
    rule: ConsentRule
    success: bool
    error_message: Optional[str] = None
    test_duration: float
    screenshots: List[str] = Field(default_factory=list)
    logs: List[str] = Field(default_factory=list)
