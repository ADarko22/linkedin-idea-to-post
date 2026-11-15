import os
from pathlib import Path

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class ArchiveSettings(BaseModel):
    db_path: Path | str = Field(default="./data/archive.db")


class DraftingSettings(BaseModel):
    voice_examples_count: int = Field(default=3)


class LlmSettings(BaseModel):
    api_key: SecretStr = Field(
        default_factory=lambda: SecretStr(os.getenv("LLM_API_KEY", ""))
    )
    model: str = Field(default="gemini/gemini-3.5-flash-lite")
    # low values for deterministic tasks, tool calling, and structured data extraction; high values for creative writing
    temperature: float = Field(default=0.2)
    max_tokens: int = Field(default=4096)


class AppConfig(BaseSettings):
    archive: ArchiveSettings = Field(default_factory=ArchiveSettings)
    drafting: DraftingSettings = Field(default_factory=DraftingSettings)
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
