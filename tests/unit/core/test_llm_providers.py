import httpx
from unittest.mock import MagicMock, patch

from smart_log_analyzer.core.llm_providers import (
    LLMProvider,
    get_provider,
    GeminiProvider,
    OllamaProvider,
)
from smart_log_analyzer.core.models import ErrorGroup


def test_get_provider_none() -> None:
    # Arrange
    provider = get_provider(LLMProvider.NONE)

    # Assert
    assert provider is None


def test_get_provider_gemini() -> None:
    # Arrange
    provider = get_provider(LLMProvider.GEMINI)

    # Assert
    assert isinstance(provider, GeminiProvider)


def test_get_provider_ollama_models() -> None:
    # Arrange
    provider = get_provider(LLMProvider.QWEN)

    # Assert
    assert isinstance(provider, OllamaProvider)


def test_gemini_provider_no_api_key() -> None:
    # Arrange
    provider = GeminiProvider()
    error = ErrorGroup(service="db", message="timeout", count=1)

    with patch("os.getenv", return_value=None):
        # Act
        result = provider.get_insight(error)

    # Assert
    assert "GEMINI_API_KEY" in result


def test_gemini_provider_success() -> None:
    # Arrange
    provider = GeminiProvider()
    error = ErrorGroup(service="db", message="timeout", count=1)

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "ok"
    mock_client.models.generate_content.return_value = mock_response

    with (
        patch("os.getenv", return_value="KEY"),
        patch("google.genai.Client", return_value=mock_client),
    ):
        # Act
        result = provider.get_insight(error)

    # Assert
    assert result == "ok"


def test_ollama_provider_connection_error() -> None:
    # Arrange
    provider = OllamaProvider("llama")
    error = ErrorGroup(service="db", message="timeout", count=1)

    with patch("httpx.Client.post", side_effect=httpx.ConnectError("fail")):
        # ACt
        result = provider.get_insight(error)

    # Assert
    assert "Cannot connect" in result
