from unittest.mock import patch, MagicMock
from smart_log_analyzer.io.ai_insight import get_error_explanation
from smart_log_analyzer.core.models import ErrorGroup


@patch("google.generativeai.GenerativeModel")  # 1. Mock the class
@patch("google.generativeai.configure")  # 2. Mock the config
@patch("os.getenv")  # 3. Mock env vars
def test_get_error_explanation_success(
    mock_getenv: MagicMock, mock_configure: MagicMock, mock_model_class: MagicMock, sample_error_group: ErrorGroup
) -> None:
    """
    Tests successful AI explanation retrieval.
    """
    mock_getenv.return_value = "FAKE_API_KEY"

    mock_model_instance = MagicMock()
    mock_model_class.return_value = mock_model_instance

    mock_response = MagicMock()
    mock_response.text = "Try restarting the database."
    mock_model_instance.generate_content.return_value = mock_response

    result = get_error_explanation(sample_error_group)

    assert result == "Try restarting the database."
    mock_configure.assert_called_with(api_key="FAKE_API_KEY")
    mock_model_instance.generate_content.assert_called_once()


def test_ai_disabled_without_key(sample_error_group: ErrorGroup) -> None:
    """
    If no API key is set, it should return a warning immediately.
    """
    with patch("os.getenv", return_value=None):
        result = get_error_explanation(sample_error_group)
        assert "disabled" in result
