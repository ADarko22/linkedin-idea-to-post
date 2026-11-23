from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

from nicegui import ui

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


def _format_value(key: str, value: Any, reveal_secrets: bool) -> str:
    if value is None:
        return "—"
    if any(h in key.lower() for h in _SECRET_HINTS) and not reveal_secrets:
        return "••••••••" if str(value) else "—"
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(x) for x in value)
    return str(value)


def build_config_tab(ctx: AppContext, toml_path: Path | None = None) -> None:
    resolved_path = resolve_config_path(toml_path)
    state: dict[str, bool] = {"reveal_secrets": False}

    with ui.column().classes(
        "w-full max-w-5xl mx-auto h-[calc(100vh-110px)] gap-3 overflow-hidden"
    ):
        with ui.card().classes("w-full q-pa-md shrink-0"):
            with ui.row().classes(
                "w-full items-center justify-between gap-2 flex-wrap"
            ):
                with ui.column().classes("gap-0.5"):
                    ui.label("Configuration").classes("text-subtitle1 text-weight-bold")
                    ui.label(f"Target file: {resolved_path}").classes(
                        "text-caption text-grey-7 font-mono break-all"
                    )
                with ui.row().classes("items-center gap-2 flex-wrap"):
                    reveal_btn = ui.button(
                        "Show Secrets",
                        icon="visibility",
                        on_click=lambda: _toggle_secrets(),
                    ).props("flat dense")
                    ui.button(
                        "Validate",
                        icon="fact_check",
                        on_click=lambda: _validate_toml(),
                    ).props("outline dense")
                    ui.button(
                        "Save & Apply",
                        icon="check_circle",
                        color="primary",
                        on_click=lambda: _save_and_apply(),
                    ).props("dense unelevated")

        with ui.grid(columns=2).classes("w-full flex-1 min-h-0 gap-3"):
            with ui.card().classes(
                "w-full h-full q-pa-md flex flex-col min-h-0 overflow-hidden"
            ):
                ui.label("Active Settings").classes(
                    "text-subtitle2 text-weight-bold shrink-0 q-mb-xs"
                )
                sections_box = ui.column().classes(
                    "w-full flex-1 min-h-0 overflow-y-auto overflow-x-hidden gap-2 pr-1"
                )

            with ui.card().classes(
                "w-full h-full q-pa-md flex flex-col min-h-0 overflow-hidden"
            ):
                ui.label("TOML Editor").classes(
                    "text-subtitle2 text-weight-bold shrink-0 q-mb-xs"
                )
                initial_text = (
                    resolved_path.read_text(encoding="utf-8")
                    if resolved_path.exists()
                    else ""
                )
                toml_editor = (
                    ui.textarea(value=initial_text)
                    .props("outlined")
                    .classes(
                        "w-full flex-1 h-[calc(100vh-285px)] min-h-72 font-mono text-caption "
                        "[&_.q-field\\_\\_inner]:h-full [&_.q-field\\_\\_control]:h-full "
                        "[&_.q-field\\_\\_control-container]:h-full [&_textarea]:h-full [&_textarea]:overflow-y-auto"
                    )
                )

    def _render_structured() -> None:
        sections_box.clear()
        with sections_box:
            for section_name, section_val in ctx.config.model_dump().items():
                with ui.card().classes("w-full shrink-0 q-pa-sm bg-grey-1 border"):
                    ui.label(str(section_name)).classes(
                        "text-caption text-weight-bold text-uppercase text-primary q-mb-xs"
                    )
                    if isinstance(section_val, dict):
                        for k, v in section_val.items():
                            with ui.row().classes(
                                "w-full items-baseline justify-between gap-2 py-0.5 border-b border-grey-3"
                            ):
                                ui.label(str(k)).classes(
                                    "text-caption text-grey-8 font-mono shrink-0"
                                )
                                ui.label(
                                    _format_value(str(k), v, state["reveal_secrets"])
                                ).classes(
                                    "text-caption text-weight-medium text-right break-all"
                                )
                    else:
                        ui.label(
                            _format_value(
                                str(section_name), section_val, state["reveal_secrets"]
                            )
                        ).classes("text-caption break-all")

    def _parse_and_validate() -> AppConfig | None:
        try:
            parsed = tomllib.loads(toml_editor.value or "")
            return AppConfig.model_validate(parsed)
        except Exception as exc:
            ui.notify(f"Invalid configuration: {exc}", type="negative")
            return None

    def _validate_toml() -> None:
        if _parse_and_validate() is not None:
            ui.notify("TOML and AppConfig schema are valid.", type="positive")

    def _save_and_apply() -> None:
        new_cfg = _parse_and_validate()
        if new_cfg is None:
            return
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_path.write_text(toml_editor.value or "", encoding="utf-8")
        ctx.reload_config(new_cfg)
        _render_structured()
        ui.notify("Saved configuration and applied to active session.", type="positive")

    def _toggle_secrets() -> None:
        state["reveal_secrets"] = not state["reveal_secrets"]
        reveal_btn.set_text(
            "Hide Secrets" if state["reveal_secrets"] else "Show Secrets"
        )
        reveal_btn.props(
            f"icon={'visibility_off' if state['reveal_secrets'] else 'visibility'}"
        )
        _render_structured()

    _render_structured()
