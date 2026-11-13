from pydantic import BaseModel

from app.providers.base import LLMProvider


class FakeProvider(LLMProvider):
    """Returns a fixed response (or raises an error) instead of calling a real AI."""

    def __init__(self, response: str = "{}", error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.prompts: list[str] = []

    def generate_json(self, prompt: str, schema: type[BaseModel]) -> str:
        self.prompts.append(prompt)
        if self.error:
            raise self.error
        return self.response