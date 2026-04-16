from typing import Annotated
from typing import Literal

from pydantic import BaseModel
from pydantic import StringConstraints
from pydantic import model_validator


ChatRole = Literal["system", "user", "assistant"]
ChatContent = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ChatMessage(BaseModel):
    role: ChatRole
    content: ChatContent


class ChatRequest(BaseModel):
    messages: list[ChatMessage]

    @model_validator(mode="after")
    def validate_messages(self) -> "ChatRequest":
        if not self.messages:
            raise ValueError("messages must not be empty")
        if self.messages[-1].role != "user":
            raise ValueError("last message must be from the user")
        return self


class ChatResponse(BaseModel):
    raw_emotion: str
    emotion: str
    strategy: str
    response: str
