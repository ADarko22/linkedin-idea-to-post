from __future__ import annotations

from datetime import UTC, datetime

from nicegui import ui

from linkedin_idea_to_post.app_context import AppContext
from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus
from linkedin_idea_to_post.domain.post_helpers import extract_hashtags
from linkedin_idea_to_post.domain.storage import PostGetQuery
from linkedin_idea_to_post.ui.gui.helpers import (
    format_hashtags,
    post_short_preview,
    run_blocking,
)


def _format_created_at(post: Post) -> str:
    return post.created_at.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC")


def build_posts_tab(ctx: AppContext) -> None:
    state: dict[str, int] = {
        "page": 1,
        "limit": ctx.config.storage.post_get_all_page_size,
    }

    # --- Overlay: Post Reader & Draft Editor ---
    post_dialog = ui.dialog().props("backdrop-filter='blur(2px)'")
    with (
        post_dialog,
        ui.card().classes("w-full max-w-3xl q-pa-md gap-3 overflow-x-hidden"),
    ):
        with ui.row().classes("w-full items-center justify-between gap-2 flex-wrap"):
            with ui.row().classes("items-center gap-2"):
                dialog_meta = ui.label("").classes("text-caption text-grey-7 font-mono")
                dialog_badge = ui.badge("")
            ui.button(
                icon="close",
                on_click=post_dialog.close,
            ).props("flat round dense color=grey-8")

        dialog_tags = ui.label("").classes(
            "text-caption text-primary whitespace-normal break-words"
        )

        with ui.scroll_area().classes(
            "w-full h-80 border rounded q-pa-sm overflow-x-hidden"
        ):
            dialog_body = ui.label("").classes(
                "text-body2 whitespace-pre-line break-words leading-relaxed"
            )

        edit_container = ui.column().classes("w-full gap-2")
        edit_container.set_visibility(False)
        with edit_container:
            body_editor = (
                ui.textarea(label="Edit post body")
                .props("outlined autogrow")
                .classes("w-full")
            )
            with ui.row().classes("gap-2 justify-end w-full"):
                cancel_edit_btn = ui.button("Cancel").props("flat")
                save_edit_btn = ui.button("Save Changes", icon="save", color="primary")

        dialog_footer = ui.row().classes("w-full justify-end gap-2")

    active_post_ref: dict[str, Post | None] = {"post": None}

    def _set_edit_mode(editing: bool, post: Post | None = None) -> None:
        edit_container.set_visibility(editing)
        dialog_body.set_visibility(not editing)
        if editing and post is not None:
            body_editor.set_value(post.body)

    def _open_post_dialog(post: Post) -> None:
        active_post_ref["post"] = post
        _set_edit_mode(False)

        dialog_meta.set_text(_format_created_at(post))
        badge_color = "positive" if post.status == PostStatus.PUBLISHED else "warning"
        dialog_badge.set_text(f"{post.origin.value} · {post.status.value}")
        dialog_badge.props(f"color={badge_color}")

        tags_str = format_hashtags(post)
        dialog_tags.set_text(tags_str)
        dialog_tags.set_visibility(bool(tags_str))
        dialog_body.set_text(post.body)

        dialog_footer.clear()
        with dialog_footer:
            if post.status != PostStatus.PUBLISHED:
                ui.button(
                    "Edit",
                    icon="edit",
                    on_click=lambda: _set_edit_mode(True, post),
                ).props("outline dense")
            ui.button(
                "Close",
                on_click=post_dialog.close,
            ).props("flat dense")

        post_dialog.open()

    async def _on_save_edit() -> None:
        post = active_post_ref["post"]
        if post is None:
            return

        updated_body = (body_editor.value or "").strip()
        if not updated_body:
            ui.notify("Post body cannot be empty.", type="warning")
            return

        post_origin = (
            PostOrigin.AI_EDIT if post.origin == PostOrigin.AI_DRAFT else post.origin
        )

        save_edit_btn.disable()
        cancel_edit_btn.disable()
        try:
            updated_post = post.model_copy(
                update={
                    "body": updated_body,
                    "hashtags": extract_hashtags(updated_body),
                    "origin": post_origin,
                    "updated_at": datetime.now(UTC),
                }
            )
            await run_blocking(lambda: ctx.post_store_manager.save_post(updated_post))
            ui.notify("Post updated.", type="positive")
            await post_dialog.close()
            await load_page()
        finally:
            save_edit_btn.enable()
            cancel_edit_btn.enable()

    cancel_edit_btn.on_click(lambda: _set_edit_mode(False))
    save_edit_btn.on_click(_on_save_edit)

    # --- Main Tab Layout ---
    with ui.column().classes("w-full max-w-4xl mx-auto gap-3"):
        with ui.card().classes("w-full q-pa-md gap-2"):
            with ui.row().classes("w-full items-center gap-3"):
                search_input = (
                    ui.input(
                        label="Search posts",
                        placeholder="Search by keywords or phrases...",
                    )
                    .props("clearable outlined dense")
                    .classes("col")
                )
                search_btn = ui.button("Search", icon="search", color="primary")

            with ui.row().classes("w-full items-center gap-3 flex-wrap"):
                origin_select = (
                    ui.select(
                        options=[o.value for o in PostOrigin],
                        multiple=True,
                        label="Origins",
                    )
                    .props("dense outlined use-chips")
                    .classes("min-w-48 col")
                )
                status_select = (
                    ui.select(
                        options=[s.value for s in PostStatus],
                        multiple=True,
                        label="Statuses",
                    )
                    .props("dense outlined use-chips")
                    .classes("min-w-48 col")
                )
                page_size_input = (
                    ui.number(
                        "Per page",
                        value=state["limit"],
                        min=1,
                        max=200,
                        step=1,
                    )
                    .props("dense outlined")
                    .classes("w-28")
                )

        with ui.row().classes("w-full justify-between items-center px-1"):
            page_label = ui.label(f"Page {state['page']}").classes(
                "text-subtitle2 text-grey-8"
            )
            with ui.row().classes("items-center gap-2"):
                prev_btn = ui.button("Previous", icon="chevron_left").props(
                    "flat dense"
                )
                next_btn = ui.button("Next", icon="chevron_right").props("flat dense")

        with ui.scroll_area().classes(
            "w-full h-[calc(100vh-310px)] min-h-72 border rounded q-pa-sm"
        ):
            list_container = ui.column().classes("w-full gap-2")

    def _render_post_card(post: Post) -> None:
        badge_color = "positive" if post.status == PostStatus.PUBLISHED else "warning"
        with (
            ui.card()
            .classes("w-full shrink-0 q-px-md q-py-sm cursor-pointer hover:bg-grey-1")
            .on("click", lambda _, p=post: _open_post_dialog(p))
        ):
            with ui.row().classes("w-full items-center justify-between gap-3 no-wrap"):
                with ui.row().classes("items-center gap-3 col min-w-0"):
                    ui.label(_format_created_at(post)).classes(
                        "text-caption text-grey-7 shrink-0 font-mono"
                    )
                    ui.label(post_short_preview(post)).classes(
                        "text-body2 text-weight-medium truncate"
                    )
                ui.badge(
                    f"{post.origin.value} · {post.status.value}",
                    color=badge_color,
                ).classes("shrink-0")

    def _render_posts(posts: list[Post]) -> None:
        list_container.clear()
        page_label.set_text(f"Page {state['page']} — {len(posts)} post(s)")
        prev_btn.set_enabled(state["page"] > 1)
        next_btn.set_enabled(len(posts) >= state["limit"])

        with list_container:
            if not posts:
                ui.label("No posts match the current search or filters.").classes(
                    "text-grey text-center w-full py-8"
                )
                return
            for post in posts:
                _render_post_card(post)

    async def load_page() -> None:
        state["limit"] = max(1, int(page_size_input.value or 20))
        search_term = (search_input.value or "").strip()

        query = PostGetQuery(
            origins=[PostOrigin(v) for v in (origin_select.value or [])],
            statuses=[PostStatus(v) for v in (status_select.value or [])],
            limit=state["limit"],
            page=state["page"],
        )
        posts = await run_blocking(lambda: ctx.post_storage.get_all(query))

        if search_term:
            needle = search_term.lower()
            posts = [
                p
                for p in posts
                if needle in p.body.lower()
                or any(needle in tag.lower() for tag in p.hashtags)
            ]

        _render_posts(posts)

    async def on_filter_or_search() -> None:
        state["page"] = 1
        await load_page()

    async def on_prev() -> None:
        if state["page"] > 1:
            state["page"] -= 1
            await load_page()

    async def on_next() -> None:
        state["page"] += 1
        await load_page()

    search_btn.on_click(on_filter_or_search)
    search_input.on("keydown.enter", lambda _: on_filter_or_search())
    origin_select.on_value_change(lambda _: on_filter_or_search())
    status_select.on_value_change(lambda _: on_filter_or_search())
    prev_btn.on_click(on_prev)
    next_btn.on_click(on_next)

    ui.timer(0.05, load_page, once=True)
