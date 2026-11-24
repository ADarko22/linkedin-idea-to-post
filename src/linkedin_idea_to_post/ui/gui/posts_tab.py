from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from nicegui import ui

from linkedin_idea_to_post.app_context import AppContext
from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus
from linkedin_idea_to_post.domain.post_helpers import extract_hashtags
from linkedin_idea_to_post.domain.storage import PostGetQuery
from linkedin_idea_to_post.ui.gui import styles
from linkedin_idea_to_post.ui.gui.helpers import (
    format_hashtags,
    post_short_preview,
    run_blocking,
)


def _format_created_at(post: Post) -> str:
    return post.created_at.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC")


def _status_badge_color(status: PostStatus) -> str:
    return "positive" if status == PostStatus.PUBLISHED else "warning"


def _build_query(
    page: int,
    limit: int,
    origins: list[str] | None,
    statuses: list[str] | None,
) -> PostGetQuery:
    return PostGetQuery(
        origins=[PostOrigin(v) for v in (origins or [])],
        statuses=[PostStatus(v) for v in (statuses or [])],
        limit=limit,
        page=page,
    )


def _filter_posts(posts: list[Post], search_term: str) -> list[Post]:
    if not search_term:
        return posts
    needle = search_term.lower()
    return [
        p
        for p in posts
        if needle in p.body.lower() or any(needle in tag.lower() for tag in p.hashtags)
    ]


def _render_post_card(post: Post, on_select: Callable[[Post], Any]) -> None:
    card = styles.interactive_card().on("click", lambda _, p=post: on_select(p))
    with card, styles.row_between("no-wrap"):
        with styles.row_gap_2("gap-3 col min-w-0"):
            styles.mono_caption(_format_created_at(post), "shrink-0")
            styles.post_preview_label(post_short_preview(post))
        ui.badge(
            f"{post.origin.value} · {post.status.value}",
            color=_status_badge_color(post.status),
        ).classes("shrink-0")


def _render_posts(
    list_container: ui.column,
    posts: list[Post],
    on_select: Callable[[Post], Any],
) -> None:
    list_container.clear()
    with list_container:
        if not posts:
            styles.empty_state_label("No posts match the current search or filters.")
            return
        for post in posts:
            _render_post_card(post, on_select)


def build_posts_tab(ctx: AppContext) -> None:
    state: dict[str, int] = {
        "page": 1,
        "limit": ctx.config.storage.post_get_all_page_size,
    }
    active_post_ref: dict[str, Post | None] = {"post": None}

    post_dialog = ui.dialog().props("backdrop-filter='blur(2px)'")
    with post_dialog, styles.dialog_card():
        with styles.row_between("gap-2 flex-wrap"):
            with styles.row_gap_2():
                dialog_meta = styles.mono_caption("")
                dialog_badge = ui.badge("")
            styles.flat_button(
                icon="close",
                on_click=post_dialog.close,
                extra_props="round dense color=grey-8",
            )

        dialog_tags = styles.tags_label("")

        with styles.scroll_box("h-80", "overflow-x-hidden"):
            dialog_body = styles.post_body_label("")

        edit_container = ui.column().classes("w-full gap-2")
        edit_container.set_visibility(False)
        with edit_container:
            body_editor = styles.outlined_textarea(
                label="Edit post body", autogrow=True
            )
            with styles.row_gap_2("justify-end w-full"):
                cancel_edit_btn = styles.flat_button("Cancel")
                save_edit_btn = styles.primary_button("Save Changes", icon="save")

        dialog_footer = ui.row().classes("w-full justify-end gap-2")

    def _set_edit_mode(editing: bool, post: Post | None = None) -> None:
        edit_container.set_visibility(editing)
        dialog_body.set_visibility(not editing)
        if editing and post is not None:
            body_editor.set_value(post.body)

    def _open_post_dialog(post: Post) -> None:
        active_post_ref["post"] = post
        _set_edit_mode(False)
        dialog_meta.set_text(_format_created_at(post))
        dialog_badge.set_text(f"{post.origin.value} · {post.status.value}")
        dialog_badge.props(f"color={_status_badge_color(post.status)}")

        tags_str = format_hashtags(post)
        dialog_tags.set_text(tags_str)
        dialog_tags.set_visibility(bool(tags_str))
        dialog_body.set_text(post.body)

        dialog_footer.clear()
        with dialog_footer:
            if post.status != PostStatus.PUBLISHED:
                styles.outline_button(
                    "Edit",
                    icon="edit",
                    on_click=lambda: _set_edit_mode(True, post),
                )
            styles.close_button(post_dialog.close)

        post_dialog.open()

    async def load_page() -> None:
        state["limit"] = max(1, int(page_size_input.value or 20))
        search_term = (search_input.value or "").strip()
        query = _build_query(
            state["page"],
            state["limit"],
            origin_select.value,
            status_select.value,
        )
        posts = await run_blocking(lambda: ctx.post_storage.get_all(query))
        filtered = _filter_posts(posts, search_term)

        page_label.set_text(f"Page {state['page']} — {len(filtered)} post(s)")
        prev_btn.set_enabled(state["page"] > 1)
        next_btn.set_enabled(len(filtered) >= state["limit"])
        _render_posts(list_container, filtered, _open_post_dialog)

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
            post_dialog.close()
            await load_page()
        finally:
            save_edit_btn.enable()
            cancel_edit_btn.enable()

    cancel_edit_btn.on_click(lambda: _set_edit_mode(False))
    save_edit_btn.on_click(_on_save_edit)

    with styles.narrow_column("h-full flex flex-col min-h-0 gap-2"):
        with styles.card_panel("gap-2 shrink-0 q-pa-sm"):
            with styles.row_gap_2("w-full gap-3"):
                search_input = styles.outlined_input(
                    "Search posts", placeholder="Search by keywords or phrases..."
                ).classes("col")
                search_btn = styles.primary_button("Search", icon="search")

            with styles.row_gap_2("w-full gap-3 flex-wrap"):
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

        with styles.row_between("px-1 shrink-0"):
            page_label = styles.section_title(
                f"Page {state['page']}", small=True
            ).classes("text-grey-8")
            with styles.row_gap_2():
                prev_btn = styles.flat_button("Previous", icon="chevron_left")
                next_btn = styles.flat_button("Next", icon="chevron_right")

        with styles.scroll_box("flex-1", "min-h-0"):
            list_container = ui.column().classes("w-full gap-2")

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
