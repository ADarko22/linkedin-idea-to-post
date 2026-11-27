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

The `ui/gui` package follows a 4-layer UI architecture plus NiceGUI-free pure-Python state modules so layout and view modules contain zero inline `.classes()` or `.props()` styling:

* `styles.py` — Pure-Python design tokens (CSS variables for light and dark themes, `GLOBAL_CSS`, `Props`, `LayoutClass`). Zero `nicegui` imports.
* `primitives.py` — Semantic styled NiceGUI widget factories (`row`, `column`, `scroll_box`, `heading`, `text`, `pill`, `button`, `icon_button`, `badge`, `text_input`, `textarea`, `select_input`, `number_input`, `csv_upload`, `checkbox`, `expansion`).
* `layout.py` — Structural containers and page shells (`app_shell` with fixed `100vh` viewport and light/dark theme toggle, `TabSpec`, `page_container`, `split_workspace`, `panel_card`, `titled_card_panel`, `key_value_card`, `modal_dialog`, `modal_header`, `status_banner`, `warning_expansion`, `search_results_panel`).
* `components.py` — Reusable data-driven widgets (`PostReaderModal`, `post_pill`, `post_summary_card`, `expandable_post_card`, `search_result_card`, `pagination_bar`, `run_with_disabled`) and formatting helpers.
* `*_state.py` (`posts_state.py`, `draft_context_state.py`, `draft_history_state.py`, `import_state.py`, `config_state.py`) — NiceGUI-free state and transition logic covered by unit tests under `tests/unit/ui/gui/`.
* `*_tab.py` & `draft_context_dialog.py` & `app.py` — Thin declarative NiceGUI views and the top-level shell.

## Features & Tabs

* **Posts**: Reactive filtering (Search, Origin, Status, Rows), concise single-line post rows inside a fixed-height scrollable panel, bottom icon pagination, and post inspection/editing via `PostReaderModal`.
* **New Draft**: Fixed-height 2-column workspace (`Idea` and `Draft`). Enter an idea, search/inspect matching posts and curate **Voice** (style/length tuned) and **Knowledge** (stance-annotated) context items via `DraftContextDialog`, generate a draft, and navigate the last `N` drafts (with their saved context restored on selection; configured via `[drafting].draft_history_limit`, default `10`).
* **Import CSV**: 2-column workspace for importing historical posts from CSV files into the local archive and viewing import summaries/warnings.
* **Config**: 2-column workspace for viewing active settings (with secret masking toggle), validating and editing TOML, and **Save & Apply** changes to reload `AppContext` live.
* **Light / Dark Theme**: Toggle between light and dark palettes from the header theme button.
