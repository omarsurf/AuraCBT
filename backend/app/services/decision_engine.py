from backend.app.services.strategy_catalog import EMOTION_TO_NORMALIZED
from backend.app.services.strategy_catalog import EMOTION_TO_STRATEGY
from backend.app.services.strategy_catalog import NORMAL_SUPPORT


def normalize_emotion(label: str) -> str:
    normalized_label = label.strip().lower()
    return EMOTION_TO_NORMALIZED.get(normalized_label, "neutral")


def choose_strategy(emotion: str) -> str:
    return EMOTION_TO_STRATEGY.get(emotion, NORMAL_SUPPORT)
