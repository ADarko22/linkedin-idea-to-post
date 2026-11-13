from pathlib import Path

from pydantic import BaseModel, Field
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
    # writer: "dry-run" or "crewai"
    writer: str = Field(default="dry-run")


class AppConfig(BaseSettings):
    archive: ArchiveSettings = Field(default_factory=ArchiveSettings)
    drafting: DraftingSettings = Field(default_factory=DraftingSettings)

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
