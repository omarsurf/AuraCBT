import pytest

from backend.app.services.response_safety import clean_response


ANXIETY_FALLBACK = (
    "It sounds like you're feeling anxious about this situation. It's understandable "
    "to feel that way when things feel uncertain. Taking it one piece at a time can make "
    "it feel more manageable. What part feels most overwhelming right now?"
)

SADNESS_FALLBACK = (
    "It sounds like you're feeling sad and alone right now. That can be a very heavy "
    "feeling to carry, and it makes sense that it hurts. You do not need to solve the "
    "whole thing at once tonight. What has been weighing on you the most lately?"
)

NEUTRAL_FALLBACK = (
    "It sounds like something is weighing on your mind. Taking a moment to slow it down "
    "can help make it clearer. We can look at one piece at a time if that helps. "
    "What feels most important about it right now?"
)


def test_clean_response_replaces_forbidden_phrase():
    response = clean_response("As a therapist, I would say call this number.", "anxiety")
    assert response == ANXIETY_FALLBACK


def test_clean_response_replaces_forbidden_phrase_with_whitespace_variants():
    response = clean_response(
        "Please call\nthis number because I think it will solve everything and make the "
        "stress disappear quickly for you tonight.",
        "sadness",
    )
    assert response == SADNESS_FALLBACK


@pytest.mark.parametrize(
    "response",
    [
        "Please call-this number because I think it will solve everything and make the "
        "stress disappear quickly for you tonight.",
        "Please call this, number because I think it will solve everything and make the "
        "stress disappear quickly for you tonight.",
    ],
)
def test_clean_response_replaces_forbidden_phrase_with_punctuation_variants(response):
    assert clean_response(response, "sadness") == SADNESS_FALLBACK


def test_clean_response_does_not_match_harmless_substring_phrase():
    response = clean_response(
        "You may recall this number from earlier, but let us focus on what hurts most right now.",
        "neutral",
    )
    assert response == "You may recall this number from earlier, but let us focus on what hurts most right now?"


def test_clean_response_replaces_short_response():
    response = clean_response("Okay.", "sadness")
    assert response == SADNESS_FALLBACK


def test_clean_response_uses_fallback_for_blank_response():
    response = clean_response("   ", "neutral")
    assert response == NEUTRAL_FALLBACK


def test_clean_response_normalizes_spacing_and_question_punctuation():
    response = clean_response(
        "  This feels difficult to sort through right now, and I am not sure what to do next.   ",
        "neutral",
    )
    assert response == "This feels difficult to sort through right now, and I am not sure what to do next?"


def test_clean_response_preserves_question_exclamation_punctuation():
    response = clean_response(
        "This feels painful and confusing, and I do not know how to make sense of it right now?!",
        "neutral",
    )
    assert response == "This feels painful and confusing, and I do not know how to make sense of it right now?!"
