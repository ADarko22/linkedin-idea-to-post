# linkedin-idea-to-post 

An autonomous multi-agent system powered by **CrewAI** and **Google Gemini** that takes a raw, unfiltered thought and
shapes it into a structured, highly engaging LinkedIn post contextualized with modern marketplace trends.

## How It Works

The project orchestrates a sequential workflow between two specialized AI agents:

1. **Idea Explorer & Trend Contextualizer:** Evaluates your raw seed idea and maps it against current industry shifts,
   finding the structural context that makes it urgent and relevant.
2. **Expert LinkedIn Creator:** Synthesizes the expanded insight into a high-impact, mobile-optimized LinkedIn post
   complete with a powerful hook, scannable spacing, and tailored formatting.

## Development Guidelines

1. **Install Python 3.12**: Ensure you have Python 3.12 installed on your system.
2. **Install uv**: Python package and project manager.
   ```bash
   brew install uv
   ```
3. **Static Type Checking with `mypy`**: configured in [pyproject.toml](pyproject.toml).
   ```bash
   uv run mypy src
   ```
4. **Code Linting and Formatting with `ruff`:** configured in [pyproject.toml](pyproject.toml).
    ```bash
    uv run ruff check --fix
    uv run ruff format
    ```
5. **Testing with `pytest`:** configured in [pyproject.toml](pyproject.toml).
   ```bash
   uv run pytest 
   ```
6. **Run the Application**: Use the following command to start the application.
   ```bash
   uv run linkedin-idea-to-post
   ```