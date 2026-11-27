from __future__ import annotations

import os

from nicegui import app, ui

from linkedin_idea_to_post.app_context import AppContext, build_app_context
from linkedin_idea_to_post.ui.gui.config_tab import build_config_tab
from linkedin_idea_to_post.ui.gui.draft_tab import build_draft_tab
from linkedin_idea_to_post.ui.gui.import_tab import build_import_tab
from linkedin_idea_to_post.ui.gui.posts_tab import build_posts_tab
from linkedin_idea_to_post.ui.gui.templates import TabSpec, app_shell

APP_TITLE = "LinkedIn Idea to Post"
APP_ICON = "edit_square"
DEFAULT_PORT = 8080


def _build_ui(ctx: AppContext) -> None:
    app_shell(
        APP_TITLE,
        APP_ICON,
        tabs=(
            TabSpec("Posts", "article", lambda: build_posts_tab(ctx), scrollable=False),
            TabSpec(
                "New Draft",
                "auto_awesome",
                lambda: build_draft_tab(ctx),
                scrollable=True,
            ),
            TabSpec(
                "Import CSV",
                "upload_file",
                lambda: build_import_tab(ctx),
                scrollable=True,
            ),
            TabSpec(
                "Config", "settings", lambda: build_config_tab(ctx), scrollable=False
            ),
        ),
    )


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
