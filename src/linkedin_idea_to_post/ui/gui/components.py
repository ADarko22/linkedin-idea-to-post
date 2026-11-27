from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from datetime import UTC
from typing import Any

from nicegui import ui

from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus
from linkedin_idea_to_post.ui.gui import templates, theme
from linkedin_idea_to_post.ui.gui.helpers import format_hashtags, post_short_preview


def format_created_at(post: Post) -> str:
    return post.created_at.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC")


def status_badge_color(status: PostStatus) -> str:
    return "positive" if status == PostStatus.PUBLISHED else "warning"


def format_post_badge(origin: PostOrigin, status: PostStatus) -> str:
    return f"{origin.value} · {status.value}"


def post_badge(
    origin: PostOrigin, status: PostStatus, *, extra_classes: str = ""
) -> ui.badge:
    badge = ui.badge(
        format_post_badge(origin, status),
        color=status_badge_color(status),
    )
    if extra_classes:
        badge.classes(extra_classes)
    return badge


def post_summary_card(post: Post, on_select: Callable[[Post], Any]) -> ui.card:
    card = templates.interactive_card().on("click", lambda _, p=post: on_select(p))
    with card, theme.row_between("no-wrap"):
        with theme.row_gap_2("gap-3 col min-w-0"):
            theme.mono_caption(format_created_at(post), "shrink-0")
            theme.post_preview_label(post_short_preview(post))
        post_badge(post.origin, post.status, extra_classes="shrink-0")
    return card


def expandable_post_card(
    post: Post,
    *,
    selected: bool,
    on_toggle: Callable[[bool, ui.checkbox], Any] | None = None,
    badge_text: str | None = None,
    badge_color: str = "grey-7",
    card_classes: str = "w-full q-pa-xs overflow-x-hidden",
    trailing_controls: Callable[[], None] | None = None,
) -> tuple[ui.card, ui.checkbox]:
    card = ui.card().classes(card_classes)
    with card, ui.row().classes("w-full items-start gap-2 flex-nowrap"):
        checkbox = ui.checkbox(value=selected).classes("shrink-0 mt-1")
        if on_toggle is not None:
            checkbox.on_value_change(
                lambda e, cb=checkbox: on_toggle(bool(e.value), cb)
            )

        expansion = ui.expansion().classes("col min-w-[200px]")
        with expansion.add_slot("header"), theme.row_between("gap-2 py-1 min-w-0"):
            preview = theme.post_preview_label(
                post_short_preview(post), "whitespace-normal col min-w-0"
            )
            preview.bind_visibility_from(
                expansion, "value", backward=lambda expanded: not expanded
            )
            if badge_text:
                ui.badge(badge_text, color=badge_color).classes("shrink-0")

        if trailing_controls is not None:
            trailing_controls()

        with expansion, ui.column().classes("w-full q-pa-sm pt-1 gap-1.5"):
            ui.separator()
            tags = format_hashtags(post)
            if tags:
                theme.tags_label(tags)
            theme.post_body_label(post.body)

    return card, checkbox


def pagination_bar(
    initial_text: str,
    on_prev: Callable[..., Any],
    on_next: Callable[..., Any],
) -> tuple[ui.label, ui.button, ui.button]:
    with theme.row_between("px-1 shrink-0"):
        page_label = theme.section_title(
            initial_text, small=True, extra_classes="text-grey-8"
        )
        with theme.row_gap_2():
            prev_btn = theme.flat_button(
                "Previous", icon="chevron_left", on_click=on_prev
            )
            next_btn = theme.flat_button("Next", icon="chevron_right", on_click=on_next)
    return page_label, prev_btn, next_btn


async def run_with_disabled[T](
    buttons: Sequence[ui.button], fn: Callable[[], Awaitable[T]]
) -> T:
    for btn in buttons:
        btn.disable()
    try:
        return await fn()
    finally:
        for btn in buttons:
            btn.enable()
