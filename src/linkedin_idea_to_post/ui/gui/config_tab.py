from __future__ import annotations

from pathlib import Path
from typing import Any

from nicegui import ui

from linkedin_idea_to_post.app_context import AppContext
from linkedin_idea_to_post.ui.gui import templates, theme
from linkedin_idea_to_post.ui.gui.config_state import (
    ConfigState,
    format_config_value,
    parse_and_validate_toml,
)

_TOML_EDITOR_CLASSES = (
    "w-full flex-1 h-[calc(100vh-285px)] min-h-72 font-mono text-caption "
    "[&_.q-field\\_\\_inner]:h-full [&_.q-field\\_\\_control]:h-full "
    "[&_.q-field\\_\\_control-container]:h-full [&_textarea]:h-full [&_textarea]:overflow-y-auto"
)


def _render_section_entries(
    section_name: str, section_val: Any, *, reveal_secrets: bool
) -> None:
    if not isinstance(section_val, dict):
        ui.label(
            format_config_value(
                section_name, section_val, reveal_secrets=reveal_secrets
            )
        ).classes("text-caption break-all")
        return

    for key, val in section_val.items():
        with ui.row().classes(
            "w-full items-baseline justify-between gap-2 py-0.5 border-b border-grey-3"
        ):
            ui.label(str(key)).classes("text-caption text-grey-8 font-mono shrink-0")
            ui.label(
                format_config_value(str(key), val, reveal_secrets=reveal_secrets)
            ).classes("text-caption text-weight-medium text-right break-all")


def _render_sections(sections_box: ui.column, state: ConfigState) -> None:
    sections_box.clear()
    with sections_box:
        for section_name, section_val in state.config_sections().items():
            with ui.card().classes("w-full shrink-0 q-pa-sm bg-grey-1 border"):
                ui.label(str(section_name)).classes(
                    "text-caption text-weight-bold text-uppercase text-primary q-mb-xs"
                )
                _render_section_entries(
                    str(section_name),
                    section_val,
                    reveal_secrets=state.reveal_secrets,
                )


def build_config_tab(ctx: AppContext, toml_path: Path | None = None) -> None:
    state = ConfigState.create(ctx, toml_path)

    with templates.wide_page():
        with templates.card_panel("shrink-0"):
            with theme.row_between("gap-2 flex-wrap"):
                with ui.column().classes("gap-0.5"):
                    theme.section_title("Configuration")
                    theme.mono_caption(
                        f"Target file: {state.resolved_path}", "break-all"
                    )
                with theme.row_gap_2("flex-wrap"):
                    reveal_btn = theme.flat_button("Show Secrets", icon="visibility")
                    validate_btn = theme.outline_button("Validate", icon="fact_check")
                    save_btn = theme.primary_button(
                        "Save & Apply", icon="check_circle", unelevated=True
                    )

        with templates.split_pane(columns=2):
            with templates.titled_card_panel("Active Settings"):
                sections_box = ui.column().classes(
                    "w-full flex-1 min-h-0 overflow-y-auto overflow-x-hidden gap-2 pr-1"
                )

            with templates.titled_card_panel("TOML Editor"):
                toml_editor = theme.outlined_textarea(
                    value=state.read_initial_toml(),
                    extra_classes=_TOML_EDITOR_CLASSES,
                )

    def on_toggle_secrets() -> None:
        revealed = state.toggle_secrets()
        reveal_btn.set_text("Hide Secrets" if revealed else "Show Secrets")
        reveal_btn.props(f"icon={'visibility_off' if revealed else 'visibility'}")
        _render_sections(sections_box, state)

    def on_validate() -> None:
        try:
            parse_and_validate_toml(toml_editor.value or "")
            ui.notify("TOML and AppConfig schema are valid.", type="positive")
        except Exception as exc:
            ui.notify(f"Invalid configuration: {exc}", type="negative")

    def on_save() -> None:
        try:
            state.save_and_apply(toml_editor.value or "")
        except Exception as exc:
            ui.notify(f"Invalid configuration: {exc}", type="negative")
            return
        _render_sections(sections_box, state)
        ui.notify("Saved configuration and applied to active session.", type="positive")

    reveal_btn.on_click(on_toggle_secrets)
    validate_btn.on_click(on_validate)
    save_btn.on_click(on_save)

    _render_sections(sections_box, state)
