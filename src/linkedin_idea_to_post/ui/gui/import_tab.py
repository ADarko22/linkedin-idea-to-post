from __future__ import annotations

from pathlib import Path

from nicegui import events, ui

from linkedin_idea_to_post.app_context import AppContext
from linkedin_idea_to_post.ui.gui import components, templates, theme
from linkedin_idea_to_post.ui.gui.helpers import run_blocking
from linkedin_idea_to_post.ui.gui.import_state import (
    ImportState,
    save_posts,
    write_temp_file,
)
from linkedin_idea_to_post.use_case.linkedin_ingestion.model import (
    CsvImporterPrepareResult,
)


def _render_errors(
    errors_box: ui.column,
    errors_expansion: ui.expansion,
    res: CsvImporterPrepareResult,
) -> None:
    errors_box.clear()
    total = len(res.parsing_errors) + len(res.mapping_errors)
    errors_expansion.set_visibility(total > 0)
    if total == 0:
        return

    errors_expansion.set_text(f"Parsing & Mapping Errors ({total})")
    with errors_box:
        for err in res.parsing_errors:
            ui.label(f"Row {err.row} [{err.field}]: {err.message}").classes(
                theme.ERROR_CAPTION
            )
        for m_err in res.mapping_errors:
            for f_err in m_err.errors:
                ui.label(
                    f"Row {m_err.raw_post.row} [{f_err.field}]: {f_err.message}"
                ).classes(theme.ERROR_CAPTION)


def build_import_tab(ctx: AppContext) -> None:
    state = ImportState()
    checkboxes: list[ui.checkbox] = []

    with templates.narrow_page():
        status_banner, banner_label = templates.status_banner()

        upload_view = templates.card_panel()
        with upload_view:
            theme.section_title("Import LinkedIn Shares CSV")
            theme.muted_caption(
                "Upload your LinkedIn Shares.csv export or enter a local file path to preview posts before importing."
            )
            path_input = theme.outlined_input(
                "Path to Shares.csv", placeholder="/path/to/Shares.csv"
            )
            with theme.row_between("q-mt-xs"):
                upload_widget = ui.upload(auto_upload=True, max_files=1).props(
                    "accept=.csv flat bordered label='Choose Shares.csv'"
                )
                parse_btn = theme.primary_button("Parse & Preview", icon="preview")

        preview_view = templates.narrow_page()
        preview_view.set_visibility(False)
        with preview_view:
            with ui.card().classes("w-full q-pa-sm"), theme.row_between():
                summary_row = theme.row_gap_2()
                with theme.row_gap_2():
                    select_all_btn = theme.flat_button("All")
                    select_none_btn = theme.flat_button("None")
                    cancel_btn = theme.outline_button(
                        "Cancel", icon="close", dense=False
                    )
                    import_btn = theme.positive_button("Import Selected", icon="check")

            errors_expansion = ui.expansion(
                "Parsing & Mapping Errors", icon="warning"
            ).classes("w-full bg-orange-1 rounded border border-orange-4")
            errors_expansion.set_visibility(False)
            with errors_expansion:
                errors_box = ui.column().classes("w-full gap-1 q-pa-sm")

            with theme.scroll_box():
                posts_box = ui.column().classes("w-full gap-2")

    def reset_view(banner_message: str | None = None) -> None:
        state.reset()
        checkboxes.clear()
        posts_box.clear()
        errors_box.clear()
        errors_expansion.set_visibility(False)
        upload_widget.reset()
        path_input.set_value("")
        preview_view.set_visibility(False)
        upload_view.set_visibility(True)
        banner_label.set_text(banner_message or "")
        status_banner.set_visibility(bool(banner_message))

    def show_preview(res: CsvImporterPrepareResult) -> None:
        status_banner.set_visibility(False)
        summary_row.clear()
        posts_box.clear()
        checkboxes.clear()

        with summary_row:
            ui.badge(f"Valid: {len(res.posts)}", color="positive")
            if res.parsing_errors:
                ui.badge(f"Parse errors: {len(res.parsing_errors)}", color="warning")
            if res.mapping_errors:
                ui.badge(f"Map errors: {len(res.mapping_errors)}", color="negative")

        _render_errors(errors_box, errors_expansion, res)

        with posts_box:
            if not res.posts:
                theme.empty_state_label("No valid posts found in this CSV.")
            for idx, post in enumerate(res.posts):
                tag_badge = f"{len(post.hashtags)} tag(s)" if post.hashtags else None

                def _on_toggle(checked: bool, _cb: ui.checkbox, i: int = idx) -> None:
                    state.toggle(i, checked)

                _, cb = components.expandable_post_card(
                    post,
                    selected=idx in state.selected_indices,
                    on_toggle=_on_toggle,
                    badge_text=tag_badge,
                    badge_color="grey-7",
                )
                checkboxes.append(cb)

        import_btn.set_enabled(bool(res.posts))
        upload_view.set_visibility(False)
        preview_view.set_visibility(True)

    async def on_upload(e: events.UploadEventArguments) -> None:
        suffix = Path(e.file.name).suffix or ".csv"
        data = await e.file.read()
        tmp_path = await run_blocking(lambda: write_temp_file(data, suffix))
        state.set_temp_file(tmp_path)
        path_input.set_value(str(tmp_path))

    async def on_parse() -> None:
        raw_path = (path_input.value or "").strip()
        if not raw_path:
            ui.notify("Upload a CSV file or enter a path first.", type="warning")
            return
        csv_path = Path(raw_path)
        if not csv_path.is_file():
            ui.notify(f"File not found: {csv_path}", type="negative")
            return

        async def _parse() -> None:
            prepared = await run_blocking(lambda: ctx.csv_importer.prepare(csv_path))
            state.set_prepared(prepared)
            show_preview(prepared)

        await components.run_with_disabled([parse_btn], _parse)

    async def on_import() -> None:
        selected = state.selected_posts()
        if not selected:
            ui.notify("Select at least one post to import.", type="warning")
            return

        async def _import() -> None:
            await run_blocking(lambda: save_posts(ctx, selected))
            msg = f"Successfully imported {len(selected)} post(s) into storage."
            ui.notify(msg, type="positive")
            reset_view(msg)

        await components.run_with_disabled([import_btn, cancel_btn], _import)

    def on_select_all() -> None:
        state.select_all()
        for cb in checkboxes:
            cb.set_value(True)

    def on_select_none() -> None:
        state.select_none()
        for cb in checkboxes:
            cb.set_value(False)

    upload_widget.on_upload(on_upload)
    parse_btn.on_click(on_parse)
    select_all_btn.on_click(on_select_all)
    select_none_btn.on_click(on_select_none)
    cancel_btn.on_click(lambda: reset_view())
    import_btn.on_click(on_import)
