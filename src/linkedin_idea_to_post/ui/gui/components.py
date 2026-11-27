from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from datetime import UTC
from typing import Any, Literal

from nicegui import ui

from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus
from linkedin_idea_to_post.ui.gui import layout, primitives
from linkedin_idea_to_post.ui.gui.helpers import format_hashtags, post_short_preview


def format_created_at(post: Post) -> str:
    return post.created_at.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC")


def format_short_date(post: Post) -> str:
    return post.created_at.astimezone(UTC).strftime("%Y-%m-%d")


def status_badge_color(status: PostStatus) -> str:
    return "positive" if status == PostStatus.PUBLISHED else "warning"


def format_post_badge(origin: PostOrigin, status: PostStatus) -> str:
    return f"{origin.value} · {status.value}"


def post_pill(post: Post) -> ui.label:
    tone: primitives.PillTone = (
        "published" if post.status == PostStatus.PUBLISHED else "draft"
    )
    origin_short = "HUMAN" if post.origin == PostOrigin.HUMAN else "AI"
    status_short = "PUB" if post.status == PostStatus.PUBLISHED else "DRAFT"
    return primitives.pill(f"{origin_short} · {status_short}", tone=tone)


def post_summary_card(post: Post, on_select: Callable[[Post], Any]) -> ui.card:
    card = layout.panel_card(size="interactive").on(
        "click", lambda _, p=post: on_select(p)
    )
    with card, primitives.row(justify="between", no_wrap=True, gap="md"):
        primitives.text(post_short_preview(post), tone="preview", grow=True)
        with primitives.row(full_width=False, shrink=True, gap="sm", no_wrap=True):
            primitives.text(format_short_date(post), tone="mono", shrink=True)
            post_pill(post)
    return card


def expandable_post_card(
    post: Post,
    *,
    selected: bool,
    on_toggle: Callable[[bool, ui.checkbox], Any] | None = None,
    badge_text: str | None = None,
    badge_color: str = "grey-7",
    accent: Literal["manual", "suggested"] | None = None,
    trailing_controls: Callable[[], None] | None = None,
) -> tuple[ui.card, ui.checkbox]:
    card = layout.panel_card(size="compact", accent=accent)
    with card, primitives.row(align="start", no_wrap=True):
        cb = primitives.checkbox(value=selected, compact=True)
        if on_toggle is not None:
            cb.on_value_change(lambda e, box=cb: on_toggle(bool(e.value), box))

        exp = primitives.expansion(grow=True)
        with exp.add_slot("header"), primitives.row(justify="between"):
            preview = primitives.text(
                post_short_preview(post), tone="preview_wrap", grow=True
            )
            preview.bind_visibility_from(
                exp, "value", backward=lambda expanded: not expanded
            )
            if badge_text:
                primitives.pill(badge_text)

        if trailing_controls is not None:
            trailing_controls()

        with exp, primitives.column(gap="xs"):
            ui.separator()
            tags = format_hashtags(post)
            if tags:
                primitives.text(tags, tone="tags")
            primitives.text(post.body, tone="prose")

    return card, cb


def pagination_bar(
    initial_text: str,
    on_prev: Callable[..., Any],
    on_next: Callable[..., Any],
) -> tuple[ui.label, ui.button, ui.button]:
    with primitives.row(full_width=False, shrink=True, gap="xs", no_wrap=True):
        prev_btn = primitives.icon_button(
            "chevron_left", tooltip="Previous page", on_click=on_prev
        )
        page_label = primitives.text(initial_text, tone="mono", shrink=True)
        next_btn = primitives.icon_button(
            "chevron_right", tooltip="Next page", on_click=on_next
        )
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


_SIZE_MAP: dict[str, layout.ModalSize] = {
    "max-w-2xl": "md",
    "max-w-3xl": "lg",
    "max-w-5xl": "xl",
    "md": "md",
    "lg": "lg",
    "xl": "xl",
}
_HEIGHT_MAP: dict[str, str] = {
    "h-72": "sm",
    "h-80": "md",
    "sm": "sm",
    "md": "md",
    "lg": "lg",
    "xl": "xl",
}


class PostReaderModal:
    """Reusable modal dialog for inspecting (and optionally editing) a Post."""

    def __init__(
        self,
        *,
        title: str | None = None,
        size: layout.ModalSize = "lg",
        width_classes: str | None = None,
        blur: str = "blur(2px)",
        body_height: str = "md",
        editable: bool = False,
        on_save: Callable[[str], Awaitable[None]] | None = None,
    ) -> None:
        resolved_size = _SIZE_MAP.get(width_classes or size, "lg")
        resolved_height = _HEIGHT_MAP.get(body_height, "md")
        with layout.modal_dialog(resolved_size, blur=blur) as (dialog, _):
            self.dialog = dialog
            if title is not None:
                layout.modal_header(title, dialog.close)
                self._meta = None
                self._badge = None
            else:
                with primitives.row(justify="between", wrap=True):
                    with primitives.row(full_width=False):
                        self._meta = primitives.text("", tone="mono")
                        self._badge = primitives.badge("")
                    primitives.icon_button("close", on_click=dialog.close)

            self._tags = primitives.text("", tone="tags")
            with primitives.scroll_box(height=resolved_height):
                self._body = primitives.text("", tone="prose")

            self._edit_box: ui.column | None = None
            self._editor: ui.textarea | None = None
            if editable:
                edit_box = primitives.column()
                edit_box.set_visibility(False)
                with edit_box:
                    editor = primitives.textarea(label="Edit post body", autogrow=True)
                    with primitives.row(justify="end"):
                        cancel_btn = primitives.button(
                            "Cancel",
                            variant="flat",
                            on_click=lambda: self.set_edit_mode(False),
                        )

                        async def _handle_save() -> None:
                            if on_save is not None:
                                await run_with_disabled(
                                    [save_btn, cancel_btn],
                                    lambda: on_save(editor.value or ""),
                                )

                        save_btn = primitives.button(
                            "Save Changes",
                            icon="save",
                            variant="primary",
                            on_click=_handle_save,
                        )
                self._edit_box = edit_box
                self._editor = editor

            self.footer = primitives.row(justify="end")

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
            primitives.set_badge_color(self._badge, status_badge_color(post.status))

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
    card = layout.panel_card(size="compact")
    with card, primitives.row(justify="between", wrap=True):
        preview = primitives.text(
            post_short_preview(post),
            tone="preview_wrap",
            grow=True,
            clickable=True,
        )
        preview.on("click", lambda _, p=post: on_preview(p))
        with primitives.row(full_width=False, gap="xs", shrink=True):
            primitives.button(
                "Voice",
                icon="add_circle",
                variant="outline",
                color="primary",
                size="xs",
                on_click=lambda _, p=post: on_add_voice(p),
            )
            primitives.button(
                "Knowledge",
                icon="add_circle",
                variant="outline",
                color="teal",
                size="xs",
                on_click=lambda _, p=post: on_add_knowledge(p),
            )
    return card
