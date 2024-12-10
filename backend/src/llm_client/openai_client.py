from .base import LLMClientTemplate
import openai
from src.config import OPENAI_API_KEY
from typing import List, Dict
import aisuite as ai

class OpenAIClient(LLMClientTemplate):
    def __init__(self, api_key: str):
        super().__init__(api_key)
    def _initialize_client(self):
        config = {"openai": {"api_key": self.api_key}}
        self.client = ai.Client(config)
    