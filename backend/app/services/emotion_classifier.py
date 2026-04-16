import importlib
from typing import Protocol

from backend.app.services.decision_engine import normalize_emotion


class ClassifierProtocol(Protocol):
    def __call__(self, text: str) -> object: ...


class EmotionClassifierService:
    def __init__(self, classifier: ClassifierProtocol):
        self.classifier = classifier

    @classmethod
    def from_model_name_or_path(cls, model_name_or_path: str) -> "EmotionClassifierService":
        try:
            transformers = importlib.import_module("transformers")
            pipeline = transformers.pipeline
            classifier = pipeline("text-classification", model=model_name_or_path, top_k=1)
        except Exception as exc:
            raise RuntimeError(
                "Emotion classifier dependencies could not be loaded. "
                "This backend environment has incompatible ML packages. "
                "Reinstall compatible versions of transformers, numpy, scipy, "
                "and scikit-learn before using emotion classification."
            ) from exc

        return cls(classifier)

    def classify(self, text: str) -> dict[str, str]:
        result = self.classifier(text)
        raw_emotion = self._extract_label(result)
        return {
            "raw_emotion": raw_emotion,
            "emotion": normalize_emotion(raw_emotion),
        }

    @staticmethod
    def _extract_label(result: object) -> str:
        try:
            batch = result[0]
            top_result = batch[0]
            label = top_result["label"]
        except (IndexError, KeyError, TypeError) as exc:
            raise ValueError(
                "Emotion classifier returned an unexpected output shape."
            ) from exc

        if not isinstance(label, str) or not label.strip():
            raise ValueError("Emotion classifier returned an unexpected output shape.")

        return label
