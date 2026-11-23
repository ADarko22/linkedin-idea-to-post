from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path

from nicegui import events, ui

from linkedin_idea_to_post.app_context import AppContext
from linkedin_idea_to_post.domain.post import Post
from linkedin_idea_to_post.ui.gui.helpers import (
    format_hashtags,
    post_short_preview,
    run_blocking,
)
from linkedin_idea_to_post.use_case.linkedin_ingestion.model import (
    CsvImporterPrepareResult,
)


@dataclass
class _ImportState:
    prepared: CsvImporterPrepareResult | None = None
    temp_file: Path | None = None
    last_import_message: str | None = None


def build_import_tab(ctx: AppContext) -> None:
    state = _ImportState()
    selection_boxes: list[tuple[int, ui.checkbox]] = []

    with ui.column().classes("w-full max-w-4xl mx-auto gap-3"):
        # Banner shown after a successful import when returning to initial view
        status_banner = ui.row().classes(
            "w-full items-center justify-between bg-green-1 text-green-10 "
            "q-pa-sm rounded border border-green-4"
        )
        status_banner.set_visibility(False)
        with status_banner:
            status_banner_label = ui.label("").classes("text-body2 text-weight-medium")
            ui.button(
                icon="close",
                on_click=lambda: status_banner.set_visibility(False),
            ).props("flat dense round size=sm")

        # --- VIEW 1: Initial Upload / File Selection ---
        upload_view = ui.card().classes("w-full q-pa-md gap-3")
        with upload_view:
            ui.label("Import LinkedIn Shares CSV").classes(
                "text-subtitle1 text-weight-bold"
            )
            ui.label(
                "Upload your LinkedIn Shares.csv export or enter a local file path to preview posts before importing."
            ).classes("text-caption text-grey-7")

            path_input = (
                ui.input(
                    label="Path to Shares.csv",
                    placeholder="/path/to/Shares.csv",
                )
                .props("outlined dense clearable")
                .classes("w-full")
            )

            with ui.row().classes("w-full items-center justify-between gap-3 q-mt-xs"):
                upload_widget = ui.upload(
                    auto_upload=True,
                    max_files=1,
                ).props("accept=.csv flat bordered label='Choose Shares.csv'")

                parse_btn = ui.button(
                    "Parse & Preview", icon="preview", color="primary"
                )

        # --- VIEW 2: Parsed Preview & Selection ---
        preview_view = ui.column().classes("w-full gap-3")
        preview_view.set_visibility(False)

        with preview_view:
            # Pinned action & summary bar
            with ui.card().classes("w-full q-pa-sm"):
                with ui.row().classes("w-full items-center justify-between gap-3"):
                    summary_row = ui.row().classes("items-center gap-2")

                    with ui.row().classes("items-center gap-2"):
                        select_all_btn = ui.button("All").props("flat dense")
                        select_none_btn = ui.button("None").props("flat dense")
                        cancel_btn = ui.button("Cancel", icon="close").props("outline")
                        import_btn = ui.button(
                            "Import Selected", icon="check", color="positive"
                        )

            # Collapsible errors drawer (only visible when errors exist)
            errors_expansion = ui.expansion(
                "Parsing & Mapping Errors", icon="warning"
            ).classes("w-full bg-orange-1 rounded border border-orange-4")
            errors_expansion.set_visibility(False)
            with errors_expansion:
                errors_box = ui.column().classes("w-full gap-1 q-pa-sm")

            # Bounded scrollable list so header & buttons stay on screen
            with ui.scroll_area().classes(
                "w-full h-[calc(100vh-300px)] min-h-72 border rounded q-pa-sm"
            ):
                posts_box = ui.column().classes("w-full gap-2")

    def _cleanup_temp_file() -> None:
        if state.temp_file and state.temp_file.exists():
            state.temp_file.unlink(missing_ok=True)
        state.temp_file = None

    def _reset_to_initial(*, banner_message: str | None = None) -> None:
        _cleanup_temp_file()
        state.prepared = None
        selection_boxes.clear()
        posts_box.clear()
        errors_box.clear()
        errors_expansion.set_visibility(False)
        upload_widget.reset()
        path_input.set_value("")

        preview_view.set_visibility(False)
        upload_view.set_visibility(True)

        if banner_message:
            status_banner_label.set_text(banner_message)
            status_banner.set_visibility(True)
        else:
            status_banner.set_visibility(False)

    def _render_preview_post(idx: int, post: Post) -> None:
        with ui.card().classes("w-full q-pa-none overflow-hidden"):
            with ui.row().classes("w-full items-center no-wrap px-2"):
                cb = ui.checkbox(value=True).classes("shrink-0")
                selection_boxes.append((idx, cb))

                expansion = ui.expansion().classes("col min-w-0")
                with expansion.add_slot("header"):
                    with ui.row().classes(
                        "w-full items-center justify-between gap-2 py-1 min-w-0"
                    ):
                        preview_label = ui.label(post_short_preview(post)).classes(
                            "text-body2 text-weight-medium truncate col min-w-0"
                        )
                        preview_label.bind_visibility_from(
                            expansion, "value", backward=lambda expanded: not expanded
                        )
                        if post.hashtags:
                            ui.badge(
                                f"{len(post.hashtags)} tag(s)", color="grey-7"
                            ).classes("shrink-0")

                with expansion, ui.column().classes("w-full q-pa-sm pt-0 gap-2"):
                    ui.separator()
                    tags_str = format_hashtags(post)
                    if tags_str:
                        ui.label(tags_str).classes("text-caption text-primary")
                    ui.label(post.body).classes(
                        "text-body2 whitespace-pre-line leading-relaxed"
                    )

    def _show_preview(res: CsvImporterPrepareResult) -> None:
        status_banner.set_visibility(False)
        summary_row.clear()
        errors_box.clear()
        posts_box.clear()
        selection_boxes.clear()

        with summary_row:
            ui.badge(f"Valid: {len(res.posts)}", color="positive")
            if res.parsing_errors:
                ui.badge(f"Parse errors: {len(res.parsing_errors)}", color="warning")
            if res.mapping_errors:
                ui.badge(f"Map errors: {len(res.mapping_errors)}", color="negative")

        total_errors = len(res.parsing_errors) + len(res.mapping_errors)
        errors_expansion.set_visibility(total_errors > 0)
        if total_errors > 0:
            errors_expansion.set_text(f"Parsing & Mapping Errors ({total_errors})")
            with errors_box:
                for err in res.parsing_errors:
                    ui.label(f"Row {err.row} [{err.field}]: {err.message}").classes(
                        "text-negative text-caption"
                    )
                for m_err in res.mapping_errors:
                    for f_err in m_err.errors:
                        ui.label(
                            f"Row {m_err.raw_post.row} [{f_err.field}]: {f_err.message}"
                        ).classes("text-negative text-caption")

        with posts_box:
            if not res.posts:
                ui.label("No valid posts found in this CSV.").classes(
                    "text-grey text-center w-full py-6"
                )
            for idx, post in enumerate(res.posts):
                _render_preview_post(idx, post)

        import_btn.set_enabled(bool(res.posts))
        upload_view.set_visibility(False)
        preview_view.set_visibility(True)

    async def on_upload(e: events.UploadEventArguments) -> None:
        _cleanup_temp_file()
        suffix = Path(e.file.name).suffix or ".csv"
        data = await e.file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(data)
            tmp_path = Path(tmp.name)
        state.temp_file = tmp_path
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

        parse_btn.disable()
        try:
            prepared = await run_blocking(lambda: ctx.csv_importer.prepare(csv_path))
            state.prepared = prepared
            _show_preview(prepared)
        finally:
            parse_btn.enable()

    async def on_import_selected() -> None:
        prepared = state.prepared
        if prepared is None:
            return

        selected_posts = [
            prepared.posts[idx] for idx, cb in selection_boxes if cb.value
        ]
        if not selected_posts:
            ui.notify("Select at least one post to import.", type="warning")
            return

        import_btn.disable()
        cancel_btn.disable()
        try:
            # Replace with your exact PostStoreManagementService batch/save method
            await run_blocking(
                lambda: (
                    ctx.post_store_manager.save_post(post) for post in selected_posts
                )
            )
            count = len(selected_posts)
            msg = f"Successfully imported {count} post(s) into storage."
            ui.notify(msg, type="positive")
            _reset_to_initial(banner_message=msg)
        finally:
            import_btn.enable()
            cancel_btn.enable()

    upload_widget.on_upload(on_upload)
    parse_btn.on_click(on_parse)
    select_all_btn.on_click(lambda: [cb.set_value(True) for _, cb in selection_boxes])
    select_none_btn.on_click(lambda: [cb.set_value(False) for _, cb in selection_boxes])
    cancel_btn.on_click(lambda: _reset_to_initial())
    import_btn.on_click(on_import_selected)
