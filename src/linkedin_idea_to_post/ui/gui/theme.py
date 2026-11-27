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


def footer_row(extra_classes: str = "") -> ui.row:
    return ui.row().classes(f"w-full justify-end gap-2 {extra_classes}".strip())


def stack(gap: str = "gap-2", extra_classes: str = "") -> ui.column:
    return ui.column().classes(f"w-full {gap} {extra_classes}".strip())


def scroll_column(extra_classes: str = "") -> ui.column:
    return ui.column().classes(
        f"w-full flex-1 min-h-0 overflow-y-auto overflow-x-hidden gap-2 pr-1 {extra_classes}".strip()
    )


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


def error_label(text: str) -> ui.label:
    return ui.label(text).classes(ERROR_CAPTION)


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


def outlined_select(
    options: list[str] | dict[str, str],
    *,
    label: str = "",
    value: Any = None,
    multiple: bool = False,
    use_chips: bool = False,
    extra_classes: str = "",
) -> ui.select:
    props = [PROPS_OUTLINED_DENSE]
    if use_chips:
        props.append("use-chips")
    sel = ui.select(
        options=options, value=value, multiple=multiple, label=label or None
    )
    sel.props(" ".join(props))
    if extra_classes:
        sel.classes(extra_classes)
    return sel


def outlined_number(
    label: str,
    *,
    value: float | int,
    min: float | int | None = None,
    max: float | int | None = None,
    step: float | int | None = None,
    extra_classes: str = "w-32",
) -> ui.number:
    return (
        ui.number(label, value=value, min=min, max=max, step=step)
        .props(PROPS_OUTLINED_DENSE)
        .classes(extra_classes)
    )


def icon_button(
    icon: str,
    *,
    on_click: Callable[..., Any] | None = None,
    color: str = "grey-8",
    size: str = "sm",
    tooltip: str | None = None,
    extra_classes: str = "",
) -> ui.button:
    btn = flat_button(
        icon=icon,
        on_click=on_click,
        extra_props=f"round size={size} color={color}",
    )
    if tooltip:
        btn.tooltip(tooltip)
    if extra_classes:
        btn.classes(extra_classes)
    return btn


def action_button(
    label: str,
    *,
    icon: str | None = None,
    color: str | None = None,
    on_click: Callable[..., Any] | None = None,
    unelevated: bool = False,
    outline: bool = False,
    dense: bool = True,
    size: str | None = None,
) -> ui.button:
    props: list[str] = []
    if dense:
        props.append("dense")
    if outline:
        props.append("outline")
    if unelevated:
        props.append("unelevated")
    if size:
        props.append(f"size={size}")
    btn = ui.button(label, icon=icon, color=color, on_click=on_click)
    if props:
        btn.props(" ".join(props))
    return btn


def badge(
    text: str = "",
    *,
    color: str = "grey-7",
    clickable: bool = False,
) -> ui.badge:
    b = ui.badge(text, color=color)
    if clickable:
        b.classes("cursor-pointer")
    return b


def set_icon(btn: ui.button, icon: str) -> None:
    btn.props(f"icon={icon}")


_TOML_EDITOR_CLASSES = (
    "w-full flex-1 h-[calc(100vh-285px)] min-h-72 font-mono text-caption "
    "[&_.q-field\\_\\_inner]:h-full [&_.q-field\\_\\_control]:h-full "
    "[&_.q-field\\_\\_control-container]:h-full [&_textarea]:h-full [&_textarea]:overflow-y-auto"
)


def toml_editor(value: str = "") -> ui.textarea:
    return outlined_textarea(value=value, extra_classes=_TOML_EDITOR_CLASSES)


def csv_upload(label: str = "Choose Shares.csv") -> ui.upload:
    return ui.upload(auto_upload=True, max_files=1).props(
        f"accept=.csv flat bordered label='{label}'"
    )
