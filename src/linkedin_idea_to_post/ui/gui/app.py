from __future__ import annotations

import os

from nicegui import app, ui

from linkedin_idea_to_post.app_context import AppContext, build_app_context
from linkedin_idea_to_post.ui.gui.config_tab import build_config_tab
from linkedin_idea_to_post.ui.gui.draft_tab import build_draft_tab
from linkedin_idea_to_post.ui.gui.import_tab import build_import_tab
from linkedin_idea_to_post.ui.gui.posts_tab import build_posts_tab


def _build_ui(ctx: AppContext) -> None:
    ui.label("LinkedIn Idea to Post").classes("text-h5 q-mb-sm")

    with ui.tabs().classes("w-full") as tabs:
        posts_tab = ui.tab("Posts")
        draft_tab = ui.tab("New Draft")
        import_tab = ui.tab("Import CSV")
        config_tab = ui.tab("Config")

    with ui.tab_panels(tabs, value=posts_tab).classes("w-full q-mt-md"):
        with ui.tab_panel(posts_tab):
            build_posts_tab(ctx)

        with ui.tab_panel(draft_tab):
            build_draft_tab(ctx)

        with ui.tab_panel(import_tab):
            build_import_tab(ctx)

        with ui.tab_panel(config_tab):
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
        show=False,  # avoids opening a new browser tab on every code save
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
