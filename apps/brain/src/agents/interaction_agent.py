"""
Interaction Agent - UI Interactions
"""
import json
import logging
from .base_agent import BaseAgent
from apps.brain.src.config import EXECUTOR_API_URL
import requests


logger = logging.getLogger(__name__)


class InteractionAgent(BaseAgent):
    """Handles clicks, drags, hover events"""
    
    def get_system_prompt(self) -> str:
        return """You are Interaction Agent for web automation testing.

Your role is to handle UI interactions like clicks, drags, and hover.

ACTIONS:
- click: Click on an element
- hover: Mouse over an element
- drag: Drag element from source to target
- double_click: Double click on element
- scroll: Scroll page

OUTPUT FORMAT:
{
  "action": "click|hover|drag|double_click|scroll",
  "selector": "CSS selector",
  "target_selector": "target selector (for drag)",
  "scroll_direction": "up|down|left|right",
  "scroll_amount": "pixels to scroll"
}"""
    
    def get_description(self) -> str:
        return "Interaction Agent - Handles UI interactions"
    
    def execute(self, action: Dict[str, str]) -> str:
        """Execute interaction action via executor"""
        try:
            act = action.get("action")
            selector = action.get("selector")
            
            if act == "click" and selector:
                payload = {
                    "action": "click",
                    "selector": selector,
                    "session_id": self.session_id
                }
                res = requests.post(f"{EXECUTOR_API_URL}/click", json=payload, timeout=60)
                result = res.json()
                
                if result.get("success"):
                    logger.info(f"✓ Clicked {selector}")
                    return f"Clicked {selector} successfully"
                else:
                    return f"Click failed: {result.get('error')}"
            
            elif act == "hover" and selector:
                payload = {
                    "action": "hover",
                    "selector": selector,
                    "session_id": self.session_id
                }
                res = requests.post(f"{EXECUTOR_API_URL}/hover", json=payload, timeout=60)
                result = res.json()
                
                if result.get("success"):
                    logger.info(f"✓ Hovered over {selector}")
                    return f"Hovered {selector} successfully"
                else:
                    return f"Hover failed: {result.get('error')}"
            
            elif act == "drag":
                source = selector
                target = action.get("target_selector")
                if source and target:
                    payload = {
                        "action": "drag",
                        "source": source,
                        "target": target,
                        "session_id": self.session_id
                    }
                    res = requests.post(f"{EXECUTOR_API_URL}/drag", json=payload, timeout=60)
                    result = res.json()
                    
                    if result.get("success"):
                        logger.info(f"✓ Dragged {source} to {target}")
                        return f"Dragged {source} to {target} successfully"
                    else:
                        return f"Drag failed: {result.get('error')}"
            
            elif act == "double_click" and selector:
                payload = {
                    "action": "double_click",
                    "selector": selector,
                    "session_id": self.session_id
                }
                res = requests.post(f"{EXECUTOR_API_URL}/double_click", json=payload, timeout=60)
                result = res.json()
                
                if result.get("success"):
                    logger.info(f"✓ Double clicked {selector}")
                    return f"Double clicked {selector} successfully"
                else:
                    return f"Double click failed: {result.get('error')}"
            
            elif act == "scroll":
                direction = action.get("scroll_direction", "down")
                amount = action.get("scroll_amount", 500)
                payload = {
                    "action": "scroll",
                    "direction": direction,
                    "amount": amount,
                    "session_id": self.session_id
                }
                res = requests.post(f"{EXECUTOR_API_URL}/scroll", json=payload, timeout=60)
                result = res.json()
                
                if result.get("success"):
                    logger.info(f"✓ Scrolled {direction} by {amount}px")
                    return f"Scrolled {direction} by {amount}px successfully"
                else:
                    return f"Scroll failed: {result.get('error')}"
            
            return "Unknown action"
        
        except Exception as e:
            logger.error(f"Interaction agent error: {e}")
            return f"Error: {str(e)}"
