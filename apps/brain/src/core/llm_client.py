"""
LLM Client - Ollama API communication
"""
import requests
import json
from ..config import OLLAMA_API_URL, LLM_MODEL


class LLMClient:
    """Ollama LLM client for QA testing"""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id
    
    def generate(self, prompt: str, agent_name: str = "unknown") -> str:
        """
        Generate LLM response.
        
        Args:
            prompt: The prompt to send to LLM
            agent_name: Name of agent making request
            
        Returns:
            LLM response string
        """
        try:
            payload = {
                "model": LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": 400}
            }
            
            print(f"[LLM] Sending request to {agent_name}...")
            res = requests.post(f"{OLLAMA_API_URL}/api/generate", json=payload, timeout=300)
            response = res.json().get('response', '')
            
            print(f"[LLM] Response received from {agent_name}: {len(response)} chars")
            return response
            
        except requests.exceptions.Timeout:
            print(f"[LLM] Timeout - model may be loading")
            return None
        except Exception as e:
            print(f"[LLM] Error: {e}")
            return None
    
    @staticmethod
    def extract_json(text: str) -> dict:
        """Extract JSON object from text."""
        try:
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
                
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                return json.loads(text[start:end+1])
            return None
        except:
            return None
