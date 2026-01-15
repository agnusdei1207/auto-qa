"""
Verification Agent - Result Validation
"""
import json
import logging
from .base_agent import BaseAgent
from apps.brain.src.config import EXECUTOR_API_URL
import requests


logger = logging.getLogger(__name__)


class VerificationAgent(BaseAgent):
    """Verifies expected results and states"""
    
    def get_system_prompt(self) -> str:
        return """You are Verification Agent for web automation testing.

Your role is to verify test results and check page states.

ACTIONS:
- verify_text: Check if text is present on page
- verify_element: Check if element exists and is visible
- verify_url: Check current URL
- verify_title: Check page title
- screenshot: Take screenshot for evidence

OUTPUT FORMAT:
{
  "action": "verify_text|verify_element|verify_url|verify_title|screenshot",
  "text": "text to verify (for verify_text)",
  "selector": "CSS selector (for verify_element)",
  "url": "expected URL (for verify_url)",
  "title": "expected title (for verify_title)",
  "expected": "what to expect"
}"""
    
    def get_description(self) -> str:
        return "Verification Agent - Validates test results"
    
    def execute(self, action: Dict[str, str]) -> str:
        """Execute verification action via executor"""
        try:
            act = action.get("action")
            
            if act == "verify_text":
                text = action.get("text")
                payload = {
                    "action": "verify_text",
                    "text": text,
                    "session_id": self.session_id
                }
                res = requests.post(f"{EXECUTOR_API_URL}/verify_text", json=payload, timeout=60)
                result = res.json()
                
                if result.get("found"):
                    logger.info(f"✓ Text found: {text}")
                    return f"Text '{text}' found on page"
                else:
                    logger.warning(f"✗ Text not found: {text}")
                    return f"Text '{text}' not found on page"
            
            elif act == "verify_element":
                selector = action.get("selector")
                payload = {
                    "action": "verify_element",
                    "selector": selector,
                    "session_id": self.session_id
                }
                res = requests.post(f"{EXECUTOR_API_URL}/verify_element", json=payload, timeout=60)
                result = res.json()
                
                if result.get("exists"):
                    logger.info(f"✓ Element exists: {selector}")
                    return f"Element '{selector}' exists and is visible"
                else:
                    logger.warning(f"✗ Element not found: {selector}")
                    return f"Element '{selector}' not found or not visible"
            
            elif act == "verify_url":
                url = action.get("url")
                payload = {
                    "action": "verify_url",
                    "expected_url": url,
                    "session_id": self.session_id
                }
                res = requests.post(f"{EXECUTOR_API_URL}/verify_url", json=payload, timeout=60)
                result = res.json()
                
                if result.get("match"):
                    logger.info(f"✓ URL matches: {url}")
                    return f"URL matches expected: {url}"
                else:
                    actual = result.get("actual_url", "unknown")
                    return f"URL mismatch. Expected: {url}, Actual: {actual}"
            
            elif act == "verify_title":
                title = action.get("title")
                payload = {
                    "action": "verify_title",
                    "expected_title": title,
                    "session_id": self.session_id
                }
                res = requests.post(f"{EXECUTOR_API_URL}/verify_title", json=payload, timeout=60)
                result = res.json()
                
                if result.get("match"):
                    logger.info(f"✓ Title matches: {title}")
                    return f"Title matches expected: {title}"
                else:
                    actual = result.get("actual_title", "unknown")
                    return f"Title mismatch. Expected: {title}, Actual: {actual}"
            
            elif act == "screenshot":
                payload = {"session_id": self.session_id}
                res = requests.post(f"{EXECUTOR_API_URL}/screenshot", json=payload, timeout=30)
                result = res.json()
                return f"Screenshot saved: {result.get('screenshot_path')}"
            
            return "Unknown action"
        
        except Exception as e:
            logger.error(f"Verification agent error: {e}")
            return f"Error: {str(e)}"
