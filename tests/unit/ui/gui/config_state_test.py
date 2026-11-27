from __future__ import annotations

import tomllib
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from linkedin_idea_to_post.config import AppConfig
from linkedin_idea_to_post.ui.gui.config_state import (
    ConfigState,
    format_config_value,
    parse_and_validate_toml,
    resolve_config_path,
)


def test_resolve_config_path_prefers_explicit_then_env(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    explicit = tmp_path / "custom.toml"
    assert resolve_config_path(explicit) == explicit

    env_file = tmp_path / "env.toml"
    monkeypatch.setenv("LI2P_CONFIG", str(env_file))
    assert resolve_config_path() == env_file


def test_format_config_value_masks_secrets_unless_revealed() -> None:
    assert (
        format_config_value("api_key", "secret123", reveal_secrets=False) == "••••••••"
    )
    assert (
        format_config_value("api_key", "secret123", reveal_secrets=True) == "secret123"
    )
    assert format_config_value("api_key", "", reveal_secrets=False) == "—"
    assert format_config_value("tags", ["a", "b"], reveal_secrets=False) == "a, b"
    assert format_config_value("optional", None, reveal_secrets=False) == "—"


def test_parse_and_validate_toml_accepts_valid_and_rejects_invalid() -> None:
    cfg = parse_and_validate_toml("[storage]\npost_get_all_page_size = 42\n")
    assert cfg.storage.post_get_all_page_size == 42

    with pytest.raises(tomllib.TOMLDecodeError):
        parse_and_validate_toml("not = [valid toml")


def test_config_state_toggle_and_save_and_apply(tmp_path: Path) -> None:
    toml_path = tmp_path / "nested" / "config.toml"
    ctx = MagicMock()
    ctx.config = AppConfig()

    state = ConfigState.create(ctx, toml_path=toml_path)
    assert state.read_initial_toml() == ""
    assert state.toggle_secrets() is True
    assert state.toggle_secrets() is False

    raw = "[storage]\npost_get_all_page_size = 33\n"
    saved_cfg = state.save_and_apply(raw)
    assert saved_cfg.storage.post_get_all_page_size == 33
    assert toml_path.read_text(encoding="utf-8") == raw
    ctx.reload_config.assert_called_once_with(saved_cfg)
