"""
Form Agent - Form Handling
"""
import json
import logging
from .base_agent import BaseAgent
from apps.brain.src.config import EXECUTOR_API_URL
import requests


logger = logging.getLogger(__name__)


class FormAgent(BaseAgent):
    """Fills and submits forms, validates inputs"""
    
    def get_system_prompt(self) -> str:
        return """You are Form Agent for web automation testing.

Your role is to handle form filling and submission.

ACTIONS:
- fill: Fill a form field with value
- select: Select an option from dropdown
- submit: Submit a form
- validate: Check if form is filled correctly

OUTPUT FORMAT:
{
  "action": "fill|select|submit|validate",
  "selector": "CSS selector for element",
  "value": "value to fill/select",
  "expected": "expected result (for validation)"
}"""
    
    def get_description(self) -> str:
        return "Form Agent - Handles form operations"
    
    def execute(self, action: Dict[str, str]) -> str:
        """Execute form action via executor"""
        try:
            act = action.get("action")
            selector = action.get("selector")
            value = action.get("value")
            
            if act == "fill" and selector and value:
                payload = {
                    "action": "fill",
                    "selector": selector,
                    "value": value,
                    "session_id": self.session_id
                }
                res = requests.post(f"{EXECUTOR_API_URL}/fill", json=payload, timeout=60)
                result = res.json()
                
                if result.get("success"):
                    logger.info(f"✓ Filled {selector} with {value}")
                    return f"Filled {selector} successfully"
                else:
                    return f"Fill failed: {result.get('error')}"
            
            elif act == "select" and selector and value:
                payload = {
                    "action": "select",
                    "selector": selector,
                    "value": value,
                    "session_id": self.session_id
                }
                res = requests.post(f"{EXECUTOR_API_URL}/select", json=payload, timeout=60)
                result = res.json()
                
                if result.get("success"):
                    logger.info(f"✓ Selected {value} in {selector}")
                    return f"Selected {value} successfully"
                else:
                    return f"Select failed: {result.get('error')}"
            
            elif act == "submit":
                payload = {
                    "action": "submit",
                    "selector": action.get("selector", "form"),
                    "session_id": self.session_id
                }
                res = requests.post(f"{EXECUTOR_API_URL}/submit", json=payload, timeout=60)
                result = res.json()
                
                if result.get("success"):
                    logger.info(f"✓ Form submitted")
                    return f"Form submitted successfully"
                else:
                    return f"Submit failed: {result.get('error')}"
            
            elif act == "validate":
                payload = {
                    "action": "validate",
                    "selector": selector,
                    "expected": action.get("expected"),
                    "session_id": self.session_id
                }
                res = requests.post(f"{EXECUTOR_API_URL}/validate", json=payload, timeout=60)
                result = res.json()
                
                return f"Validation result: {result.get('valid')}"
            
            return "Unknown action"
        
        except Exception as e:
            logger.error(f"Form agent error: {e}")
            return f"Error: {str(e)}"
