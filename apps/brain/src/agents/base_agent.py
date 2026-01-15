"""
Base Agent Module
"""
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any


logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all QA agents"""
    
    def __init__(self, session_id: str, llm):
        self.session_id = session_id
        self.llm = llm
        self.history = []
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return system prompt for this agent"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return agent description"""
        pass
    
    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to reason about context and decide on action"""
        prompt = self._build_prompt(context)
        response = self.llm.generate(prompt, self.__class__.__name__)
        
        if response:
            try:
                text = response
                if '```json' in text:
                    text = text.split('```json')[1].split('```')[0]
                elif '```' in text:
                    text = text.split('```')[1].split('```')[0]
                
                start = text.find('{')
                end = text.rfind('}')
                if start != -1 and end != -1:
                    return json.loads(text[start:end+1])
            except:
                pass
            return {}
        return {}
    
    def execute(self, action: Dict[str, Any]) -> str:
        """Execute the decided action (to be implemented by subclasses)"""
        return f"Executed action: {action}"
    
    def learn(self, action: Dict[str, Any], result: str):
        """Learn from execution result"""
        self.history.append({
            "action": action,
            "result": result,
            "timestamp": __import__('time').time()
        })
    
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt from context"""
        return f"""{self.get_system_prompt()}

Context:
{json.dumps(context, indent=2, default=str)}

History:
{self._format_history()}"""
    
    def _format_history(self) -> str:
        """Format action history"""
        if not self.history:
            return "No previous actions"
        
        lines = []
        for i, entry in enumerate(self.history[-5:], 1):
            lines.append(f"{i}. {entry['action']} -> {entry['result'][:100]}")
        return "\n".join(lines)
