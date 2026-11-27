from __future__ import annotations

from collections.abc import Callable
from typing import Any

from nicegui import ui

# Color palette
COLOR_PRIMARY = "#0A66C2"
COLOR_SECONDARY = "#2E7D32"
COLOR_ACCENT = "#0288D1"

# Quasar prop presets
PROPS_FLAT_DENSE = "flat dense"
PROPS_OUTLINED_DENSE = "outlined dense"
PROPS_OUTLINE_DENSE = "outline dense"
PROPS_UNELEVATED_DENSE = "dense unelevated"

# Layout & typography class presets
CONTAINER_NARROW = "w-full max-w-4xl mx-auto gap-3"
CONTAINER_WIDE = "w-full max-w-5xl mx-auto h-[calc(100vh-110px)] gap-3 overflow-hidden"
CARD_PANEL = "w-full q-pa-md gap-3"
ROW_BETWEEN = "w-full items-center justify-between gap-3"
ROW_GAP_2 = "items-center gap-2"
CAPTION_MUTED = "text-caption text-grey-7"
ERROR_CAPTION = "text-negative text-caption"


def row_between(extra_classes: str = "") -> ui.row:
    return ui.row().classes(f"{ROW_BETWEEN} {extra_classes}".strip())


def row_gap_2(extra_classes: str = "") -> ui.row:
    return ui.row().classes(f"{ROW_GAP_2} {extra_classes}".strip())


def section_title(
    text: str, *, small: bool = False, extra_classes: str = ""
) -> ui.label:
    size = "text-subtitle2" if small else "text-subtitle1"
    return ui.label(text).classes(f"{size} text-weight-bold {extra_classes}".strip())


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
    props = f"{PROPS_FLAT_DENSE} {extra_props}".strip()
    return ui.button(label, icon=icon, on_click=on_click).props(props)


def primary_button(
    label: str,
    *,
    icon: str | None = None,
    on_click: Callable[..., Any] | None = None,
    unelevated: bool = False,
) -> ui.button:
    btn = ui.button(label, icon=icon, color="primary", on_click=on_click)
    return btn.props(PROPS_UNELEVATED_DENSE) if unelevated else btn


def outline_button(
    label: str,
    *,
    icon: str | None = None,
    on_click: Callable[..., Any] | None = None,
    dense: bool = True,
) -> ui.button:
    props = PROPS_OUTLINE_DENSE if dense else "outline"
    return ui.button(label, icon=icon, on_click=on_click).props(props)


def positive_button(
    label: str,
    *,
    icon: str | None = None,
    on_click: Callable[..., Any] | None = None,
    unelevated: bool = False,
) -> ui.button:
    btn = ui.button(label, icon=icon, color="positive", on_click=on_click)
    return btn.props(PROPS_UNELEVATED_DENSE) if unelevated else btn


def close_button(on_click: Callable[..., Any]) -> ui.button:
    return flat_button("Close", on_click=on_click)


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
        .props(f"{PROPS_OUTLINED_DENSE}{clear_prop}")
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
