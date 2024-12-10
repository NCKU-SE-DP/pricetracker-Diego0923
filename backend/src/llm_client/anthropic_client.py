from .base import LLMClientTemplate
import aisuite as ai
class AnthropicClient(LLMClientTemplate):
    def __init__(self, api_key: str):
        super().__init__(api_key)
    def _initialize_client(self):
        config = {"anthropic": {"api_key": self.api_key}}
        self.client = ai.Client(config)