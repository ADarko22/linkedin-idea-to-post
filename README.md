# linkedin-idea-to-post

An autonomous multi-agent system powered by **CrewAI** and **Google Gemini** that transforms raw, unfiltered thoughts
into structured, engaging LinkedIn posts contextualized with modern marketplace trends.

## How It Works

The application orchestrates a sequential workflow between two specialized AI agents:

| Agent                                    | Responsibility                                                                                                                                               |
|------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Idea Explorer & Trend Contextualizer** | Evaluates the raw idea and maps it against current industry shifts, identifying the context that makes it relevant and timely.                               |
| **Expert LinkedIn Creator**              | Transforms the expanded insight into a high-impact, mobile-optimized LinkedIn post, featuring a compelling hook, scannable spacing, and tailored formatting. |

## Development Guidelines

### Requirements

| Requirement     | Description                                                 |
|-----------------|-------------------------------------------------------------|
| **Python 3.12** | Required Python version.                                    |
| **uv**          | Python package and project manager. Install using Homebrew: |

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

### Running the Application

Run the CLI application using:

```bash
uv run linkedin-idea-to-post
```

Available commands:

| Command       | Description                            |
|---------------|----------------------------------------|
| `show-config` | Display application configuration.     |
| `csv-import`  | Import LinkedIn posts from a CSV file. |
| `list-posts`  | List archived posts.                   |

Configuration options are defined in [config.py](src/linkedin_idea_to_post/config.py) and set via:
- the [config.toml](config.toml) file
- or corresponding env variables (e.g. `DRAFTING__WRITER="crewai"`)

### Pre-commit Hooks

Install the pre-commit hook to automatically lint and format your code before each commit:

```bash
uv run pre-commit install
```

## Dependencies

The project aims to minimize external dependencies, using only the necessary modules and classes from each library.

| Dependency                                                         | Usage                                                                                                                                                    | Scope / Reference                                                        |
|--------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| [Click](https://github.com/pallets/click)                          | Builds the CLI, including help pages, nested commands, and lazy loading of subcommands.                                                                  | CLI entrypoint: [cli.py](src/linkedin_idea_to_post/cli.py)               |
| [Crewai](https://github.com/crewaiinc/crewai)                      | Builds an AI Workflow with agents for researching the web for trends and news regarding the idea and for drafting a post based on the generated context. | Used in the [ai_workflow](src/linkedin_idea_to_post/ai_workflow) module. |
| [Pydantic](https://github.com/pydantic/pydantic)                   | Data modeling, validation, and JSON encoding/decoding.                                                                                                   | Used extensively throughout the application.                             |
| [Pydantic Settings](https://github.com/pydantic/pydantic-settings) | Manages application-specific configuration.                                                                                                              | [config.py](src/linkedin_idea_to_post/config.py)                         |
| [Rich](https://github.com/Textualize/rich)                         | Provides rich terminal output.                                                                                                                           | CLI entrypoint: [cli.py](src/linkedin_idea_to_post/cli.py)               |
|                                                                    |                                                                                                                                                          |                                                            