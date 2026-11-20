import os
from pathlib import Path

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class PersistenceSettings(BaseModel):
    db_path: Path | str = Field(default="./data/persistence.db")


class EmbeddingSettings(BaseModel):
    # Some of possible models: BAAI/bge-large-en-v1.5, all-MiniLM-L6-v2
    model_name: str = Field(default="BAAI/bge-large-en-v1.5")
    local_model_path: Path = Field(default=Path("./data/models/all-MiniLM-L6-v2"))
    # device represents the hardware execution device.
    # PyTorch supports "cpu" (universal CPUs), "cuda" (NVIDIA GPU), "mps" (Apple Silicon integrated GPU)
    device: str = "cpu"


class DraftingSettings(BaseModel):
    voice_examples_count: int = Field(default=3)
    knowledge_examples_count: int = Field(default=5)


class LlmSettings(BaseModel):
    api_key: SecretStr = Field(
        default_factory=lambda: SecretStr(os.getenv("LLM_API_KEY", ""))
    )
    model: str = Field(default="gemini/gemini-3.5-flash-lite")
    # low values for deterministic tasks, tool calling, and structured data extraction; high values for creative writing
    temperature: float = Field(default=0.2)
    max_tokens: int = Field(default=4096)


class AppConfig(BaseSettings):
    storage: PersistenceSettings = Field(default_factory=PersistenceSettings)
    drafting: DraftingSettings = Field(default_factory=DraftingSettings)
    embedding: EmbeddingSettings = Field(default=EmbeddingSettings())
    writer_llm: LlmSettings | None = None

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        toml_file="config.toml",
    )

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
            TomlConfigSettingsSource(settings_cls),
        )


class ConfigurationError(Exception):
    """Raised when required application configuration is missing or invalid."""

    def __init__(
        self,
        message: str,
        hint: str | None = None,
    ) -> None:
        super().__init__(message)
        self.hint = hint
