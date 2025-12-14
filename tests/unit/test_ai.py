from unittest.mock import patch, MagicMock
from smart_log_analyzer.io.ai_insight import get_error_explanation
from smart_log_analyzer.core.models import ErrorGroup


@patch("google.genai.Client")
@patch("os.getenv")
def test_get_error_explanation_success(
    mock_getenv: MagicMock,
    mock_client_class: MagicMock,
    sample_error_group: ErrorGroup,
) -> None:
    mock_getenv.return_value = "FAKE_API_KEY"

    mock_client_instance = MagicMock()
    mock_client_class.return_value = mock_client_instance

    mock_response = MagicMock()
    mock_response.text = "Try restarting the database."

    mock_client_instance.models.generate_content.return_value = mock_response

    result = get_error_explanation(sample_error_group)

    assert result == "Try restarting the database."
    mock_client_class.assert_called_with(api_key="FAKE_API_KEY")
    mock_client_instance.models.generate_content.assert_called_once()


def test_ai_disabled_without_key(sample_error_group: ErrorGroup) -> None:
    with patch("os.getenv", return_value=None):
        result = get_error_explanation(sample_error_group)
        assert "disabled" in result
