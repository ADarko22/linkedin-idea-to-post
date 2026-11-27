# linkedin-idea-to-post - GUI (`li2p-gui`)

Browser-based [NiceGUI](https://nicegui.io/) interface for drafting posts, inspecting and managing stored posts,
importing CSV archives, and editing application configuration.

## Requirements & Running

Requires Python `>=3.12,<3.14` and `uv` (or an installed `li2p-gui` entry point).

```bash
# Installed via uv tool / pipx
li2p-gui

# Or from a local repo checkout
uv run li2p-gui
```

## Architecture

The `ui/gui` package separates styling, layout templates, reusable components, pure-Python state, and thin NiceGUI views:

* `theme.py` — Design tokens (colors, Quasar prop presets, container/typography classes) and styled UI primitives.
* `templates.py` — Structural layout templates (`narrow_page`, `wide_page`, `card_panel`, `split_pane`, `titled_card_panel`, `modal_dialog`, `status_banner`).
* `components.py` — Reusable data-driven widgets (`post_badge`, `post_summary_card`, `expandable_post_card`, `pagination_bar`, `run_with_disabled`) and formatting helpers.
* `*_state.py` (`posts_state.py`, `draft_state.py`, `import_state.py`, `config_state.py`) — NiceGUI-free state and transition logic covered by unit tests under `tests/unit/ui/gui/`.
* `*_tab.py` & `app.py` — Declarative NiceGUI tab views and the top-level shell.

## Features & Tabs

* **Posts**: Browse, filter, paginate, inspect, and edit stored posts via a modal viewer/editor.
* **New Draft**: Enter an idea, search/inspect matching posts in an overlay viewer, curate **Voice** (style/length tuned) and **Knowledge** (stance-annotated) context items, generate a draft, and navigate the last `N` drafts (with their saved context restored on selection; configured via `[drafting].draft_history_limit`, default `10`).
* **Import CSV**: Import historical posts from CSV files into the local archive.
* **Config**: View active settings (with secret masking toggle), validate and edit TOML, and **Save & Apply** changes to reload `AppContext` live.
