from __future__ import annotations

import os

from nicegui import app, ui

from linkedin_idea_to_post.app_context import AppContext, build_app_context
from linkedin_idea_to_post.ui.gui import styles
from linkedin_idea_to_post.ui.gui.config_tab import build_config_tab
from linkedin_idea_to_post.ui.gui.draft_tab import build_draft_tab
from linkedin_idea_to_post.ui.gui.import_tab import build_import_tab
from linkedin_idea_to_post.ui.gui.posts_tab import build_posts_tab

_PANEL_FLEX = (
    "w-full h-full q-px-md q-pt-xs q-pb-sm flex flex-col min-h-0 overflow-hidden"
)
_PANEL_SCROLL = "w-full h-full q-px-md q-pt-xs q-pb-sm overflow-y-auto"


def _build_ui(ctx: AppContext) -> None:
    ui.colors(primary="#0A66C2", secondary="#2E7D32", accent="#0288D1")
    ui.query("body").classes("overflow-hidden")

    with ui.header(elevated=True).classes(
        "bg-white text-grey-10 border-b q-pa-none min-h-0"
    ):
        with styles.row_between("w-full max-w-6xl mx-auto px-4 h-12 no-wrap"):
            with styles.row_gap_2("shrink-0"):
                ui.icon("edit_square", size="sm", color="primary")
                ui.label("LinkedIn Idea to Post").classes(
                    "text-h6 text-weight-bold leading-none whitespace-nowrap"
                )

            with (
                ui.tabs()
                .classes("h-12")
                .props(
                    "dense align=right no-caps active-color=primary indicator-color=primary"
                ) as tabs
            ):
                posts_tab = ui.tab("Posts", icon="article")
                draft_tab = ui.tab("New Draft", icon="auto_awesome")
                import_tab = ui.tab("Import CSV", icon="upload_file")
                config_tab = ui.tab("Config", icon="settings")

    with (
        ui.column().classes("w-full h-screen flex flex-col overflow-hidden gap-0"),
        ui.tab_panels(tabs, value=posts_tab).classes(
            "w-full flex-1 min-h-0 bg-transparent q-pa-none overflow-hidden"
        ),
    ):
        with ui.tab_panel(posts_tab).classes(_PANEL_FLEX):
            build_posts_tab(ctx)

        with ui.tab_panel(draft_tab).classes(_PANEL_SCROLL):
            build_draft_tab(ctx)

        with ui.tab_panel(import_tab).classes(_PANEL_SCROLL):
            build_import_tab(ctx)

        with ui.tab_panel(config_tab).classes(_PANEL_FLEX):
            build_config_tab(ctx)


def main() -> None:
    ctx = build_app_context()

    @ui.page("/")
    def index() -> None:
        _build_ui(ctx)

    app.on_shutdown(ctx.close)
    reload = os.getenv("LI2P_DEV_RELOAD", "0") == "1"
    ui.run(
        title="LinkedIn Idea to Post",
        port=8080,
        reload=reload,
        uvicorn_reload_dirs="src",
        show=False,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
