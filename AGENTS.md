# Project Instructions

## Commands

- Install / sync deps: `uv sync` (or `pip install -e ".[dev]"`)
- Run tests: `pytest`
- Lint & format: `ruff check . && ruff format --check .`
- Type check: `mypy src`

## Architecture & Boundaries

- Keep core domain logic isolated from framework/LLM client code (CrewAI, Gemini SDK, SQLite, file/API adapters belong
  in outer layers).
- Do not hardcode API keys, secrets, or local absolute paths; load configuration via environment variables.
- Never publish or post externally automatically; outputs must remain local drafts for human review.

## Workflow Rules

- Before modifying more than 2 files, propose a brief plan and list affected modules.
- Every bug fix or new behavior must include or update corresponding unit tests under `tests/`.
- Run `pytest` and linter checks before concluding any implementation task.