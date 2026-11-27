from __future__ import annotations

from collections.abc import Callable
from typing import Any

from nicegui import ui

from linkedin_idea_to_post.app_context import AppContext
from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus
from linkedin_idea_to_post.ui.gui import components, layout, primitives
from linkedin_idea_to_post.ui.gui.helpers import run_blocking
from linkedin_idea_to_post.ui.gui.posts_state import (
    MAX_PAGE_SIZE,
    MIN_PAGE_SIZE,
    PostsState,
)

_INITIAL_LOAD_DELAY_SEC = 0.05


def _render_posts(
    list_container: ui.column,
    posts: list[Post],
    on_select: Callable[[Post], Any],
) -> None:
    list_container.clear()
    with list_container:
        if not posts:
            primitives.text(
                "No posts match the current search or filters.", tone="empty"
            )
            return
        for post in posts:
            components.post_summary_card(post, on_select)


def build_posts_tab(ctx: AppContext) -> None:
    state = PostsState(limit=ctx.config.storage.post_get_all_page_size)

    async def on_save_edit(raw_body: str) -> None:
        try:
            updated_post = state.build_updated_post(raw_body)
        except ValueError as exc:
            ui.notify(str(exc), type="warning")
            return
        if updated_post is None:
            return
        await run_blocking(lambda: ctx.post_store_manager.save_post(updated_post))
        ui.notify("Post updated.", type="positive")
        reader_modal.close()
        await load_page()

    reader_modal = components.PostReaderModal(editable=True, on_save=on_save_edit)

    def open_post_dialog(post: Post) -> None:
        state.active_post = post

        def render_footer(target: Post) -> None:
            if target.status != PostStatus.PUBLISHED:
                primitives.button(
                    "Edit",
                    icon="edit",
                    variant="outline",
                    on_click=lambda: reader_modal.set_edit_mode(True, target),
                )
            primitives.button("Close", variant="flat", on_click=reader_modal.close)

        reader_modal.open(post, render_footer=render_footer)

    async def load_page() -> None:
        state.set_limit(page_size_input.value)
        state.search_term = search_input.value or ""
        state.origins = list(origin_select.value or [])
        state.statuses = list(status_select.value or [])

        posts = await run_blocking(
            lambda: ctx.post_storage.get_all(state.build_query())
        )
        filtered = state.filter_posts(posts)

        count_label.set_text(f"{len(filtered)} post(s)")
        page_label.set_text(f"Page {state.page}")
        prev_btn.set_enabled(state.can_go_prev())
        next_btn.set_enabled(state.can_go_next(len(filtered)))
        _render_posts(list_container, filtered, open_post_dialog)

    async def on_filter_or_search() -> None:
        state.reset_page()
        await load_page()

    async def on_prev() -> None:
        if state.prev_page():
            await load_page()

    async def on_next() -> None:
        state.next_page()
        await load_page()

    with layout.page_container(), layout.panel_card(size="fill"):
        with primitives.row(wrap=True, gap="sm", shrink=True):
            search_input = primitives.text_input(
                "Search",
                placeholder="Keywords or #tags...",
                grow=True,
            )
            origin_select = primitives.select_input(
                [o.value for o in PostOrigin],
                label="Origin",
                multiple=True,
                use_chips=True,
                width="col",
            )
            status_select = primitives.select_input(
                [s.value for s in PostStatus],
                label="Status",
                multiple=True,
                use_chips=True,
                width="col",
            )
            page_size_input = primitives.number_input(
                "Rows",
                value=state.limit,
                min_val=MIN_PAGE_SIZE,
                max_val=MAX_PAGE_SIZE,
                step=1,
                width="xs",
            )

        ui.separator()
        list_container = primitives.column(scroll=True)
        ui.separator()

        with primitives.row(justify="between", shrink=True):
            count_label = primitives.text("0 post(s)", tone="muted")
            page_label, prev_btn, next_btn = components.pagination_bar(
                f"Page {state.page}", on_prev, on_next
            )

    search_input.on_value_change(lambda _: on_filter_or_search())
    origin_select.on_value_change(lambda _: on_filter_or_search())
    status_select.on_value_change(lambda _: on_filter_or_search())
    page_size_input.on_value_change(lambda _: on_filter_or_search())

    ui.timer(_INITIAL_LOAD_DELAY_SEC, load_page, once=True)
