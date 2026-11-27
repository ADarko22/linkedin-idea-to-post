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

The `ui/gui` package separates styling, layout templates, reusable components, pure-Python state, and thin NiceGUI views so tab modules contain zero inline `.classes()` or `.props()` styling:

* `theme.py` — Design tokens (colors, Quasar prop presets, container/typography classes) and styled UI primitives (`outlined_input`, `outlined_textarea`, `outlined_select`, `outlined_number`, `action_button`, `icon_button`, `toml_editor`, `csv_upload`, etc.).
* `templates.py` — Structural layout templates (`app_shell`, `TabSpec`, `narrow_page`, `wide_page`, `card_panel`, `compact_card`, `accent_card`, `key_value_card`, `split_pane`, `titled_card_panel`, `modal_dialog`, `status_banner`, `warning_expansion`, `search_results_panel`).
* `components.py` — Reusable data-driven widgets (`PostReaderModal`, `post_badge`, `post_summary_card`, `expandable_post_card`, `search_result_card`, `pagination_bar`, `run_with_disabled`) and formatting helpers.
* `*_state.py` (`posts_state.py`, `draft_state.py`, `import_state.py`, `config_state.py`) — NiceGUI-free state and transition logic covered by unit tests under `tests/unit/ui/gui/`.
* `*_tab.py` & `draft_context_dialog.py` & `app.py` — Declarative NiceGUI views and the top-level shell.

## Features & Tabs

* **Posts**: Browse, filter, paginate, inspect, and edit stored posts via `PostReaderModal`.
* **New Draft**: Enter an idea, search/inspect matching posts and curate **Voice** (style/length tuned) and **Knowledge** (stance-annotated) context items via `DraftContextDialog`, generate a draft, and navigate the last `N` drafts (with their saved context restored on selection; configured via `[drafting].draft_history_limit`, default `10`).
* **Import CSV**: Import historical posts from CSV files into the local archive.
* **Config**: View active settings (with secret masking toggle), validate and edit TOML, and **Save & Apply** changes to reload `AppContext` live.
