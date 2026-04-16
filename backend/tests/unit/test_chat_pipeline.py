import threading
import time

import pytest

from backend.app.schemas.chat import ChatMessage
from backend.app.services.chat_pipeline import ChatPipelineService


class LocalModelProbe:
    def __init__(self):
        self._lock = threading.Lock()
        self.active = 0
        self.max_active = 0

    def run(self):
        with self._lock:
            self.active += 1
            self.max_active = max(self.max_active, self.active)

        time.sleep(0.05)

        with self._lock:
            self.active -= 1


class RecordingEmotionService:
    def __init__(self, probe: LocalModelProbe | None = None):
        self.calls = []
        self.probe = probe

    def classify(self, text: str):
        self.calls.append(text)
        if self.probe is not None:
            self.probe.run()
        return {"raw_emotion": "fear", "emotion": "anxiety"}


class RecordingInferenceService:
    def __init__(self, probe: LocalModelProbe | None = None):
        self.calls = []
        self.probe = probe

    def generate(self, messages, system_prompt):
        self.calls.append((messages, system_prompt))
        if self.probe is not None:
            self.probe.run()
        return (
            "It sounds like you're worried right now. Taking it step by step can help. "
            "What feels most uncertain?"
        )


def test_pipeline_passes_trimmed_history_strategy_prompt_and_latest_user_text_downstream():
    emotion_service = RecordingEmotionService()
    inference_service = RecordingInferenceService()
    service = ChatPipelineService(
        emotion_service=emotion_service,
        inference_service=inference_service,
        max_history_messages=3,
    )
    messages = [
        ChatMessage(role="user", content="I am worried about tomorrow."),
        ChatMessage(role="assistant", content="What part feels most uncertain?"),
        ChatMessage(role="user", content="It might all go wrong."),
    ]

    result = service.chat(messages)

    assert emotion_service.calls == ["It might all go wrong."]
    assert len(inference_service.calls) == 1
    generated_messages, system_prompt = inference_service.calls[0]
    assert generated_messages == [message.model_dump() for message in messages]
    assert "STRATEGY: reassure_and_structure" in system_prompt
    assert result.raw_emotion == "fear"
    assert result.emotion == "anxiety"
    assert result.strategy == "reassure_and_structure"


def test_pipeline_uses_latest_user_message_within_trimmed_window_when_last_message_is_assistant():
    emotion_service = RecordingEmotionService()
    inference_service = RecordingInferenceService()
    service = ChatPipelineService(
        emotion_service=emotion_service,
        inference_service=inference_service,
        max_history_messages=3,
    )
    messages = [
        ChatMessage(role="user", content="Earlier context."),
        ChatMessage(role="assistant", content="Can you say more?"),
        ChatMessage(role="user", content="I keep thinking something bad will happen."),
        ChatMessage(role="assistant", content="Take your time."),
    ]

    service.chat(messages)

    trimmed = [message.model_dump() for message in messages[-3:]]
    generated_messages, _ = inference_service.calls[0]
    assert emotion_service.calls == ["I keep thinking something bad will happen."]
    assert generated_messages == trimmed


def test_pipeline_serializes_local_model_work_behind_one_lock():
    probe = LocalModelProbe()
    service = ChatPipelineService(
        emotion_service=RecordingEmotionService(probe=probe),
        inference_service=RecordingInferenceService(probe=probe),
        max_history_messages=1,
    )
    start = threading.Barrier(3)
    errors = []

    def worker(text: str):
        try:
            start.wait()
            service.chat([ChatMessage(role="user", content=text)])
        except Exception as exc:  # pragma: no cover - surfaced by assertion below
            errors.append(exc)

    threads = [
        threading.Thread(target=worker, args=(f"message {index}",))
        for index in range(2)
    ]
    for thread in threads:
        thread.start()

    start.wait()

    for thread in threads:
        thread.join()

    assert errors == []
    assert probe.max_active == 1


def test_pipeline_rejects_empty_messages():
    service = ChatPipelineService(
        emotion_service=RecordingEmotionService(),
        inference_service=RecordingInferenceService(),
        max_history_messages=1,
    )

    with pytest.raises(ValueError, match="messages must not be empty"):
        service.chat([])


def test_pipeline_rejects_non_positive_history_budget():
    with pytest.raises(ValueError, match="max_history_messages must be positive"):
        ChatPipelineService(
            emotion_service=RecordingEmotionService(),
            inference_service=RecordingInferenceService(),
            max_history_messages=0,
        )
