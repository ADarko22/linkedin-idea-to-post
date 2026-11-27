from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from linkedin_idea_to_post.app_context import AppContext
from linkedin_idea_to_post.config import AppConfig

_SECRET_HINTS = ("key", "secret", "token", "password", "api_key")


def resolve_config_path(explicit_path: Path | None = None) -> Path:
    if explicit_path is not None:
        return explicit_path
    env_path = os.environ.get("LI2P_CONFIG") or os.environ.get(
        "LINKEDIN_IDEA_TO_POST_CONFIG"
    )
    if env_path:
        return Path(env_path).expanduser()
    cwd_toml = Path("config.toml")
    if cwd_toml.exists():
        return cwd_toml.resolve()
    return Path.home() / ".config" / "linkedin-idea-to-post" / "config.toml"


def format_config_value(key: str, value: Any, *, reveal_secrets: bool) -> str:
    if value is None:
        return "—"
    if any(hint in key.lower() for hint in _SECRET_HINTS) and not reveal_secrets:
        return "••••••••" if str(value) else "—"
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(x) for x in value)
    return str(value)


def parse_and_validate_toml(raw_text: str) -> AppConfig:
    parsed = tomllib.loads(raw_text)
    return AppConfig.model_validate(parsed)


@dataclass
class ConfigState:
    ctx: AppContext
    resolved_path: Path
    reveal_secrets: bool = False

    @classmethod
    def create(cls, ctx: AppContext, toml_path: Path | None = None) -> ConfigState:
        return cls(ctx=ctx, resolved_path=resolve_config_path(toml_path))

    def read_initial_toml(self) -> str:
        if self.resolved_path.exists():
            return self.resolved_path.read_text(encoding="utf-8")
        return ""

    def toggle_secrets(self) -> bool:
        self.reveal_secrets = not self.reveal_secrets
        return self.reveal_secrets

    def config_sections(self) -> dict[str, Any]:
        return self.ctx.config.model_dump()

    def save_and_apply(self, raw_text: str) -> AppConfig:
        new_cfg = parse_and_validate_toml(raw_text)
        self.resolved_path.parent.mkdir(parents=True, exist_ok=True)
        self.resolved_path.write_text(raw_text, encoding="utf-8")
        self.ctx.reload_config(new_cfg)
        return new_cfg
