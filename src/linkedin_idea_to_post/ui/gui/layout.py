from __future__ import annotations

from collections.abc import Callable, Generator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Literal

from nicegui import ui

from linkedin_idea_to_post.ui.gui import primitives, styles
from linkedin_idea_to_post.ui.gui.styles import LayoutClass, Props

CardSize = Literal["md", "sm", "fill", "compact", "interactive"]
CardAccent = Literal["manual", "suggested"]
ModalSize = Literal["md", "lg", "xl"]
SplitRatio = Literal["equal", "2:3"]

_CARD_CLASS_MAP: dict[CardSize, str] = {
    "md": LayoutClass.CARD_MD,
    "sm": LayoutClass.CARD_SM,
    "fill": LayoutClass.CARD_FILL,
    "compact": LayoutClass.CARD_COMPACT_ITEM,
    "interactive": LayoutClass.CARD_INTERACTIVE,
}
_ACCENT_CLASS_MAP: dict[CardAccent, str] = {
    "manual": "li2p-accent-manual",
    "suggested": "li2p-accent-suggested",
}


@dataclass(frozen=True)
class TabSpec:
    label: str
    icon: str
    build: Callable[[], None]


def app_shell(title: str, icon: str, tabs: Sequence[TabSpec]) -> None:
    ui.add_css(styles.GLOBAL_CSS)
    ui.colors(
        primary=styles.COLOR_PRIMARY,
        secondary=styles.COLOR_SECONDARY,
        accent=styles.COLOR_ACCENT,
    )
    dark = ui.dark_mode(value=False)

    with ui.column().classes(LayoutClass.APP_SHELL_COL):
        with ui.element("header").classes(LayoutClass.APP_HEADER):
            with ui.row().classes(LayoutClass.APP_HEADER_INNER):
                with primitives.row(full_width=False, shrink=True, gap="xs"):
                    ui.icon(icon, size="xs", color="primary")
                    ui.label(title).classes(LayoutClass.APP_TITLE)

                with primitives.row(full_width=False, shrink=True, gap="sm"):
                    with (
                        ui.tabs()
                        .classes(LayoutClass.APP_TAB_BAR)
                        .props(Props.TABS_HEADER) as tab_bar
                    ):
                        tab_widgets = [
                            ui.tab(spec.label, icon=spec.icon).props("inline-label")
                            for spec in tabs
                        ]

                    theme_btn = primitives.icon_button(
                        "dark_mode", tooltip="Toggle dark / light theme"
                    )

                    def _toggle_theme() -> None:
                        dark.toggle()
                        primitives.set_button_icon(
                            theme_btn, "light_mode" if dark.value else "dark_mode"
                        )

                    theme_btn.on_click(_toggle_theme)

        with ui.tab_panels(tab_bar, value=tab_widgets[0]).classes(
            LayoutClass.APP_TAB_PANELS
        ):
            for tab_widget, spec in zip(tab_widgets, tabs, strict=True):
                with ui.tab_panel(tab_widget).classes(LayoutClass.PANEL_FIXED):
                    spec.build()


def page_container() -> ui.column:
    return ui.column().classes(LayoutClass.PAGE_FLUID_FILL)


def split_workspace(*, ratio: SplitRatio = "equal") -> ui.element:
    cls = LayoutClass.SPLIT_EQUAL if ratio == "equal" else LayoutClass.SPLIT_2_3
    return ui.element("div").classes(cls)


def panel_card(
    *,
    size: CardSize = "md",
    accent: CardAccent | None = None,
) -> ui.card:
    parts = [_CARD_CLASS_MAP[size]]
    if accent is not None:
        parts.append(_ACCENT_CLASS_MAP[accent])
    return ui.card().classes(" ".join(parts))


@contextmanager
def titled_card_panel(
    title: str,
    *,
    level: int = 2,
) -> Generator[ui.card, None, None]:
    with panel_card(size="fill") as card:
        primitives.heading(title, level=level)
        yield card


def key_value_card(title: str, entries: Sequence[tuple[str, str]] | str) -> ui.card:
    with panel_card(size="sm") as card:
        ui.label(title).classes(LayoutClass.KV_TITLE)
        if isinstance(entries, str):
            primitives.text(entries, tone="muted", break_all=True)
        else:
            for key, val in entries:
                with ui.row().classes(LayoutClass.KV_ROW):
                    ui.label(key).classes(LayoutClass.KV_KEY)
                    ui.label(val).classes(LayoutClass.KV_VAL)
    return card


def warning_expansion(title: str = "Errors") -> tuple[ui.expansion, ui.column]:
    exp = ui.expansion(title, icon="warning").classes(LayoutClass.WARNING_EXPANSION)
    exp.props("dense")
    exp.set_visibility(False)
    with exp:
        inner = primitives.column(gap="xs")
    return exp, inner


def search_results_panel() -> tuple[ui.column, ui.label, ui.column]:
    panel = ui.column().classes(LayoutClass.SEARCH_PANEL)
    panel.set_visibility(False)
    with panel:
        info = primitives.text("", tone="muted")
        box = ui.column().classes(LayoutClass.SEARCH_BOX)
    return panel, info, box


@contextmanager
def modal_dialog(
    size: ModalSize = "lg",
    *,
    blur: str = "blur(2px)",
) -> Generator[tuple[ui.dialog, ui.card], None, None]:
    dialog = ui.dialog().props(f"backdrop-filter='{blur}'")
    with dialog, ui.card().classes(LayoutClass.MODAL_WIDTHS[size]) as card:
        yield dialog, card


def modal_header(
    title: str,
    on_close: Callable[..., Any],
    *,
    level: int = 1,
) -> ui.row:
    with primitives.row(justify="between") as row_widget:
        primitives.heading(title, level=level)
        primitives.icon_button("close", on_click=on_close)
    return row_widget


def status_banner() -> tuple[ui.row, ui.label]:
    banner = ui.row().classes(LayoutClass.BANNER_SUCCESS)
    banner.set_visibility(False)
    with banner:
        label = primitives.text("", tone="body")
        primitives.icon_button(
            "close",
            on_click=lambda: banner.set_visibility(False),
        )
    return banner, label
