from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass

from nicegui import app, ui

from linkedin_idea_to_post.app_context import AppContext, build_app_context
from linkedin_idea_to_post.ui.gui import theme
from linkedin_idea_to_post.ui.gui.config_tab import build_config_tab
from linkedin_idea_to_post.ui.gui.draft_tab import build_draft_tab
from linkedin_idea_to_post.ui.gui.import_tab import build_import_tab
from linkedin_idea_to_post.ui.gui.posts_tab import build_posts_tab

APP_TITLE = "LinkedIn Idea to Post"
DEFAULT_PORT = 8080

_PANEL_FLEX = (
    "w-full h-full q-px-md q-pt-xs q-pb-sm flex flex-col min-h-0 overflow-hidden"
)
_PANEL_SCROLL = "w-full h-full q-px-md q-pt-xs q-pb-sm overflow-y-auto"


@dataclass(frozen=True)
class _TabSpec:
    label: str
    icon: str
    panel_classes: str
    build: Callable[[AppContext], None]


_TABS: tuple[_TabSpec, ...] = (
    _TabSpec("Posts", "article", _PANEL_FLEX, build_posts_tab),
    _TabSpec("New Draft", "auto_awesome", _PANEL_SCROLL, build_draft_tab),
    _TabSpec("Import CSV", "upload_file", _PANEL_SCROLL, build_import_tab),
    _TabSpec("Config", "settings", _PANEL_FLEX, build_config_tab),
)


def _build_ui(ctx: AppContext) -> None:
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
                ui.icon("edit_square", size="sm", color="primary")
                ui.label(APP_TITLE).classes(
                    "text-h6 text-weight-bold leading-none whitespace-nowrap"
                )

            with (
                ui.tabs()
                .classes("h-12")
                .props(
                    "dense align=right no-caps active-color=primary indicator-color=primary"
                ) as tabs
            ):
                tab_widgets = [ui.tab(spec.label, icon=spec.icon) for spec in _TABS]

    with (
        ui.column().classes("w-full h-screen flex flex-col overflow-hidden gap-0"),
        ui.tab_panels(tabs, value=tab_widgets[0]).classes(
            "w-full flex-1 min-h-0 bg-transparent q-pa-none overflow-hidden"
        ),
    ):
        for tab_widget, spec in zip(tab_widgets, _TABS, strict=True):
            with ui.tab_panel(tab_widget).classes(spec.panel_classes):
                spec.build(ctx)


def main() -> None:
    ctx = build_app_context()

    @ui.page("/")
    def index() -> None:
        _build_ui(ctx)

    app.on_shutdown(ctx.close)
    reload = os.getenv("LI2P_DEV_RELOAD", "0") == "1"
    ui.run(
        title=APP_TITLE,
        port=DEFAULT_PORT,
        reload=reload,
        uvicorn_reload_dirs="src",
        show=False,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
