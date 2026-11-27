from __future__ import annotations

from pathlib import Path

from nicegui import ui

from linkedin_idea_to_post.app_context import AppContext
from linkedin_idea_to_post.ui.gui import templates, theme
from linkedin_idea_to_post.ui.gui.config_state import (
    ConfigState,
    format_config_value,
    parse_and_validate_toml,
)


def _render_sections(sections_box: ui.column, state: ConfigState) -> None:
    sections_box.clear()
    with sections_box:
        for section_name, section_val in state.config_sections().items():
            name = str(section_name)
            if isinstance(section_val, dict):
                entries: list[tuple[str, str]] | str = [
                    (
                        str(k),
                        format_config_value(
                            str(k), v, reveal_secrets=state.reveal_secrets
                        ),
                    )
                    for k, v in section_val.items()
                ]
            else:
                entries = format_config_value(
                    name, section_val, reveal_secrets=state.reveal_secrets
                )
            templates.key_value_card(name, entries)


def build_config_tab(ctx: AppContext, toml_path: Path | None = None) -> None:
    state = ConfigState.create(ctx, toml_path)

    with templates.wide_page():
        with (
            templates.card_panel("shrink-0"),
            theme.row_between("gap-2 flex-wrap"),
        ):
            with theme.stack("gap-0.5", "col"):
                theme.section_title("Configuration")
                theme.mono_caption(f"Target file: {state.resolved_path}", "break-all")
            with theme.row_gap_2("flex-wrap"):
                reveal_btn = theme.flat_button("Show Secrets", icon="visibility")
                validate_btn = theme.outline_button("Validate", icon="fact_check")
                save_btn = theme.primary_button(
                    "Save & Apply", icon="check_circle", unelevated=True
                )

        with templates.split_pane(columns=2):
            with templates.titled_card_panel("Active Settings"):
                sections_box = theme.scroll_column()
            with templates.titled_card_panel("TOML Editor"):
                toml_editor = theme.toml_editor(state.read_initial_toml())

    def on_toggle_secrets() -> None:
        revealed = state.toggle_secrets()
        reveal_btn.set_text("Hide Secrets" if revealed else "Show Secrets")
        theme.set_icon(reveal_btn, "visibility_off" if revealed else "visibility")
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
