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
    accent: str | None = None,
    trailing_controls: Callable[[], None] | None = None,
) -> tuple[ui.card, ui.checkbox]:
    card = (
        templates.accent_card(accent, "q-pa-xs overflow-x-hidden")
        if accent is not None
        else ui.card().classes(card_classes)
    )
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


class PostReaderModal:
    """Reusable modal dialog for inspecting (and optionally editing) a Post."""

    def __init__(
        self,
        *,
        title: str | None = None,
        width_classes: str = "max-w-3xl",
        blur: str = "blur(2px)",
        body_height: str = "h-80",
        editable: bool = False,
        on_save: Callable[[str], Awaitable[None]] | None = None,
    ) -> None:
        self._editable = editable
        with templates.modal_dialog(width_classes, blur=blur) as (dialog, _):
            self.dialog = dialog
            if title is not None:
                templates.modal_header(title, dialog.close)
                self._meta = None
                self._badge = None
            else:
                with theme.row_between("gap-2 flex-wrap"):
                    with theme.row_gap_2():
                        self._meta = theme.mono_caption("")
                        self._badge = ui.badge("")
                    theme.icon_button("close", on_click=dialog.close)

            self._tags = theme.tags_label("")
            with theme.scroll_box(body_height, "overflow-x-hidden"):
                self._body = theme.post_body_label("")

            self._edit_box: ui.column | None = None
            self._editor: ui.textarea | None = None
            if editable:
                edit_box = theme.stack()
                edit_box.set_visibility(False)
                with edit_box:
                    editor = theme.outlined_textarea(
                        label="Edit post body", autogrow=True
                    )
                    with theme.footer_row():
                        cancel_btn = theme.flat_button(
                            "Cancel", on_click=lambda: self.set_edit_mode(False)
                        )

                        async def _handle_save() -> None:
                            if on_save is not None:
                                await run_with_disabled(
                                    [save_btn, cancel_btn],
                                    lambda: on_save(editor.value or ""),
                                )

                        save_btn = theme.primary_button(
                            "Save Changes", icon="save", on_click=_handle_save
                        )
                self._edit_box = edit_box
                self._editor = editor

            self.footer = theme.footer_row()

    def set_edit_mode(self, editing: bool, post: Post | None = None) -> None:
        if self._edit_box is not None:
            self._edit_box.set_visibility(editing)
        self._body.set_visibility(not editing)
        if editing and post is not None and self._editor is not None:
            self._editor.set_value(post.body)

    def open(
        self,
        post: Post,
        *,
        render_footer: Callable[[Post], None] | None = None,
    ) -> None:
        self.set_edit_mode(False)
        if self._meta is not None:
            self._meta.set_text(format_created_at(post))
        if self._badge is not None:
            self._badge.set_text(format_post_badge(post.origin, post.status))
            self._badge.props(f"color={status_badge_color(post.status)}")

        tags_str = format_hashtags(post)
        self._tags.set_text(tags_str)
        self._tags.set_visibility(bool(tags_str))
        self._body.set_text(post.body)

        self.footer.clear()
        if render_footer is not None:
            with self.footer:
                render_footer(post)
        self.dialog.open()

    def close(self) -> None:
        self.dialog.close()


def search_result_card(
    post: Post,
    *,
    on_preview: Callable[[Post], Any],
    on_add_voice: Callable[[Post], Any],
    on_add_knowledge: Callable[[Post], Any],
) -> ui.card:
    card = templates.compact_card("bg-white overflow-visible")
    with card, theme.row_between("gap-2 flex-wrap overflow-visible"):
        preview = theme.post_preview_label(
            post_short_preview(post),
            "text-grey-10 cursor-pointer hover:text-primary whitespace-normal overflow-visible flex-1 min-w-[240px]",
        )
        preview.on("click", lambda _, p=post: on_preview(p))
        with theme.row_gap_2("gap-1.5 shrink-0"):
            theme.action_button(
                "Voice",
                icon="add_circle",
                color="primary",
                outline=True,
                size="sm",
                on_click=lambda _, p=post: on_add_voice(p),
            )
            theme.action_button(
                "Knowledge",
                icon="add_circle",
                color="teal",
                outline=True,
                size="sm",
                on_click=lambda _, p=post: on_add_knowledge(p),
            )
    return card
