"""
Brain Configuration
"""
import os

OLLAMA_API_URL = os.environ.get('OLLAMA_API_URL', 'http://ollama:11434')
EXECUTOR_API_URL = os.environ.get('EXECUTOR_API_URL', 'http://executor:9001')
LLM_MODEL = os.environ.get('LLM_MODEL', 'gemma3:1b')
