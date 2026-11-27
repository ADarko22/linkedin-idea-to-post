from __future__ import annotations

from collections.abc import Callable
from typing import Any

from nicegui import ui

from linkedin_idea_to_post.app_context import AppContext
from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus
from linkedin_idea_to_post.ui.gui import components, templates, theme
from linkedin_idea_to_post.ui.gui.helpers import format_hashtags, run_blocking
from linkedin_idea_to_post.ui.gui.posts_state import PostsState


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

    with templates.modal_dialog() as (post_dialog, _):
        with theme.row_between("gap-2 flex-wrap"):
            with theme.row_gap_2():
                dialog_meta = theme.mono_caption("")
                dialog_badge = ui.badge("")
            theme.flat_button(
                icon="close",
                on_click=post_dialog.close,
                extra_props="round color=grey-8",
            )

        dialog_tags = theme.tags_label("")

        with theme.scroll_box("h-80", "overflow-x-hidden"):
            dialog_body = theme.post_body_label("")

        edit_container = ui.column().classes("w-full gap-2")
        edit_container.set_visibility(False)
        with edit_container:
            body_editor = theme.outlined_textarea(label="Edit post body", autogrow=True)
            with theme.row_gap_2("justify-end w-full"):
                cancel_edit_btn = theme.flat_button("Cancel")
                save_edit_btn = theme.primary_button("Save Changes", icon="save")

        dialog_footer = ui.row().classes("w-full justify-end gap-2")

    def set_edit_mode(editing: bool, post: Post | None = None) -> None:
        edit_container.set_visibility(editing)
        dialog_body.set_visibility(not editing)
        if editing and post is not None:
            body_editor.set_value(post.body)

    def open_post_dialog(post: Post) -> None:
        state.active_post = post
        set_edit_mode(False)
        dialog_meta.set_text(components.format_created_at(post))
        dialog_badge.set_text(components.format_post_badge(post.origin, post.status))
        dialog_badge.props(f"color={components.status_badge_color(post.status)}")

        tags_str = format_hashtags(post)
        dialog_tags.set_text(tags_str)
        dialog_tags.set_visibility(bool(tags_str))
        dialog_body.set_text(post.body)

        dialog_footer.clear()
        with dialog_footer:
            if post.status != PostStatus.PUBLISHED:
                theme.outline_button(
                    "Edit",
                    icon="edit",
                    on_click=lambda: set_edit_mode(True, post),
                )
            theme.close_button(post_dialog.close)

        post_dialog.open()

    async def load_page() -> None:
        state.set_limit(page_size_input.value)
        state.search_term = search_input.value or ""
        state.origins = list(origin_select.value or [])
        state.statuses = list(status_select.value or [])

        query = state.build_query()
        posts = await run_blocking(lambda: ctx.post_storage.get_all(query))
        filtered = state.filter_posts(posts)

        page_label.set_text(f"Page {state.page} — {len(filtered)} post(s)")
        prev_btn.set_enabled(state.can_go_prev())
        next_btn.set_enabled(state.can_go_next(len(filtered)))
        _render_posts(list_container, filtered, open_post_dialog)

    async def on_save_edit() -> None:
        try:
            updated_post = state.build_updated_post(body_editor.value or "")
        except ValueError as exc:
            ui.notify(str(exc), type="warning")
            return
        if updated_post is None:
            return

        async def _save() -> None:
            await run_blocking(lambda: ctx.post_store_manager.save_post(updated_post))
            ui.notify("Post updated.", type="positive")
            post_dialog.close()
            await load_page()

        await components.run_with_disabled([save_edit_btn, cancel_edit_btn], _save)

    async def on_filter_or_search() -> None:
        state.reset_page()
        await load_page()

    async def on_prev() -> None:
        if state.prev_page():
            await load_page()

    async def on_next() -> None:
        state.next_page()
        await load_page()

    cancel_edit_btn.on_click(lambda: set_edit_mode(False))
    save_edit_btn.on_click(on_save_edit)

    with templates.narrow_page("h-full flex flex-col min-h-0 gap-2"):
        with templates.card_panel("gap-2 shrink-0 q-pa-sm"):
            with theme.row_gap_2("w-full gap-3"):
                search_input = theme.outlined_input(
                    "Search posts", placeholder="Search by keywords or phrases..."
                ).classes("col")
                search_btn = theme.primary_button("Search", icon="search")

            with theme.row_gap_2("w-full gap-3 flex-wrap"):
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
                        value=state.limit,
                        min=1,
                        max=200,
                        step=1,
                    )
                    .props(theme.PROPS_OUTLINED_DENSE)
                    .classes("w-28")
                )

        page_label, prev_btn, next_btn = components.pagination_bar(
            f"Page {state.page}", on_prev, on_next
        )

        with theme.scroll_box("flex-1", "min-h-0"):
            list_container = ui.column().classes("w-full gap-2")

    search_btn.on_click(on_filter_or_search)
    search_input.on("keydown.enter", lambda _: on_filter_or_search())
    origin_select.on_value_change(lambda _: on_filter_or_search())
    status_select.on_value_change(lambda _: on_filter_or_search())

    ui.timer(0.05, load_page, once=True)
