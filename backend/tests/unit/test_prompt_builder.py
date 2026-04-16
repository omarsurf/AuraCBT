import backend.app.services as services

import pytest

from backend.app.services.prompt_builder import build_system_prompt


def test_build_system_prompt_contains_global_rules():
    prompt = build_system_prompt("validate_and_support")
    assert "Never invent facts" in prompt
    assert "Keep the answer concise" in prompt
    assert "STRATEGY: validate_and_support" in prompt


@pytest.mark.parametrize(
    ("strategy", "expected_marker"),
    [
        ("validate_and_support", "sad, lonely, discouraged"),
        ("reassure_and_structure", "anxious, fearful, stressed"),
        ("deescalate_and_reflect", "angry, irritated, resentful"),
        ("encourage_and_reinforce", "happy, relieved, hopeful"),
        ("normal_support", "neutral, mixed, or unclear"),
    ],
)
def test_build_system_prompt_contains_each_known_strategy_block(strategy: str, expected_marker: str):
    prompt = build_system_prompt(strategy)
    assert f"STRATEGY: {strategy}" in prompt
    assert expected_marker in prompt


def test_build_system_prompt_falls_back_to_normal_support():
    prompt = build_system_prompt("mystery")
    assert "STRATEGY: normal_support" in prompt


def test_services_package_exports_are_explicit():
    assert services.__all__ == (
        "choose_strategy",
        "normalize_emotion",
        "build_system_prompt",
    )
