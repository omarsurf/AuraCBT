from threading import Lock

from backend.app.schemas.chat import ChatMessage
from backend.app.schemas.chat import ChatResponse
from backend.app.services.decision_engine import choose_strategy
from backend.app.services.prompt_builder import build_system_prompt
from backend.app.services.response_safety import clean_response


class ChatPipelineService:
    """
    Request flow
    user messages -> trim history -> classify latest user turn -> choose strategy
    -> build prompt -> acquire inference lock -> generate -> clean response
    """

    def __init__(self, emotion_service, inference_service, max_history_messages: int):
        if max_history_messages <= 0:
            raise ValueError("max_history_messages must be positive")

        self.emotion_service = emotion_service
        self.inference_service = inference_service
        self.max_history_messages = max_history_messages
        self.inference_lock = Lock()

    def _trim_history(self, messages: list[ChatMessage]) -> list[ChatMessage]:
        return messages[-self.max_history_messages :]

    def _latest_user_message(self, messages: list[ChatMessage]) -> str:
        for message in reversed(messages):
            if message.role == "user":
                return message.content
        raise ValueError("trimmed history must include at least one user message")

    def chat(self, messages: list[ChatMessage]) -> ChatResponse:
        if not messages:
            raise ValueError("messages must not be empty")

        trimmed = self._trim_history(messages)
        latest_user_message = self._latest_user_message(trimmed)
        payload_messages = [message.model_dump() for message in trimmed]

        with self.inference_lock:
            emotion_info = self.emotion_service.classify(latest_user_message)
            strategy = choose_strategy(emotion_info["emotion"])
            system_prompt = build_system_prompt(strategy)
            raw_response = self.inference_service.generate(payload_messages, system_prompt)

        response = clean_response(raw_response, emotion_info["emotion"])
        return ChatResponse(
            raw_emotion=emotion_info["raw_emotion"],
            emotion=emotion_info["emotion"],
            strategy=strategy,
            response=response,
        )
