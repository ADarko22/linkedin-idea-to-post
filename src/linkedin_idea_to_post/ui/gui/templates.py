from __future__ import annotations

from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any

from nicegui import ui

from linkedin_idea_to_post.ui.gui import theme


def narrow_page(extra_classes: str = "") -> ui.column:
    return ui.column().classes(f"{theme.CONTAINER_NARROW} {extra_classes}".strip())


def wide_page(extra_classes: str = "") -> ui.column:
    return ui.column().classes(f"{theme.CONTAINER_WIDE} {extra_classes}".strip())


def card_panel(extra_classes: str = "") -> ui.card:
    return ui.card().classes(f"{theme.CARD_PANEL} {extra_classes}".strip())


def interactive_card(extra_classes: str = "") -> ui.card:
    return ui.card().classes(
        f"w-full shrink-0 q-px-md q-py-sm cursor-pointer hover:bg-grey-1 {extra_classes}".strip()
    )


def split_pane(columns: int = 2, extra_classes: str = "") -> ui.grid:
    return ui.grid(columns=columns).classes(
        f"w-full flex-1 min-h-0 gap-3 {extra_classes}".strip()
    )


@contextmanager
def titled_card_panel(
    title: str,
    *,
    small_title: bool = True,
    card_classes: str = "w-full h-full q-pa-md flex flex-col min-h-0 overflow-hidden",
) -> Generator[ui.card, None, None]:
    with ui.card().classes(card_classes) as card:
        theme.section_title(title, small=small_title, extra_classes="shrink-0 q-mb-xs")
        yield card


@contextmanager
def modal_dialog(
    width_classes: str = "max-w-3xl",
    *,
    blur: str = "blur(2px)",
) -> Generator[tuple[ui.dialog, ui.card], None, None]:
    dialog = ui.dialog().props(f"backdrop-filter='{blur}'")
    with (
        dialog,
        ui.card().classes(
            f"w-full {width_classes} q-pa-md gap-3 overflow-x-hidden"
        ) as card,
    ):
        yield dialog, card


def modal_header(
    title: str,
    on_close: Callable[..., Any],
    *,
    small: bool = False,
) -> ui.row:
    with theme.row_between() as row:
        theme.section_title(title, small=small)
        theme.flat_button(
            icon="close", on_click=on_close, extra_props="round color=grey-8"
        )
    return row


def status_banner() -> tuple[ui.row, ui.label]:
    banner = ui.row().classes(
        "w-full items-center justify-between bg-green-1 text-green-10 "
        "q-pa-sm rounded border border-green-4"
    )
    banner.set_visibility(False)
    with banner:
        label = ui.label("").classes("text-body2 text-weight-medium")
        theme.flat_button(
            icon="close",
            on_click=lambda: banner.set_visibility(False),
            extra_props="round size=sm",
        )
    return banner, label
