from __future__ import annotations

from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any

from nicegui import ui

FLAT_DENSE = "flat dense"
OUTLINED_DENSE = "outlined dense"
CONTAINER_NARROW = "w-full max-w-4xl mx-auto gap-3"
CONTAINER_WIDE = "w-full max-w-5xl mx-auto h-[calc(100vh-110px)] gap-3 overflow-hidden"
CARD_PANEL = "w-full q-pa-md gap-3"
ROW_BETWEEN = "w-full items-center justify-between gap-3"
ROW_GAP_2 = "items-center gap-2"
CAPTION_MUTED = "text-caption text-grey-7"
ERROR_CAPTION = "text-negative text-caption"


def narrow_column(extra_classes: str = "") -> ui.column:
    return ui.column().classes(f"{CONTAINER_NARROW} {extra_classes}".strip())


def wide_column(extra_classes: str = "") -> ui.column:
    return ui.column().classes(f"{CONTAINER_WIDE} {extra_classes}".strip())


def card_panel(extra_classes: str = "") -> ui.card:
    return ui.card().classes(f"{CARD_PANEL} {extra_classes}".strip())


def interactive_card(extra_classes: str = "") -> ui.card:
    return ui.card().classes(
        f"w-full shrink-0 q-px-md q-py-sm cursor-pointer hover:bg-grey-1 {extra_classes}".strip()
    )


def dialog_card(extra_classes: str = "") -> ui.card:
    return ui.card().classes(
        f"w-full max-w-3xl q-pa-md gap-3 overflow-x-hidden {extra_classes}".strip()
    )


@contextmanager
def modal_card(
    width_classes: str = "max-w-3xl",
    *,
    blur: str = "blur(2px)",
) -> Generator[ui.card, None, None]:
    dialog = ui.dialog().props(f"backdrop-filter='{blur}'")
    with (
        dialog,
        ui.card().classes(
            f"w-full {width_classes} q-pa-md gap-3 overflow-x-hidden"
        ) as card,
    ):
        yield card


def row_between(extra_classes: str = "") -> ui.row:
    return ui.row().classes(f"{ROW_BETWEEN} {extra_classes}".strip())


def row_gap_2(extra_classes: str = "") -> ui.row:
    return ui.row().classes(f"{ROW_GAP_2} {extra_classes}".strip())


def modal_header(
    title: str,
    on_close: Callable[..., Any],
    *,
    small: bool = False,
) -> ui.row:
    with row_between() as row:
        section_title(title, small=small)
        flat_button(icon="close", on_click=on_close, extra_props="round")
    return row


def section_title(text: str, *, small: bool = False) -> ui.label:
    size = "text-subtitle2" if small else "text-subtitle1"
    return ui.label(text).classes(f"{size} text-weight-bold")


def muted_caption(text: str, extra_classes: str = "") -> ui.label:
    return ui.label(text).classes(f"{CAPTION_MUTED} {extra_classes}".strip())


def mono_caption(text: str, extra_classes: str = "") -> ui.label:
    return ui.label(text).classes(f"{CAPTION_MUTED} font-mono {extra_classes}".strip())


def tags_label(text: str, extra_classes: str = "") -> ui.label:
    return ui.label(text).classes(
        f"text-caption text-primary whitespace-normal break-words {extra_classes}".strip()
    )


def post_preview_label(text: str, extra_classes: str = "") -> ui.label:
    return ui.label(text).classes(
        f"text-body2 text-weight-medium truncate {extra_classes}".strip()
    )


def post_body_label(text: str, extra_classes: str = "") -> ui.label:
    return ui.label(text).classes(
        f"text-body2 whitespace-pre-line break-words leading-relaxed {extra_classes}".strip()
    )


def empty_state_label(text: str) -> ui.label:
    return ui.label(text).classes("text-grey text-center w-full py-8")


def scroll_box(
    height_classes: str = "h-[calc(100vh-300px)]", extra_classes: str = ""
) -> ui.scroll_area:
    return ui.scroll_area().classes(
        f"w-full {height_classes} min-h-72 border rounded q-pa-sm {extra_classes}".strip()
    )


def flat_button(
    label: str = "",
    *,
    icon: str | None = None,
    on_click: Callable[..., Any] | None = None,
    extra_props: str = "",
) -> ui.button:
    props = f"{FLAT_DENSE} {extra_props}".strip()
    return ui.button(label, icon=icon, on_click=on_click).props(props)


def primary_button(
    label: str,
    *,
    icon: str | None = None,
    on_click: Callable[..., Any] | None = None,
) -> ui.button:
    return ui.button(label, icon=icon, color="primary", on_click=on_click)


def outline_button(
    label: str,
    *,
    icon: str | None = None,
    on_click: Callable[..., Any] | None = None,
    dense: bool = True,
) -> ui.button:
    props = "outline dense" if dense else "outline"
    return ui.button(label, icon=icon, on_click=on_click).props(props)


def positive_button(
    label: str,
    *,
    icon: str | None = None,
    on_click: Callable[..., Any] | None = None,
    unelevated: bool = False,
) -> ui.button:
    btn = ui.button(label, icon=icon, color="positive", on_click=on_click)
    return btn.props("dense unelevated") if unelevated else btn


def close_button(on_click: Callable[..., Any]) -> ui.button:
    return flat_button("Close", on_click=on_click, extra_props="dense")


def outlined_input(
    label: str,
    *,
    placeholder: str = "",
    clearable: bool = True,
    extra_classes: str = "w-full",
) -> ui.input:
    clear_prop = " clearable" if clearable else ""
    return (
        ui.input(label=label, placeholder=placeholder)
        .props(f"{OUTLINED_DENSE}{clear_prop}")
        .classes(extra_classes)
    )


def outlined_textarea(
    label: str = "",
    *,
    placeholder: str = "",
    value: str = "",
    rows: int | None = None,
    autogrow: bool = False,
    extra_classes: str = "w-full",
    extra_props: str = "",
) -> ui.textarea:
    props = ["outlined", extra_props]
    if rows is not None:
        props.append(f"rows={rows}")
    if autogrow:
        props.append("autogrow")
    return (
        ui.textarea(label=label or None, placeholder=placeholder, value=value)
        .props(" ".join(p for p in props if p))
        .classes(extra_classes)
    )
