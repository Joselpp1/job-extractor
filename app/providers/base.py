from abc import ABC, abstractmethod

from pydantic import BaseModel


class LLMProviderError(Exception):
    """Raised when the AI provider fails or returns an unusable response."""


class LLMProvider(ABC):
    """Common interface for any AI provider (Gemini, DeepSeek, a fake one for tests...)."""

    @abstractmethod
    def generate_json(self, prompt: str, schema: type[BaseModel]) -> str:
        """Send the prompt and return the raw JSON text that should match `schema`."""