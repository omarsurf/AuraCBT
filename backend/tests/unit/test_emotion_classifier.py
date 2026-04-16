import pytest

from backend.app.services import emotion_classifier
from backend.app.services.emotion_classifier import EmotionClassifierService


class FakeClassifier:
    def __call__(self, text: str):
        return [[{"label": "fear", "score": 0.9}]]


class MalformedClassifier:
    def __call__(self, text: str):
        return [{"score": 0.9}]


def test_emotion_classifier_returns_raw_and_normalized_labels():
    service = EmotionClassifierService(FakeClassifier())

    result = service.classify("I am scared about tomorrow.")

    assert result["raw_emotion"] == "fear"
    assert result["emotion"] == "anxiety"


def test_emotion_classifier_rejects_malformed_classifier_output():
    service = EmotionClassifierService(MalformedClassifier())

    with pytest.raises(ValueError, match="unexpected output shape"):
        service.classify("I am scared about tomorrow.")


def test_emotion_classifier_wraps_pipeline_import_failures(monkeypatch: pytest.MonkeyPatch):
    def fake_import_module(name: str):
        assert name == "transformers"
        raise ImportError("numpy.core.multiarray failed to import")

    monkeypatch.setattr(
        emotion_classifier,
        "importlib",
        type("ImportLibStub", (), {"import_module": staticmethod(fake_import_module)})(),
        raising=False,
    )

    with pytest.raises(RuntimeError, match="incompatible ML packages"):
        EmotionClassifierService.from_model_name_or_path("mock-model")


def test_emotion_classifier_wraps_pipeline_construction_failures(monkeypatch: pytest.MonkeyPatch):
    class FakeTransformersModule:
        @staticmethod
        def pipeline(*args, **kwargs):
            raise ValueError("model initialization failed")

    def fake_import_module(name: str):
        assert name == "transformers"
        return FakeTransformersModule()

    monkeypatch.setattr(
        emotion_classifier,
        "importlib",
        type("ImportLibStub", (), {"import_module": staticmethod(fake_import_module)})(),
        raising=False,
    )

    with pytest.raises(RuntimeError, match="incompatible ML packages"):
        EmotionClassifierService.from_model_name_or_path("mock-model")
