# Project setup tool

Pick a profile, and get a Python project with a virtual environment, a Git repository, a ruff configuration, a Dockerfile, VS Code settings and its dependencies installed. Choose a name and a profile, and the tool writes the whole tree; the same work runs from a PyQt5 window or from the command line.

[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![CI](https://github.com/aa-blinov/project-setup-tool/actions/workflows/ci.yml/badge.svg)](https://github.com/aa-blinov/project-setup-tool/actions/workflows/ci.yml)

---

## Quick start

```bash
git clone https://github.com/aa-blinov/project-setup-tool.git
cd project-setup-tool
uv sync
uv run pst-cli my-api fastapi
```

The last command creates `~/projects/my-api` with the FastAPI layout, installs the dependencies into a `.venv`, and opens the folder in an editor. The machine needs Python 3.10 or newer, [uv](https://docs.astral.sh/uv/getting-started/installation/) and Git; the tool also fetches a `.gitignore` from `raw.githubusercontent.com`, and an editor is optional. On a Mac with an Apple chip, `uv sync` fails on the pinned `PyQt5-Qt5==5.15.2`, which has no arm64 wheel; `AGENTS.md` says what to do about it.

| Command | What it does |
| --- | --- |
| `uv run pst` | The window: a profile drop-down, an output directory picker, an output console and a progress bar. |
| `uv run pst-cli` | The terminal, asking for the name and the profile. |
| `uv run pst-cli my-api fastapi` | The terminal, without questions. The profile is a slug or a number from 1 to 20. |
| `uv run pst-cli --list` | The 20 profiles, with their slugs and labels. |
| `uv run pst-cli my-bot telegram --no-editor` | Leaves the finished folder closed. |

## What it does

- **Scaffolds from 20 profiles.** Each profile writes its own tree: source files, a test file, a README and a `requirements.txt`, and 15 of them a `Dockerfile` and a `docker-compose.yml` as well. The `fastapi-db` profile, for instance, writes `app/main.py`, `app/models.py`, `app/routers/items.py`, an Alembic environment and a health check test.
- **Creates the virtual environment with uv.** `uv venv` puts the environment in `.venv` inside the new project, and the dependencies go into it with `uv pip install`.
- **Initialises Git and fetches a `.gitignore`.** `git init` runs in the new directory, and the Python `.gitignore` comes from the `github/gitignore` repository over HTTPS with a 10 second timeout.
- **Writes the ruff configuration.** `ruff.toml` sets a line length of 88 and turns on the `E`, `F`, `W`, `B` and `C` rule sets.
- **Writes the Docker files.** The `Dockerfile` runs on `python:3.12-slim` and installs the requirements with uv; the data profile gets a Jupyter notebook image on port 8888 instead, and the FastAPI profile gets port 8000 in the compose file.
- **Writes the VS Code settings.** `.vscode/settings.json` points at the interpreter in `.venv`, makes ruff the formatter for Python files, and turns the pytest runner on with the `tests` folder as its argument.
- **Adds the test tools to every project.** The requirements file carries the profile's own dependencies plus pytest, pytest-cov, pytest-mock, pytest-xdist, pytest-asyncio and pytest-profiling.
- **Opens the result in an editor.** VS Code, VS Code Insiders, Cursor, Windsurf, VSCodium and VS Code OSS are tried in that order, then the path in `VSCODE_PATH`, and finally the system file explorer.
- **Checks the project name.** A name with `\ / : * ? " < > |` or with `..` in it is refused before anything is written.

## Profiles

| # | Slug | Label | Packages |
| --- | --- | --- | --- |
| 1 | `basic` | Basic Python Project | none |
| 2 | `data` | Data Analytics Project | jupyter, pandas, numpy, matplotlib |
| 3 | `fastapi` | FastAPI Project | fastapi, uvicorn, httpx |
| 4 | `fastapi-db` | FastAPI + SQLAlchemy + Alembic | fastapi, uvicorn[standard], sqlalchemy[asyncio], alembic, aiosqlite, asyncpg, pydantic, anyio[trio], httpx |
| 5 | `flask` | Flask Web App | flask, flask-cors |
| 6 | `streamlit` | Streamlit Dashboard | streamlit, pandas, plotly |
| 7 | `cli` | CLI Tool (Typer) | typer, rich |
| 8 | `telegram` | Telegram Bot (aiogram 3) | aiogram, python-dotenv |
| 9 | `discord` | Discord Bot (discord.py) | discord.py, python-dotenv |
| 10 | `django` | Django Web App | django, gunicorn, python-dotenv, pytest-django |
| 11 | `grpc` | gRPC Service | grpcio, grpcio-tools, protobuf |
| 12 | `celery` | Celery Worker | celery, redis, python-dotenv |
| 13 | `ml` | ML Project (scikit-learn) | scikit-learn, pandas, numpy, matplotlib, jupyter, mlflow |
| 14 | `scraper` | Web Scraper (httpx + BS4) | httpx, beautifulsoup4, lxml |
| 15 | `pypi` | PyPI Package | build, twine, hatchling |
| 16 | `langchain` | LangChain Agent | langchain, langchain-openai, langchain-community, langchain-core, python-dotenv |
| 17 | `llama` | LlamaIndex Agent | llama-index, llama-index-llms-openai, llama-index-embeddings-openai, python-dotenv |
| 18 | `mcp` | MCP Server (Model Context Protocol) | mcp[cli] |
| 19 | `lambda` | AWS Lambda (Serverless) | boto3, aws-lambda-powertools, python-dotenv |
| 20 | `pytest-plugin` | pytest Plugin | pytest, hatchling |

## How it works

```
name + profile
    -> SetupService.run()
        -> project directory
        -> .venv                 (uv venv)
        -> .gitignore            (downloaded)
        -> git init
        -> ruff.toml
        -> the profile's files
        -> .vscode/settings.json
        -> uv pip install
        -> the editor
```

The two front ends are thin. `app.py` builds the PyQt5 window and `cli.py` parses the arguments, and both hand the same values to `setup_service.SetupService`: the name, the profile index, and the callbacks for messages, progress and cancellation. The service imports no Qt, so the pipeline can be driven from a test or from a script.

`profiles.py` holds one class per profile. A class carries a label, a slug and a list of dependencies, and its `setup` method writes the files. `generators.py` holds the writers that several profiles share: the README, the Dockerfile, the compose file, the requirements file, the ruff configuration and the VS Code settings. `editor.py` looks for something to open the finished project in.

The nine steps report themselves as they finish. The progress bar counts them and reaches 100 at the end, and the message for each step carries its level in the text: `SUCCESS:`, `ERROR:` or `INFO:`. The window colours the three levels in the output console; the terminal prints a check mark, a cross or a middle dot in front of them.

## Configuration

| Variable | Default | What it does |
| --- | --- | --- |
| `PROJECT_BASE_PATH` | `~/projects` | The directory the new project is created in. |
| `VSCODE_PATH` | `C:\Program Files\Microsoft VS Code\Code.exe` | The last editor the tool tries to launch. |

`PROJECT_BASE_PATH` is read when `setup_service` is imported, so the window's output directory field overrides it and the command line has no way to change it.

Two settings live in the window rather than in the environment: the output directory, and the "Open in editor after creation" box, which is ticked by default. `--no-editor` turns the same thing off from the command line.

## Development

```bash
uv sync                  # install
uv run --dev pytest -v   # run the tests
uv run pst               # run the window
uv run pst-cli --list    # list the profiles
```

`uv run --dev pytest -v` is what the CI workflow runs, on ubuntu-latest, for every push to `master` and every pull request. The suite has 129 tests.

| Path | What it holds |
| --- | --- |
| `app.py` | The PyQt5 window. |
| `cli.py` | The command line front end. |
| `setup_service.py` | The pipeline, and the only module that runs `uv`, `git` and `requests`. |
| `profiles.py` | The 20 profile classes and the `ALL_PROFILES` list. |
| `generators.py` | The file writers the profiles share. |
| `editor.py` | The editor search and the file explorer fallback. |
| `tests/` | The tests. |
| `run.sh`, `run.bat` | Launchers for the window. |

A new profile is a class that subclasses `BaseProfile` in `profiles.py`, with a `setup` method that writes the files, and one line added to `ALL_PROFILES` at the bottom of the file. The window and the command line both read that list, so the profile appears in the drop-down and in `--list` at once.

## License

MIT, © aa-blinov. See [LICENSE](LICENSE).
