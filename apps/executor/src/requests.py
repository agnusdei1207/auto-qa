"""
Request/Response Models for Executor API
"""
from pydantic import BaseModel


class NavigateRequest(BaseModel):
    """Navigate to URL request"""
    url: str
    session_id: str


class FillRequest(BaseModel):
    """Fill form field request"""
    selector: str
    value: str
    session_id: str


class SelectRequest(BaseModel):
    """Select dropdown option request"""
    selector: str
    value: str
    session_id: str


class ClickRequest(BaseModel):
    """Click element request"""
    selector: str
    session_id: str


class HoverRequest(BaseModel):
    """Hover over element request"""
    selector: str
    session_id: str


class DragRequest(BaseModel):
    """Drag element request"""
    source: str
    target: str
    session_id: str


class ScrollRequest(BaseModel):
    """Scroll page request"""
    direction: str
    amount: int
    session_id: str


class ScreenshotRequest(BaseModel):
    """Take screenshot request"""
    session_id: str
    full_page: bool = False


class SetHeadfulRequest(BaseModel):
    """Toggle headful mode request"""
    session_id: str
    headful: bool = True


class GetHTMLRequest(BaseModel):
    """Get HTML content request"""
    session_id: str


class ProgressUpdateRequest(BaseModel):
    """Update progress request"""
    session_id: str
    test_case_id: str
    step_number: int
    status: str
    message: str
