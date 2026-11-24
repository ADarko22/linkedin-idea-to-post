# linkedin-idea-to-post

An AI-assisted drafting tool powered by **CrewAI** and **Google Gemini** that retrieves relevant past posts (combining
full-text search, semantic embeddings, rank fusion, and word-count proximity), builds a voice and knowledge context, and
generates LinkedIn posts tailored to your style and stance.

## Interfaces

- **CLI (`li2p`)**: See [CLI Documentation](src/linkedin_idea_to_post/ui/cli/README.md)
- **GUI (`li2p-gui`)**: See [GUI Documentation](src/linkedin_idea_to_post/ui/gui/README.md)

## How It Works

1. **Context Selection (`DraftContextService`)**: Embeds your idea, runs full-text and semantic retrieval over stored
   posts, fuses rankings, and selects voice examples (human-authored posts tuned by style/length) and knowledge
   references (contextual posts with explicit stances).
2. **Draft Generation (`DraftService` + CrewAI)**: Injects the core idea, tuned voice examples, and stance-annotated
   knowledge posts into a structured writer task to produce a LinkedIn-ready draft.
3. **Persistence & Import**: Stores and queries posts locally in SQLite and supports importing historical posts from
   CSV (`Shares.csv`).

## Requirements & Setup

- **Python**: `>=3.12,<3.14`
- **Package manager**: [`uv`](https://docs.astral.sh/uv/) (`brew install uv`)

Install as a tool from GitHub:

- With `uv`:
   ```bash
   uv tool install git+https://github.com/ADarko22/linkedin-idea-to-post.git
   ```

- With `pip` (inside a virtual environment):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install git+https://github.com/ADarko22/linkedin-idea-to-post.git
   ```
  
- Or run locally from a clone:
    ```bash
   uv sync
   ```

### Configuration

Configuration is loaded via
`AppConfig` ([config.py](https://www.google.com/search?q=src/linkedin_idea_to_post/config.py)) from:

* `LI2P_CONFIG` environment variable (if set)
* `./config.toml` (when present in the current directory)
* User app directory (`platformdirs.user_data_path("linkedin-idea-to-post", appauthor=False) / "config.toml"`)

Environment variables also override settings using nested delimiters (for example, `WRITER_LLM__API_KEY="..."`). By
default, SQLite storage and embedding models live under the user data directory (`APP_DIR`).

## Development Commands

| Task          | Tool     | Command                   |
|---------------|----------|---------------------------|
| Type checking | `mypy`   | `uv run mypy src`         |
| Linting       | `ruff`   | `uv run ruff check --fix` |
| Formatting    | `ruff`   | `uv run ruff format`      |
| Testing       | `pytest` | `uv run pytest`           |

Install pre-commit hooks:

```bash
uv run pre-commit install
```

## Dependencies

| Dependency                                                                                                                           | Usage                                            | Scope                   |
|--------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------|-------------------------|
| [Click](https://github.com/pallets/click)                                                                                            | CLI commands and options                         | `ui/cli/`               |
| [Rich](https://github.com/Textualize/rich)                                                                                           | Formatted terminal output                        | `ui/cli/`               |
| [NiceGUI](https://nicegui.io/)                                                                                                       | Browser-based GUI                                | `ui/gui/`               |
| [CrewAI](https://github.com/crewaiinc/crewai)                                                                                        | Writer agent and task orchestration              | `adapters/ai_workflow/` |
| [NumPy](https://numpy.org/)                                                                                                          | Vector math and embedding serialization          | `adapters/embedding/`   |
| [Sentence-Transformers](https://www.sbert.net/) & [PyTorch](https://pytorch.org/)                                                    | Dense semantic embeddings (`cpu`, `cuda`, `mps`) | `adapters/embedding/`   |
| [Pydantic](https://github.com/pydantic/pydantic) & [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) | Domain models, validation, and TOML/env settings | `domain/`, `config.py`  |
| [platformdirs](https://www.google.com/search?q=https://github.com/platformdirs/platformdirs)                                         | OS-standard user config and data directories     | `config.py`             |
