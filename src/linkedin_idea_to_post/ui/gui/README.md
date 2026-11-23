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

## Features & Tabs

* **Posts**: Browse, filter, paginate, inspect, and edit stored posts via a modal viewer/editor.
* **New Draft**: Enter an idea, search/inspect matching posts in an overlay viewer, curate **Voice** (style/length
  tuned)
  and **Knowledge** (stance-annotated) context items, and generate a draft.
* **Import Csv**: Import historical posts from CSV files into the local archive.
* **Config**: View active settings (with secret masking toggle), validate and edit TOML, and **Save & Apply** changes to
  reload `AppContext` live.