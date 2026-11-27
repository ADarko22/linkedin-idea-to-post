from __future__ import annotations

from collections.abc import Callable
from typing import Any

from nicegui import ui

from linkedin_idea_to_post.app_context import AppContext
from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus
from linkedin_idea_to_post.ui.gui import components, templates, theme
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
            theme.empty_state_label("No posts match the current search or filters.")
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
                theme.outline_button(
                    "Edit",
                    icon="edit",
                    on_click=lambda: reader_modal.set_edit_mode(True, target),
                )
            theme.close_button(reader_modal.close)

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

        page_label.set_text(f"Page {state.page} — {len(filtered)} post(s)")
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

    with templates.narrow_page("h-full flex flex-col min-h-0 gap-2"):
        with templates.card_panel("gap-2 shrink-0 q-pa-sm"):
            with theme.row_gap_2("w-full gap-3"):
                search_input = theme.outlined_input(
                    "Search posts",
                    placeholder="Search by keywords or phrases...",
                    extra_classes="col",
                )
                search_btn = theme.primary_button("Search", icon="search")

            with theme.row_gap_2("w-full gap-3 flex-wrap"):
                origin_select = theme.outlined_select(
                    [o.value for o in PostOrigin],
                    label="Origins",
                    multiple=True,
                    use_chips=True,
                    extra_classes="min-w-48 col",
                )
                status_select = theme.outlined_select(
                    [s.value for s in PostStatus],
                    label="Statuses",
                    multiple=True,
                    use_chips=True,
                    extra_classes="min-w-48 col",
                )
                page_size_input = theme.outlined_number(
                    "Per page",
                    value=state.limit,
                    min=MIN_PAGE_SIZE,
                    max=MAX_PAGE_SIZE,
                    step=1,
                    extra_classes="w-28",
                )

        page_label, prev_btn, next_btn = components.pagination_bar(
            f"Page {state.page}", on_prev, on_next
        )

        with theme.scroll_box("flex-1", "min-h-0"):
            list_container = theme.stack()

    search_btn.on_click(on_filter_or_search)
    search_input.on("keydown.enter", lambda _: on_filter_or_search())
    origin_select.on_value_change(lambda _: on_filter_or_search())
    status_select.on_value_change(lambda _: on_filter_or_search())

    ui.timer(_INITIAL_LOAD_DELAY_SEC, load_page, once=True)
