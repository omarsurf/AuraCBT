from pathlib import Path

import pytest

from backend.app.core.config import get_settings
from backend.app.core.config import Settings


REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_settings_defaults():
    settings = get_settings()
    assert settings.app_name == "CBT Chat Backend"
    assert settings.llm_model_path.name == "qwen05b-cbt-lora-merged"
    assert settings.max_history_messages == 12
    assert "http://localhost:5173" in settings.allowed_origins


def test_settings_env_overrides_and_allowed_origins_parse(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("APP_NAME", "Overridden Backend")
    monkeypatch.setenv(
        "ALLOWED_ORIGINS",
        '["http://localhost:5173", "http://127.0.0.1:5173"]',
    )

    settings = get_settings()

    assert settings.app_name == "Overridden Backend"
    assert settings.allowed_origins == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


def test_settings_env_file_path_is_absolute():
    assert Settings.model_config["env_file"] == REPO_ROOT / "backend" / ".env"
