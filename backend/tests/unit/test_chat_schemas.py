import pytest
from pydantic import ValidationError

from backend.app.schemas.chat import ChatMessage
from backend.app.schemas.chat import ChatRequest


def test_chat_message_accepts_valid_payload():
    message = ChatMessage(role="user", content="I feel anxious about tomorrow.")
    assert message.role == "user"
    assert message.content == "I feel anxious about tomorrow."


def test_chat_message_rejects_invalid_role():
    with pytest.raises(ValidationError, match="Input should be 'system', 'user' or 'assistant'"):
        ChatMessage(role="moderator", content="Hello")


def test_chat_message_rejects_blank_content():
    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        ChatMessage(role="user", content="   ")


def test_chat_request_accepts_valid_payload():
    payload = ChatRequest(
        messages=[
            {"role": "user", "content": "I feel anxious about tomorrow."}
        ]
    )
    assert payload.messages[-1].role == "user"


def test_chat_request_rejects_empty_messages():
    with pytest.raises(ValidationError, match="messages must not be empty"):
        ChatRequest(messages=[])


def test_chat_request_rejects_non_user_last_message():
    with pytest.raises(ValidationError, match="last message must be from the user"):
        ChatRequest(
            messages=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi"},
            ]
        )
