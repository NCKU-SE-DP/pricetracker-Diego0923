from .base import LLMClientTemplate
import aisuite as ai

class OpenAIClient(LLMClientTemplate):
    def __init__(self, api_key: str, model: str):
        super().__init__(api_key, model)
    def _initialize_client(self):
        config = {"openai": {"api_key": self.api_key}}
        self.client = ai.Client(config)
    