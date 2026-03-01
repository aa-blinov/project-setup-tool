# Project Setup Tool

A GUI + CLI tool for quickly bootstrapping Python projects with a predefined structure, virtual environment, Git, ruff, and VS Code configuration.

## Features

- **18 project profiles** — from basic scripts to FastAPI+SQLAlchemy, Discord bots, MCP servers, and LLM agents
- **GUI** (PyQt5): dark Material theme, output directory picker, per-profile dependency preview, progress bar, abort button
- **CLI** (`pst-cli`): non-interactive mode with profile selection by slug or number, `--list`, `--no-editor`
- **Project scaffolding**: directory + `.venv` via [uv](https://github.com/astral-sh/uv)
- **Git**: `git init` + auto-download of Python `.gitignore`
- **Linter**: `ruff.toml` with rules `E`, `F`, `W`, `B`, `C`
- **Docker**: `Dockerfile` + `docker-compose.yml` tailored to each profile
- **VS Code**: `.vscode/settings.json` with interpreter, ruff, and pytest settings
- **Dependency installation**: `uv pip install` into the created virtual environment
- **Editor auto-open**: tries VS Code, VS Code Insiders, Cursor, Windsurf, VSCodium; falls back to the system file explorer
- **CI**: `.github/workflows/ci.yml` included in the tool itself

## Profiles

| # | Slug | Label | Key packages |
|---|------|-------|--------------|
| 1 | `basic` | Basic Python Project | — |
| 2 | `data` | Data Analytics | jupyter, pandas, numpy, matplotlib |
| 3 | `fastapi` | FastAPI | fastapi, uvicorn, httpx |
| 4 | `fastapi-db` | FastAPI + SQLAlchemy + Alembic | fastapi, sqlalchemy[asyncio], alembic, aiosqlite |
| 5 | `flask` | Flask Web App | flask, flask-cors |
| 6 | `streamlit` | Streamlit Dashboard | streamlit, pandas, plotly |
| 7 | `cli` | CLI Tool (Typer) | typer, rich |
| 8 | `telegram` | Telegram Bot (aiogram 3) | aiogram, python-dotenv |
| 9 | `discord` | Discord Bot (discord.py) | discord.py, python-dotenv |
| 10 | `django` | Django Web App | django, gunicorn, python-dotenv |
| 11 | `grpc` | gRPC Service | grpcio, grpcio-tools, protobuf |
| 12 | `celery` | Celery Worker | celery, redis, python-dotenv |
| 13 | `ml` | ML Project (scikit-learn) | scikit-learn, pandas, numpy, mlflow |
| 14 | `scraper` | Web Scraper (httpx + BS4) | httpx, beautifulsoup4, lxml |
| 15 | `pypi` | PyPI Package | build, twine, hatchling |
| 16 | `langchain` | LangChain Agent | langchain, langchain-openai, python-dotenv |
| 17 | `llama` | LlamaIndex Agent | llama-index, llama-index-llms-openai |
| 18 | `mcp` | MCP Server (Model Context Protocol) | mcp[cli] |
| 19 | `lambda` | AWS Lambda (Serverless) | boto3, aws-lambda-powertools, python-dotenv |
| 20 | `pytest-plugin` | pytest Plugin | pytest, hatchling |

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Git
- A supported editor (optional): VS Code, VS Code Insiders, Cursor, Windsurf, VSCodium

## Installation

```bash
git clone https://github.com/aa-blinov/project-setup-tool.git
cd project-setup-tool
uv sync
```

## Usage

### GUI

```bash
uv run pst
```

1. Enter a project name
2. Select a profile from the dropdown — description and packages are shown below
3. Choose the output directory (defaults to `~/projects`)
4. Click **Create Project**

### CLI

```bash
# Interactive — prompts for name and profile
uv run pst-cli

# Non-interactive by slug
uv run pst-cli my-api fastapi
uv run pst-cli my-bot telegram --no-editor

# Non-interactive by number
uv run pst-cli my-dash 6

# List all profiles
uv run pst-cli --list
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `PROJECT_BASE_PATH` | `~/projects` | Default root folder for new projects |

## Project Structure

```
project-setup-tool/
├── app.py            # PyQt5 GUI
├── cli.py            # CLI entry point
├── profiles.py       # All 18 project profiles (subclass BaseProfile to add more)
├── generators.py     # File generators (README, Docker, requirements, ruff, vscode)
├── setup_service.py  # Setup pipeline (no Qt dependency)
├── editor.py         # Editor auto-detection and launch
├── tests/
│   ├── test_project_templates.py   # basic, data, fastapi profiles
│   ├── test_new_profiles.py        # flask, fastapi-db, streamlit, mcp, discord
│   ├── test_cli.py                 # CLI slug resolution and validation
│   ├── test_file_generators.py     # generators.py unit tests
│   ├── test_subprocess_calls.py    # git/uv subprocess mocks
│   └── test_validation.py         # project name validation
└── .github/workflows/ci.yml
```

## Extending with a New Profile

```python
# profiles.py
class MyProfile(BaseProfile):
    label = "My Custom Profile"
    slug  = "my-profile"
    deps  = ["some-package", "another-package"]

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        _write(project_dir, "app/main.py", "print('hello')\n")
        ctx.create_readme(project_dir, "python app/main.py")
        ctx.create_docker_files(project_dir, "python app/main.py")
        ctx.create_requirements(project_dir, self.deps + _BASE_TEST_DEPS)
        ctx.emit("SUCCESS: My Custom Profile project set up.")

# Then add it to ALL_PROFILES list at the bottom of profiles.py
```

## Running Tests

```bash
uv run pytest -v
```

113 tests across all profiles and subsystems.

## Tool Dependencies

- `PyQt5 >= 5.15.11` (with `PyQt5-Qt5 == 5.15.2` override for Windows compatibility)
- `requests >= 2.32.3`

## License

MIT — see [LICENSE](LICENSE)


