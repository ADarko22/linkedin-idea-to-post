from __future__ import annotations

from pathlib import Path

from nicegui import events, ui

from linkedin_idea_to_post.app_context import AppContext
from linkedin_idea_to_post.ui.gui import components, layout, primitives
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
            primitives.text(f"Row {err.row} [{err.field}]: {err.message}", tone="error")
        for m_err in res.mapping_errors:
            for f_err in m_err.errors:
                primitives.text(
                    f"Row {m_err.raw_post.row} [{f_err.field}]: {f_err.message}",
                    tone="error",
                )


def build_import_tab(ctx: AppContext) -> None:
    state = ImportState()
    checkboxes: list[ui.checkbox] = []

    with layout.page_container():
        status_banner, banner_label = layout.status_banner()

        upload_view = layout.panel_card(size="md")
        with upload_view:
            primitives.heading("Import LinkedIn Shares CSV", level=1)
            primitives.text(
                "Upload your LinkedIn Shares.csv export or enter a local file path to preview posts before importing.",
                tone="muted",
            )
            path_input = primitives.text_input(
                "Path to Shares.csv", placeholder="/path/to/Shares.csv"
            )
            with primitives.row(justify="between"):
                upload_widget = primitives.csv_upload()
                parse_btn = primitives.button(
                    "Parse & Preview", icon="preview", variant="primary"
                )

        preview_view = layout.panel_card(size="fill")
        preview_view.set_visibility(False)
        with preview_view:
            with primitives.row(justify="between", wrap=True, shrink=True):
                summary_row = primitives.row(full_width=False, gap="xs")
                with primitives.row(full_width=False, gap="xs"):
                    select_all_btn = primitives.button("All", variant="flat")
                    select_none_btn = primitives.button("None", variant="flat")
                    cancel_btn = primitives.button(
                        "Cancel", icon="close", variant="outline"
                    )
                    import_btn = primitives.button(
                        "Import Selected", icon="check", variant="positive"
                    )

            errors_expansion, errors_box = layout.warning_expansion(
                "Parsing & Mapping Errors"
            )
            ui.separator()
            posts_box = primitives.column(scroll=True)

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
            primitives.pill(f"Valid: {len(res.posts)}", tone="published")
            if res.parsing_errors:
                primitives.pill(
                    f"Parse errors: {len(res.parsing_errors)}", tone="draft"
                )
            if res.mapping_errors:
                primitives.pill(f"Map errors: {len(res.mapping_errors)}", tone="draft")

        _render_errors(errors_box, errors_expansion, res)

        with posts_box:
            if not res.posts:
                primitives.text("No valid posts found in this CSV.", tone="empty")
            for idx, post in enumerate(res.posts):
                tag_badge = f"{len(post.hashtags)} tag(s)" if post.hashtags else None

                def _on_toggle(checked: bool, _cb: ui.checkbox, i: int = idx) -> None:
                    state.toggle(i, checked)

                _, cb = components.expandable_post_card(
                    post,
                    selected=idx in state.selected_indices,
                    on_toggle=_on_toggle,
                    badge_text=tag_badge,
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
