"""LLM Provider abstraction for multiple AI backends."""

import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

import httpx
from dotenv import load_dotenv
from google import genai
from google.genai import types

from .models import ErrorGroup

load_dotenv()


class LLMProvider(str, Enum):
    """Available LLM providers."""

    NONE = "none"
    GEMINI = "gemini"
    QWEN = "qwen2.5:7b-instruct"
    PHI = "phi3.5:mini"
    LLAMA = "llama3.2:3b"


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def get_insight(self, error: ErrorGroup) -> str: ...


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API provider."""

    @property
    def name(self) -> str:
        return "Google Gemini"

    def get_insight(self, error: ErrorGroup) -> str:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "⚠️ GEMINI_API_KEY not found in environment."

        try:
            client = genai.Client(api_key=api_key)
            prompt = self._build_prompt(error)

            response = client.models.generate_content(  # pyright: ignore[reportUnknownMemberType]
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are an expert software engineer specializing in log analysis.",
                    temperature=0.2,
                ),
            )
            return str(response.text)
        except Exception as e:
            return f"⚠️ Gemini error: {e}"

    def _build_prompt(self, error: ErrorGroup) -> str:
        return f"""Analyze this error occurring {error.count} times in '{error.service}':

Error: "{error.message}"

Explain what this error means and suggest 2 fixes. Keep it under 3 sentences."""


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider."""

    def __init__(self, model: str):
        self._model = model
        self._base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")

    @property
    def name(self) -> str:
        return f"Ollama ({self._model})"

    def get_insight(self, error: ErrorGroup) -> str:
        prompt = self._build_prompt(error)

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self._base_url}/api/generate",
                    json={
                        "model": self._model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.2},
                    },
                )
                response.raise_for_status()
                return response.json().get("response", "No response from model.")
        except httpx.ConnectError:
            return f"⚠️ Cannot connect to Ollama at {self._base_url}. Is Ollama running?"
        except Exception as e:
            return f"⚠️ Ollama error: {e}"

    def _build_prompt(self, error: ErrorGroup) -> str:
        return f"""You are an expert software engineer. Analyze this error occurring {error.count} times in service '{error.service}':

Error Message: "{error.message}"

Explain what this error typically means and suggest 2 common ways to fix it. Keep your response under 3 sentences."""


def get_provider(provider_type: LLMProvider) -> Optional[BaseLLMProvider]:
    """Factory function to get the appropriate LLM provider."""
    match provider_type:
        case LLMProvider.NONE:
            return None
        case LLMProvider.GEMINI:
            return GeminiProvider()
        case LLMProvider.QWEN | LLMProvider.PHI | LLMProvider.LLAMA:
            return OllamaProvider(provider_type.value)
        case _:
            return None
