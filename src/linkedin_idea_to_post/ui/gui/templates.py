from __future__ import annotations

from collections.abc import Callable, Generator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

from nicegui import ui

from linkedin_idea_to_post.ui.gui import theme

_PANEL_FLEX = (
    "w-full h-full q-px-md q-pt-xs q-pb-sm flex flex-col min-h-0 overflow-hidden"
)
_PANEL_SCROLL = "w-full h-full q-px-md q-pt-xs q-pb-sm overflow-y-auto"

_ACCENT_STYLES: dict[str, str] = {
    "manual": "border-l-4 border-teal-6 bg-teal-1",
    "suggested": "border-l-4 border-grey-5",
    "neutral": "bg-grey-1 border",
}


@dataclass(frozen=True)
class TabSpec:
    label: str
    icon: str
    build: Callable[[], None]
    scrollable: bool = True


def app_shell(title: str, icon: str, tabs: Sequence[TabSpec]) -> None:
    ui.colors(
        primary=theme.COLOR_PRIMARY,
        secondary=theme.COLOR_SECONDARY,
        accent=theme.COLOR_ACCENT,
    )
    ui.query("body").classes("overflow-hidden")

    with ui.header(elevated=True).classes(
        "bg-white text-grey-10 border-b q-pa-none min-h-0"
    ):
        with theme.row_between("w-full max-w-6xl mx-auto px-4 h-12 no-wrap"):
            with theme.row_gap_2("shrink-0"):
                ui.icon(icon, size="sm", color="primary")
                ui.label(title).classes(
                    "text-h6 text-weight-bold leading-none whitespace-nowrap"
                )

            with (
                ui.tabs()
                .classes("h-12")
                .props(
                    "dense align=right no-caps active-color=primary indicator-color=primary"
                ) as tab_bar
            ):
                tab_widgets = [ui.tab(spec.label, icon=spec.icon) for spec in tabs]

    with (
        ui.column().classes("w-full h-screen flex flex-col overflow-hidden gap-0"),
        ui.tab_panels(tab_bar, value=tab_widgets[0]).classes(
            "w-full flex-1 min-h-0 bg-transparent q-pa-none overflow-hidden"
        ),
    ):
        for tab_widget, spec in zip(tab_widgets, tabs, strict=True):
            panel_cls = _PANEL_SCROLL if spec.scrollable else _PANEL_FLEX
            with ui.tab_panel(tab_widget).classes(panel_cls):
                spec.build()


def narrow_page(extra_classes: str = "") -> ui.column:
    return ui.column().classes(f"{theme.CONTAINER_NARROW} {extra_classes}".strip())


def wide_page(extra_classes: str = "") -> ui.column:
    return ui.column().classes(f"{theme.CONTAINER_WIDE} {extra_classes}".strip())


def card_panel(extra_classes: str = "") -> ui.card:
    return ui.card().classes(f"{theme.CARD_PANEL} {extra_classes}".strip())


def compact_card(extra_classes: str = "") -> ui.card:
    return ui.card().classes(f"w-full shrink-0 q-pa-sm {extra_classes}".strip())


def accent_card(accent: str = "neutral", extra_classes: str = "") -> ui.card:
    accent_cls = _ACCENT_STYLES.get(accent, _ACCENT_STYLES["neutral"])
    return ui.card().classes(
        f"w-full shrink-0 q-pa-sm {accent_cls} {extra_classes}".strip()
    )


def key_value_card(title: str, entries: Sequence[tuple[str, str]] | str) -> ui.card:
    with accent_card("neutral") as card:
        ui.label(title).classes(
            "text-caption text-weight-bold text-uppercase text-primary q-mb-xs"
        )
        if isinstance(entries, str):
            ui.label(entries).classes("text-caption break-all")
        else:
            for key, val in entries:
                with ui.row().classes(
                    "w-full items-baseline justify-between gap-2 py-0.5 border-b border-grey-3"
                ):
                    ui.label(key).classes("text-caption text-grey-8 font-mono shrink-0")
                    ui.label(val).classes(
                        "text-caption text-weight-medium text-right break-all"
                    )
    return card


def warning_expansion(title: str = "Errors") -> tuple[ui.expansion, ui.column]:
    expansion = ui.expansion(title, icon="warning").classes(
        "w-full bg-orange-1 rounded border border-orange-4"
    )
    expansion.set_visibility(False)
    with expansion:
        inner = ui.column().classes("w-full gap-1 q-pa-sm")
    return expansion, inner


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
