# linkedin-idea-to-post

An AI-assisted drafting tool powered by **CrewAI** and **Google Gemini** that retrieves relevant past posts (combining
full-text search, semantic embeddings, rank fusion, and word-count proximity), builds a voice and knowledge context, and
generates LinkedIn posts tailored to your style and stance.

## How It Works

1. **Context Selection (`DraftContextService`):** Embeds your idea, runs full-text and semantic retrieval over stored
   posts, fuses rankings, and selects voice examples (human-authored posts tuned by style/length) and knowledge
   references (contextual posts with explicit stances).
2. **Draft Generation (`DraftService` + CrewAI):** Injects the core idea, tuned voice examples, and stance-annotated
   knowledge posts into a structured writer task to produce a LinkedIn-ready draft.
3. **Persistence & Import:** Stores and queries posts locally in SQLite and supports importing historical posts from
   `Shares.csv`.

## Development Guidelines

### Requirements

| Requirement      | Description                                                 |
|:-----------------|:------------------------------------------------------------|
| **Python 3.12+** | Supported Python range (`>=3.12,<3.14`).                    |
| **uv**           | Python package and project manager. Install using Homebrew: |

```bash
brew install uv

```

### Development Commands

The following tools are configured in [`pyproject.toml`](pyproject.toml).

| Task                 | Tool     | Command                   |
|----------------------|----------|---------------------------|
| Static type checking | `mypy`   | `uv run mypy src`         |
| Code linting         | `ruff`   | `uv run ruff check --fix` |
| Code formatting      | `ruff`   | `uv run ruff format`      |
| Testing              | `pytest` | `uv run pytest`           |

### Running the CLI

Run the CLI application using:

```bash
uv run li2p

```

Available commands:

| Command       | Description                                                         |
|---------------|---------------------------------------------------------------------|
| `show-config` | Display active application configuration.                           |
| `draft`       | Draft a post from an input idea using context retrieval and CrewAI. |
| `csv-import`  | Import LinkedIn posts from a CSV file (`Shares.csv`).               |
| `list-posts`  | List stored posts.                                                  |

Configuration options are defined in [config.py](src/linkedin_idea_to_post/config.py) and set via:

- the [config.toml](config.toml) file
- or corresponding env variables (e.g. `WRITER_LLM__API_KEY="..."`)

### Pre-commit Hooks

Install the pre-commit hook to automatically lint and format your code before each commit:

```bash
uv run pre-commit install

```

## Dependencies

The project aims to keep external dependencies focused and explicit.

| Dependency                                                               | Usage                                                                              | Scope / Reference                                                                              |
|--------------------------------------------------------------------------|------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| [Click](https://github.com/pallets/click)                                | Builds the `li2p` CLI commands and options.                                        | [`cli.py`](https://www.google.com/search?q=src/linkedin_idea_to_post/cli.py)                   |
| [CrewAI](https://github.com/crewaiinc/crewai)                            | Orchestrates the writer agent and task execution for drafting posts.               | [`ai_workflow`](https://www.google.com/search?q=src/linkedin_idea_to_post/adapter/ai_workflow) |
| [NumPy](https://numpy.org/)                                              | Vector operations and binary BLOB serialization for embeddings.                    | [`embedding`](https://www.google.com/search?q=src/linkedin_idea_to_post/adapter/embedding)     |
| [Pydantic](https://github.com/pydantic/pydantic)                         | Domain models, selection/stance types, and validation.                             | Domain & use-case layer                                                                        |
| [Pydantic Settings](https://github.com/pydantic/pydantic-settings)       | Loads and validates application configuration from TOML and environment variables. | [`config.py`](https://www.google.com/search?q=src/linkedin_idea_to_post/config.py)             |
| [Rich](https://github.com/Textualize/rich)                               | Formats terminal tables, panels, and CLI output.                                   | [`cli.py`](https://www.google.com/search?q=src/linkedin_idea_to_post/cli.py)                   |
| [Sentence-Transformers](https://github.com/UKPLab/sentence-transformers) | Generates dense semantic embeddings for posts and queries.                         | [`embedding`](https://www.google.com/search?q=src/linkedin_idea_to_post/adapter/embedding)     |
| [PyTorch](https://pytorch.org/)                                          | Underlying tensor runtime across CPU, CUDA, and MPS devices.                       | Backend for `sentence-transformers`                                                            |

