import re


FALLBACKS = {
    "anxiety": "It sounds like you're feeling anxious about this situation. It's understandable to feel that way when things feel uncertain. Taking it one piece at a time can make it feel more manageable. What part feels most overwhelming right now?",
    "sadness": "It sounds like you're feeling sad and alone right now. That can be a very heavy feeling to carry, and it makes sense that it hurts. You do not need to solve the whole thing at once tonight. What has been weighing on you the most lately?",
    "anger": "It sounds like you're feeling frustrated by what happened. That reaction makes sense when something feels unfair or hurtful. Slowing the moment down can help before reacting. What part of it hit you the hardest?",
    "positive": "It sounds like something meaningful went well for you. Noticing that matters, and it can help you build more moments like this. Holding onto what made it feel good can be useful. What do you think made this moment land so well?",
    "neutral": "It sounds like something is weighing on your mind. Taking a moment to slow it down can help make it clearer. We can look at one piece at a time if that helps. What feels most important about it right now?",
}

FORBIDDEN_PHRASES = [
    "reach out to us",
    "call this number",
    "as a therapist",
    "when i was",
    "in my experience",
]

_WORD_SEP = r"[\W_]+"

FORBIDDEN_PATTERNS = tuple(
    re.compile(
        rf"(?<!\w){_WORD_SEP.join(re.escape(part) for part in phrase.split())}(?!\w)"
    )
    for phrase in FORBIDDEN_PHRASES
)


def clean_response(response: str, emotion: str) -> str:
    fallback = FALLBACKS.get(emotion, FALLBACKS["neutral"])
    trimmed = " ".join(response.split())
    lowered = trimmed.lower()

    if not lowered:
        return fallback
    if any(pattern.search(lowered) for pattern in FORBIDDEN_PATTERNS):
        return fallback
    if len(trimmed.split()) < 12:
        return fallback

    if not trimmed.endswith(("?", "?!", "!?")):
        trimmed = trimmed.rstrip(".! ") + "?"
    return trimmed
