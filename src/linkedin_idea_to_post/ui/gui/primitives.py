from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

from nicegui import ui

from linkedin_idea_to_post.ui.gui.styles import LayoutClass, Props

Justify = Literal["start", "between", "end"]
Align = Literal["center", "start", "baseline"]
Gap = Literal["xs", "sm", "md", "lg"]
TextTone = Literal[
    "body",
    "muted",
    "mono",
    "tags",
    "error",
    "empty",
    "prose",
    "preview",
    "preview_wrap",
]
ButtonVariant = Literal["primary", "secondary", "positive", "outline", "flat", "danger"]
PillTone = Literal["neutral", "published", "draft"]

_JUSTIFY_MAP: dict[Justify, str] = {
    "start": "justify-start",
    "between": "justify-between",
    "end": "justify-end",
}
_ALIGN_MAP: dict[Align, str] = {
    "center": "items-center",
    "start": "items-start",
    "baseline": "items-baseline",
}
_TONE_MAP: dict[TextTone, str] = {
    "body": LayoutClass.TEXT_BODY,
    "muted": LayoutClass.TEXT_MUTED,
    "mono": LayoutClass.TEXT_MONO,
    "tags": LayoutClass.TEXT_TAGS,
    "error": LayoutClass.TEXT_ERROR,
    "empty": LayoutClass.TEXT_EMPTY,
    "prose": LayoutClass.TEXT_PROSE,
    "preview": LayoutClass.TEXT_PREVIEW,
    "preview_wrap": LayoutClass.TEXT_PREVIEW_WRAP,
}
_PILL_MAP: dict[PillTone, str] = {
    "neutral": "li2p-pill",
    "published": "li2p-pill li2p-pill-published",
    "draft": "li2p-pill li2p-pill-draft",
}


def row(
    *,
    justify: Justify = "start",
    align: Align = "center",
    gap: Gap = "sm",
    wrap: bool = False,
    full_width: bool = True,
    no_wrap: bool = False,
    shrink: bool = False,
) -> ui.row:
    parts = [
        _ALIGN_MAP[align],
        _JUSTIFY_MAP[justify],
        LayoutClass.GAP_CLASSES[gap],
    ]
    if full_width:
        parts.append("w-full")
    if wrap:
        parts.append("flex-wrap")
    if no_wrap:
        parts.append("flex-nowrap")
    if shrink:
        parts.append("shrink-0")
    return ui.row().classes(" ".join(parts))


def column(
    *,
    gap: Gap = "sm",
    full_width: bool = True,
    grow: bool = False,
    scroll: bool = False,
) -> ui.column:
    if scroll:
        return ui.column().classes(LayoutClass.SCROLL_COLUMN)
    parts = [LayoutClass.GAP_CLASSES[gap]]
    if full_width:
        parts.append("w-full")
    if grow:
        parts.append("col min-w-0")
    return ui.column().classes(" ".join(parts))


def scroll_box(*, height: str = "lg", fill: bool = False) -> ui.scroll_area:
    key = "fill" if fill else height
    return ui.scroll_area().classes(
        LayoutClass.SCROLL_HEIGHTS.get(key, LayoutClass.SCROLL_HEIGHTS["lg"])
    )


def heading(value: str, *, level: int = 1) -> ui.label:
    cls = LayoutClass.TEXT_HEADING_1 if level == 1 else LayoutClass.TEXT_HEADING_2
    return ui.label(value).classes(cls)


def text(
    value: str = "",
    *,
    tone: TextTone = "body",
    grow: bool = False,
    shrink: bool = False,
    clickable: bool = False,
    break_all: bool = False,
) -> ui.label:
    parts = [_TONE_MAP[tone]]
    if grow:
        parts.append("flex-1 min-w-0")
    if shrink:
        parts.append("shrink-0")
    if clickable:
        parts.append("cursor-pointer hover:text-primary")
    if break_all:
        parts.append("break-all")
    return ui.label(value).classes(" ".join(parts))


def pill(value: str = "", *, tone: PillTone = "neutral") -> ui.label:
    return ui.label(value).classes(_PILL_MAP[tone])


def button(
    label: str = "",
    *,
    icon: str | None = None,
    variant: ButtonVariant = "primary",
    color: str | None = None,
    size: str | None = "sm",
    dense: bool = True,
    unelevated: bool = True,
    on_click: Callable[..., Any] | None = None,
    tooltip: str | None = None,
) -> ui.button:
    color_map: dict[ButtonVariant, str | None] = {
        "primary": "primary",
        "secondary": "secondary",
        "positive": "positive",
        "outline": None,
        "flat": None,
        "danger": "negative",
    }
    resolved_color = color if color is not None else color_map[variant]
    props: list[str] = ["no-caps"]
    if dense:
        props.append("dense")
    if variant == "flat":
        props.append("flat")
    elif variant == "outline":
        props.append("outline")
    if unelevated and variant not in ("flat", "outline"):
        props.append("unelevated")
    if size:
        props.append(f"size={size}")

    btn = ui.button(label, icon=icon, color=resolved_color, on_click=on_click)
    btn.props(" ".join(props))
    if tooltip:
        btn.tooltip(tooltip)
    return btn


def icon_button(
    icon: str,
    *,
    color: str = "grey-7",
    size: str = "sm",
    on_click: Callable[..., Any] | None = None,
    tooltip: str | None = None,
    shrink: bool = False,
) -> ui.button:
    btn = ui.button("", icon=icon, on_click=on_click).props(
        f"{Props.FLAT_DENSE} round size={size} color={color}"
    )
    if tooltip:
        btn.tooltip(tooltip)
    if shrink:
        btn.classes("shrink-0")
    return btn


def set_button_icon(btn: ui.button, icon: str) -> None:
    btn.props(f"icon={icon}")


def badge(
    value: str = "",
    *,
    color: str = "grey-7",
    clickable: bool = False,
    shrink: bool = False,
) -> ui.badge:
    b = ui.badge(value, color=color)
    parts: list[str] = []
    if clickable:
        parts.append("cursor-pointer")
    if shrink:
        parts.append("shrink-0")
    if parts:
        b.classes(" ".join(parts))
    return b


def set_badge_color(badge_widget: ui.badge, color: str) -> None:
    badge_widget.props(f"color={color}")


def text_input(
    label: str,
    *,
    placeholder: str = "",
    clearable: bool = True,
    grow: bool = False,
) -> ui.input:
    clear_prop = " clearable" if clearable else ""
    cls = "col min-w-0" if grow else "w-full"
    return (
        ui.input(label=label, placeholder=placeholder)
        .props(f"{Props.OUTLINED_DENSE}{clear_prop}")
        .classes(cls)
    )


def textarea(
    label: str = "",
    *,
    placeholder: str = "",
    value: str = "",
    rows: int | None = None,
    autogrow: bool = False,
    toml: bool = False,
    fill: bool = False,
) -> ui.textarea:
    props = ["outlined", "dense"]
    if rows is not None:
        props.append(f"rows={rows}")
    if autogrow:
        props.append("autogrow")
    if toml:
        cls = LayoutClass.TOML_EDITOR
    elif fill:
        cls = LayoutClass.FILL_TEXTAREA
    else:
        cls = "w-full"
    return (
        ui.textarea(label=label or None, placeholder=placeholder, value=value)
        .props(" ".join(props))
        .classes(cls)
    )


def select_input(
    options: list[str] | dict[str, str],
    *,
    label: str = "",
    value: Any = None,
    multiple: bool = False,
    use_chips: bool = False,
    width: str = "auto",
) -> ui.select:
    props = [Props.OUTLINED_DENSE]
    if use_chips:
        props.append("use-chips")
    sel = ui.select(
        options=options, value=value, multiple=multiple, label=label or None
    )
    sel.props(" ".join(props))
    cls = LayoutClass.SELECT_WIDTHS.get(width, "")
    if cls:
        sel.classes(cls)
    return sel


def number_input(
    label: str,
    *,
    value: float | int,
    min_val: float | int | None = None,
    max_val: float | int | None = None,
    step: float | int | None = None,
    width: str = "sm",
) -> ui.number:
    cls = LayoutClass.NUMBER_WIDTHS.get(width, LayoutClass.NUMBER_WIDTHS["sm"])
    return (
        ui.number(label, value=value, min=min_val, max=max_val, step=step)
        .props(Props.OUTLINED_DENSE)
        .classes(cls)
    )


def csv_upload(label: str = "Choose Shares.csv") -> ui.upload:
    return ui.upload(auto_upload=True, max_files=1).props(
        f"{Props.CSV_UPLOAD} label='{label}'"
    )


def checkbox(*, value: bool = False, compact: bool = False) -> ui.checkbox:
    cb = ui.checkbox(value=value).props("dense")
    if compact:
        cb.classes(LayoutClass.CHECKBOX_COMPACT)
    return cb


def expansion(*, grow: bool = False) -> ui.expansion:
    exp = ui.expansion().props("dense")
    if grow:
        exp.classes(LayoutClass.EXPANSION_GROW)
    return exp
