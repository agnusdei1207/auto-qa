"""
Output Parser Module
"""
import json
import re


def parse_test_cases(llm_output: str) -> list:
    """Parse test cases from LLM output."""
    try:
        data = extract_json(llm_output)
        if data and 'test_cases' in data:
            return data['test_cases']
        return []
    except Exception as e:
        print(f"[Parser] Error parsing test cases: {e}")
        return []


def parse_action(llm_output: str) -> dict:
    """Parse action from LLM output."""
    try:
        data = extract_json(llm_output)
        if data:
            return data
        return {}
    except Exception as e:
        print(f"[Parser] Error parsing action: {e}")
        return {}


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
