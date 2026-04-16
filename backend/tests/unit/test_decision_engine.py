import pytest

from backend.app.services.decision_engine import choose_strategy
from backend.app.services.decision_engine import normalize_emotion


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("fear", "anxiety"),
        ("anxiety", "anxiety"),
        ("sadness", "sadness"),
        ("anger", "anger"),
        ("joy", "positive"),
        ("positive", "positive"),
        ("neutral", "neutral"),
    ],
)
def test_normalize_emotion_maps_known_labels(label: str, expected: str):
    assert normalize_emotion(label) == expected


def test_normalize_emotion_trims_whitespace_and_normalizes_case():
    assert normalize_emotion("  FEAR  ") == "anxiety"


def test_normalize_emotion_falls_back_to_neutral():
    assert normalize_emotion("unknown") == "neutral"


@pytest.mark.parametrize(
    ("emotion", "expected"),
    [
        ("sadness", "validate_and_support"),
        ("anxiety", "reassure_and_structure"),
        ("anger", "deescalate_and_reflect"),
        ("positive", "encourage_and_reinforce"),
        ("neutral", "normal_support"),
    ],
)
def test_choose_strategy_maps_all_known_emotions(emotion: str, expected: str):
    assert choose_strategy(emotion) == expected


def test_choose_strategy_falls_back_to_normal_support():
    assert choose_strategy("mystery") == "normal_support"
