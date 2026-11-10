import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import BaseModel

from app.providers.base import LLMProvider, LLMProviderError

DEFAULT_MODEL = "gemini-3.5-flash-lite"


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    @classmethod
    def from_env(cls) -> "GeminiProvider":
        """Build the provider from the GEMINI_API_KEY and GEMINI_MODEL variables."""
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise LLMProviderError("GEMINI_API_KEY is not set. Add it to your .env file.")
        return cls(api_key=api_key, model=os.getenv("GEMINI_MODEL", DEFAULT_MODEL))

    def generate_json(self, prompt: str, schema: type[BaseModel]) -> str:
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
            )
        except errors.APIError as exc:
            raise LLMProviderError(f"Gemini API error: {exc}") from exc

        if not response.text:
            raise LLMProviderError("Gemini returned an empty response.")
        return response.text
    