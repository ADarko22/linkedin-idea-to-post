from __future__ import annotations

import os
from pathlib import Path

from platformdirs import user_data_path
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from linkedin_idea_to_post.domain import retrieval, storage

APP_NAME = "linkedin-idea-to-post"
APP_DIR = user_data_path(APP_NAME, appauthor=False)


def ensure_app_dirs(config: AppConfig) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    Path(config.storage.db_path).parent.mkdir(parents=True, exist_ok=True)
    Path(config.embedding.local_model_path).parent.mkdir(parents=True, exist_ok=True)


def resolve_config_path() -> Path:
    if env_path := os.getenv("LI2P_CONFIG"):
        return Path(env_path).expanduser()
    config_toml = "config.toml"
    if Path(config_toml).exists():
        return Path(config_toml).resolve()
    return APP_DIR / config_toml


class PersistenceSettings(BaseModel):
    db_path: Path = Field(default=APP_DIR / "archive.db")
    post_retrieval_max_results: int = Field(default=retrieval.DEFAULT_MAX_RESULTS)
    post_get_all_page_size: int = Field(default=storage.DEFAULT_PAGE_SIZE)


class EmbeddingSettings(BaseModel):
    # Some of possible models: BAAI/bge-large-en-v1.5, all-MiniLM-L6-v2
    model_name: str = Field(default="BAAI/bge-large-en-v1.5")
    local_model_path: Path = Field(default=APP_DIR / "models" / "all-MiniLM-L6-v2")
    # device represents the hardware execution device.
    # PyTorch supports "cpu" (universal CPUs), "cuda" (NVIDIA GPU), "mps" (Apple Silicon integrated GPU)
    device: str = "cpu"


class DraftingSettings(BaseModel):
    voice_examples_count: int = Field(default=3)
    knowledge_examples_count: int = Field(default=5)
    draft_history_limit: int = Field(default=10, ge=1)


class LlmSettings(BaseModel):
    api_key: SecretStr = Field(
        default_factory=lambda: SecretStr(os.getenv("LLM_API_KEY", ""))
    )
    model: str = Field(default="gemini/gemini-3.5-flash-lite")
    temperature: float = Field(default=0.2)
    max_tokens: int = Field(default=4096)


class AppConfig(BaseSettings):
    storage: PersistenceSettings = Field(default_factory=PersistenceSettings)
    drafting: DraftingSettings = Field(default_factory=DraftingSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    writer_llm: LlmSettings | None = None

    model_config = SettingsConfigDict(env_nested_delimiter="__")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            TomlConfigSettingsSource(settings_cls, toml_file=resolve_config_path()),
        )


class ConfigurationError(Exception):
    """Raised when required application configuration is missing or invalid."""

    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(message)
        self.hint = hint
