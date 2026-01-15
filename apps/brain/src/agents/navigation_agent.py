"""
Navigation Agent - Page Navigation
"""
import json
import logging
from .base_agent import BaseAgent
from apps.brain.src.config import EXECUTOR_API_URL
import requests


logger = logging.getLogger(__name__)


class NavigationAgent(BaseAgent):
    """Handles page navigation and URL routing"""
    
    def get_system_prompt(self) -> str:
        return """You are Navigation Agent for web automation testing.

Your role is to handle page navigation and URL routing.

ACTIONS:
- navigate: Go to a specific URL
- wait: Wait for page to load
- screenshot: Take a screenshot of current page

OUTPUT FORMAT:
{
  "action": "navigate|wait|screenshot",
  "url": "target URL (for navigate)",
  "wait_time": "seconds (for wait)"
}"""
    
    def get_description(self) -> str:
        return "Navigation Agent - Handles page navigation"
    
    def execute(self, action: Dict[str, str]) -> str:
        """Execute navigation action via executor"""
        try:
            url = action.get("url")
            act = action.get("action", "navigate")
            
            if act == "navigate" and url:
                payload = {
                    "action": "navigate",
                    "url": url,
                    "session_id": self.session_id
                }
                res = requests.post(f"{EXECUTOR_API_URL}/navigate", json=payload, timeout=60)
                result = res.json()
                
                if result.get("success"):
                    logger.info(f"✓ Navigated to {url}")
                    return f"Navigated to {url} successfully"
                else:
                    logger.error(f"✗ Navigation failed: {result.get('error')}")
                    return f"Navigation failed: {result.get('error')}"
            
            elif act == "wait":
                wait_time = action.get("wait_time", 2)
                import time
                time.sleep(wait_time)
                return f"Waited {wait_time} seconds"
            
            elif act == "screenshot":
                payload = {"session_id": self.session_id}
                res = requests.post(f"{EXECUTOR_API_URL}/screenshot", json=payload, timeout=30)
                result = res.json()
                return f"Screenshot saved: {result.get('screenshot_path')}"
            
            return "Unknown action"
        
        except Exception as e:
            logger.error(f"Navigation agent error: {e}")
            return f"Error: {str(e)}"
