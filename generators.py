"""Pure file-generation helpers.

All functions are stateless and have no Qt or subprocess dependency.
They can be imported by profiles, SetupService, and tests alike.
"""

from __future__ import annotations

import json
import os


def _write(project_dir: str, relative_path: str, content: str) -> None:
    """Write *content* to *relative_path* inside *project_dir*, creating parents."""
    full = os.path.join(project_dir, *relative_path.split("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)


def create_ruff_config(project_dir: str) -> None:
    """Write ruff.toml with standard lint rules."""
    _write(
        project_dir,
        "ruff.toml",
        'line-length = 88\n\n[lint]\nselect = ["E", "F", "W", "B", "C"]\nignore = []\n',
    )


def create_requirements(project_dir: str, packages: list[str]) -> None:
    """Write requirements.txt with one package per line."""
    _write(project_dir, "requirements.txt", "\n".join(packages) + "\n")


def create_readme(project_dir: str, project_name: str, run_command: str) -> None:
    """Write README.md with How-to-Run and Docker sections."""
    if "uvicorn" in run_command:
        docker_run = f"docker run -p 8000:8000 {project_name}\n"
    elif "jupyter" in run_command:
        docker_run = f"docker run -p 8888:8888 {project_name}\n"
    else:
        docker_run = f"docker run --rm {project_name}\n"

    content = (
        f"# {project_name}\n\n"
        "## How to Run\n"
        "\n"
        f"{run_command}\n"
        "\n"
        "## How to Run Tests\n"
        "\n"
        "pytest\n"
        "\n"
        "## Docker Usage\n"
        "### Build Docker Image\n"
        "\n"
        f"docker build -t {project_name} .\n"
        "\n"
        "### Run Docker Container\n"
        "\n" + docker_run + "\n"
        "## Docker Compose Usage\n"
        "\n"
        "docker-compose up --build\n"
        "\n"
    )
    _write(project_dir, "README.md", content)


def create_docker_files(
    project_dir: str,
    command: str | None,
    is_data_project: bool = False,
    is_fastapi: bool = False,
) -> None:
    """Write Dockerfile and docker-compose.yml."""
    if is_data_project:
        _write(
            project_dir,
            "Dockerfile",
            "FROM jupyter/base-notebook:python-3.11.6\n"
            "COPY notebooks/ /home/jovyan/work/\n",
        )
        _write(
            project_dir,
            "docker-compose.yml",
            "services:\n"
            "  jupyter:\n"
            "    build: .\n"
            "    ports:\n"
            '      - "8888:8888"\n'
            "    volumes:\n"
            "      - ./notebooks:/home/jovyan/work\n",
        )
        return

    if command:
        cmd_list = command.split()
        cmd_part = "CMD [" + ", ".join(f'"{a}"' for a in cmd_list) + "]\n"
    else:
        cmd_part = 'CMD ["python", "app/main.py"]\n'

    _write(
        project_dir,
        "Dockerfile",
        "FROM python:3.12-slim\n"
        "COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv\n"
        "WORKDIR /app\n"
        "COPY requirements.txt .\n"
        "RUN uv pip install --system --no-cache -r requirements.txt\n"
        "COPY . .\n" + cmd_part,
    )

    compose = "services:\n  app:\n    build: .\n"
    if is_fastapi:
        compose += '    ports:\n      - "8000:8000"\n'
    if command:
        compose += f"    command: {command}\n"
    _write(project_dir, "docker-compose.yml", compose)


def setup_vscode(project_dir: str) -> None:
    """Write .vscode/settings.json with Python, ruff, and pytest settings."""
    settings: dict = {
        "python.defaultInterpreterPath": (
            ".venv\\Scripts\\python.exe" if os.name == "nt" else ".venv/bin/python"
        ),
        "editor.formatOnSave": True,
        "[python]": {"editor.defaultFormatter": "charliermarsh.ruff"},
        "ruff.enable": True,
        "python.testing.pytestEnabled": True,
        "python.testing.pytestArgs": ["tests"],
    }
    vscode_dir = os.path.join(project_dir, ".vscode")
    os.makedirs(vscode_dir, exist_ok=True)
    with open(os.path.join(vscode_dir, "settings.json"), "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)
