import abc
from pydantic import BaseModel, Field
from typing import List, Dict
class LLMClientBase(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def ai_respond(self, content: str, words: str) -> str:
        """
        Abstract method to generate a response using AI.
        :param content: The input content to respond to.
        :param words: The guiding instructions for the AI.
        :return: The AI-generated response as a string.
        """
        pass
    @staticmethod
    @abc.abstractmethod
    def _generate_text(messages: List[Dict[str, str]]) -> str:
        """
        Sends a list of messages to the LLM and retrieves the generated text.
        :param messages: A list of messages to send to the LLM.
        :return: The text response from the LLM.
        """
        pass