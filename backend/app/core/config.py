from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT_DIR / "backend" / ".env"


class Settings(BaseSettings):
    app_name: str = "CBT Chat Backend"
    llm_model_path: Path = ROOT_DIR / "models" / "qwen05b-cbt-lora-merged"
    emotion_model_name_or_path: str = "j-hartmann/emotion-english-distilroberta-base"
    max_history_messages: int = 12
    max_new_tokens: int = 110
    temperature: float = 0.55
    top_p: float = 0.9
    repetition_penalty: float = 1.1
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
