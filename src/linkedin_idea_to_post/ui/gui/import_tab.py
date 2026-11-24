from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
import tempfile

from nicegui import events, ui

from linkedin_idea_to_post.app_context import AppContext
from linkedin_idea_to_post.domain.post import Post
from linkedin_idea_to_post.ui.gui import styles
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
    selection_boxes: list[tuple[int, ui.checkbox]] = field(default_factory=list)


def _write_temp_file(data: bytes | str, suffix: str) -> Path:
    mode = "wb" if isinstance(data, bytes) else "w"
    encoding = None if isinstance(data, bytes) else "utf-8"
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=suffix, mode=mode, encoding=encoding
    ) as tmp:
        tmp.write(data)
        return Path(tmp.name)


def _cleanup_temp_file(state: _ImportState) -> None:
    if state.temp_file and state.temp_file.exists():
        state.temp_file.unlink(missing_ok=True)
    state.temp_file = None


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
                styles.ERROR_CAPTION
            )
        for m_err in res.mapping_errors:
            for f_err in m_err.errors:
                ui.label(
                    f"Row {m_err.raw_post.row} [{f_err.field}]: {f_err.message}"
                ).classes(styles.ERROR_CAPTION)


def _render_post_card(
    selection_boxes: list[tuple[int, ui.checkbox]], idx: int, post: Post
) -> None:
    with (
        ui.card().classes("w-full q-pa-none overflow-hidden"),
        ui.row().classes("w-full items-center no-wrap px-2"),
    ):
        cb = ui.checkbox(value=True).classes("shrink-0")
        selection_boxes.append((idx, cb))

        expansion = ui.expansion().classes("col min-w-0")
        with expansion.add_slot("header"), styles.row_between("gap-2 py-1 min-w-0"):
            label = styles.post_preview_label(
                post_short_preview(post), "truncate col min-w-0"
            )
            label.bind_visibility_from(
                expansion, "value", backward=lambda expanded: not expanded
            )
            if post.hashtags:
                ui.badge(f"{len(post.hashtags)} tag(s)", color="grey-7").classes(
                    "shrink-0"
                )

        with expansion, ui.column().classes("w-full q-pa-sm pt-0 gap-2"):
            ui.separator()
            tags = format_hashtags(post)
            if tags:
                styles.tags_label(tags)
            styles.post_body_label(post.body)


def _save_posts_sync(ctx: AppContext, posts: list[Post]) -> None:
    for post in posts:
        ctx.post_store_manager.save_post(post)


def build_import_tab(ctx: AppContext) -> None:
    state = _ImportState()

    with styles.narrow_column():
        status_banner = ui.row().classes(
            "w-full items-center justify-between bg-green-1 text-green-10 "
            "q-pa-sm rounded border border-green-4"
        )
        status_banner.set_visibility(False)
        with status_banner:
            banner_label = ui.label("").classes("text-body2 text-weight-medium")
            styles.flat_button(
                icon="close",
                on_click=lambda: status_banner.set_visibility(False),
                extra_props="round size=sm",
            )

        upload_view = styles.card_panel()
        with upload_view:
            styles.section_title("Import LinkedIn Shares CSV")
            styles.muted_caption(
                "Upload your LinkedIn Shares.csv export or enter a local file path to preview posts before importing."
            )
            path_input = styles.outlined_input(
                "Path to Shares.csv", placeholder="/path/to/Shares.csv"
            )
            with styles.row_between("q-mt-xs"):
                upload_widget = ui.upload(auto_upload=True, max_files=1).props(
                    "accept=.csv flat bordered label='Choose Shares.csv'"
                )
                parse_btn = styles.primary_button("Parse & Preview", icon="preview")

        preview_view = styles.narrow_column()
        preview_view.set_visibility(False)
        with preview_view:
            with ui.card().classes("w-full q-pa-sm"), styles.row_between():
                summary_row = styles.row_gap_2()
                with styles.row_gap_2():
                    select_all_btn = styles.flat_button("All")
                    select_none_btn = styles.flat_button("None")
                    cancel_btn = styles.outline_button("Cancel", icon="close", dense=False)
                    import_btn = styles.positive_button("Import Selected", icon="check")

            errors_expansion = ui.expansion(
                "Parsing & Mapping Errors", icon="warning"
            ).classes("w-full bg-orange-1 rounded border border-orange-4")
            errors_expansion.set_visibility(False)
            with errors_expansion:
                errors_box = ui.column().classes("w-full gap-1 q-pa-sm")

            with styles.scroll_box():
                posts_box = ui.column().classes("w-full gap-2")

    def reset_view(banner_message: str | None = None) -> None:
        _cleanup_temp_file(state)
        state.prepared = None
        state.selection_boxes.clear()
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
        state.selection_boxes.clear()

        with summary_row:
            ui.badge(f"Valid: {len(res.posts)}", color="positive")
            if res.parsing_errors:
                ui.badge(f"Parse errors: {len(res.parsing_errors)}", color="warning")
            if res.mapping_errors:
                ui.badge(f"Map errors: {len(res.mapping_errors)}", color="negative")

        _render_errors(errors_box, errors_expansion, res)

        with posts_box:
            if not res.posts:
                styles.empty_state_label("No valid posts found in this CSV.")
            for idx, post in enumerate(res.posts):
                _render_post_card(state.selection_boxes, idx, post)

        import_btn.set_enabled(bool(res.posts))
        upload_view.set_visibility(False)
        preview_view.set_visibility(True)

    async def on_upload(e: events.UploadEventArguments) -> None:
        _cleanup_temp_file(state)
        suffix = Path(e.file.name).suffix or ".csv"
        data = await e.file.read()
        tmp_path = await asyncio.to_thread(_write_temp_file, data, suffix)
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
            show_preview(prepared)
        finally:
            parse_btn.enable()

    async def on_import() -> None:
        if state.prepared is None:
            return
        selected = [
            state.prepared.posts[idx] for idx, cb in state.selection_boxes if cb.value
        ]
        if not selected:
            ui.notify("Select at least one post to import.", type="warning")
            return

        import_btn.disable()
        cancel_btn.disable()
        try:
            await run_blocking(lambda: _save_posts_sync(ctx, selected))
            msg = f"Successfully imported {len(selected)} post(s) into storage."
            ui.notify(msg, type="positive")
            reset_view(msg)
        finally:
            import_btn.enable()
            cancel_btn.enable()

    upload_widget.on_upload(on_upload)
    parse_btn.on_click(on_parse)
    select_all_btn.on_click(
        lambda: [cb.set_value(True) for _, cb in state.selection_boxes]
    )
    select_none_btn.on_click(
        lambda: [cb.set_value(False) for _, cb in state.selection_boxes]
    )
    cancel_btn.on_click(lambda: reset_view())
    import_btn.on_click(on_import)