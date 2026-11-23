# linkedin-idea-to-post - CLI (`li2p`)

Command-line interface for inspecting configuration, importing historical posts, browsing stored posts, and generating
LinkedIn post drafts.

## Requirements & Running

Requires Python `>=3.12,<3.14` and `uv` (or an installed `li2p` entry point).

```bash
# Installed via uv tool / pipx
li2p --help

# Or from a local repo checkout
uv run li2p --help
```

## Commands

| Command       | Description                                                                                      |
|---------------|--------------------------------------------------------------------------------------------------|
| `show-config` | Show the resolved config path and active application settings.                                   |
| `draft`       | Generate a LinkedIn draft from an input idea using retrieved voice/knowledge context and CrewAI. |
| `csv-import`  | Import historical posts from a LinkedIn export CSV (such as `Shares.csv`).                       |
| `list-posts`  | List posts stored in the local SQLite database.                                                  |

## Examples

```bash
li2p show-config
li2p csv-import path/to/Shares.csv
li2p list-posts
li2p draft "Why boring architectures beat over-engineered microservices" --commit
```
