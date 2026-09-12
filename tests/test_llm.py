from unittest.mock import patch, MagicMock

from smartcommit.llm import generate_commit_message, _clean_message
from smartcommit.config import Config


def test_clean_message_strips_code_fence():
    raw = "```\nfeat(auth): add login\n```"
    assert _clean_message(raw) == "feat(auth): add login"


def test_clean_message_strips_quotes():
    raw = '"feat(auth): add login"'
    assert _clean_message(raw) == "feat(auth): add login"


def test_clean_message_takes_first_line_only():
    raw = "feat(auth): add login\nSome extra explanation the model added anyway"
    assert _clean_message(raw) == "feat(auth): add login"


@patch("smartcommit.llm.genai")
def test_generate_commit_message_success(mock_genai):
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value.text = "feat(cart): prevent negative quantity"
    mock_genai.Client.return_value = mock_client

    config = Config(gemini_api_key="fake-key")
    result = generate_commit_message("+ some diff", config)

    assert result == "feat(cart): prevent negative quantity"
    mock_genai.Client.assert_called_once_with(api_key="fake-key")


@patch("smartcommit.llm.genai")
def test_generate_commit_message_empty_response_raises(mock_genai):
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value.text = ""
    mock_genai.Client.return_value = mock_client

    config = Config(gemini_api_key="fake-key")
    try:
        generate_commit_message("+ diff", config)
        assert False, "expected RuntimeError"
    except RuntimeError as e:
        assert "empty" in str(e).lower()
