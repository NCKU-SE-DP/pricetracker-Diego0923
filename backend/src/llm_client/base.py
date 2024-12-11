import abc
from pydantic import BaseModel, Field
from typing import List, Dict
import aisuite as ai
from src.config import newsImpactAndCause, DesiredKeywords, PriceChangeRelevance
class LLMClientBase(metaclass=abc.ABCMeta):    
    @staticmethod
    @abc.abstractmethod
    def _generate_text(messages: List[Dict[str, str]]) -> str:
        """
        Sends a list of messages to the LLM and retrieves the generated text.
        :param messages: A list of messages to send to the LLM.
        :return: The text response from the LLM.
        """
        pass
class LLMClientTemplate(abc.ABC):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.client = None
        self.model = model
        self._initialize_client()

    @abc.abstractmethod
    def _initialize_client(self):
        pass

    def generate_summary(self, content):
        keyword_messages = [
        {
            "role": "system",
            "content": newsImpactAndCause,
        },
        {"role": "user", "content": f"{content}"},
        ]
        return self._generate_text(messages=keyword_messages)
    def extract_search_keywords(self, content):
        keyword_messages = [
        {
            "role": "system",
            "content": DesiredKeywords,
        },
        {"role": "user", "content": f"{content}"},
        ]
        return self._generate_text(messages=keyword_messages)
    def evaluate_relevance(self, content):
        keyword_messages = [
        {
            "role": "system",
            "content": PriceChangeRelevance,
        },
        {"role": "user", "content": f"{content}"},
        ]
        return self._generate_text(messages=keyword_messages)
    def _generate_text(self, messages: List[Dict[str, str]]) -> str:       
        try:
            response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise e