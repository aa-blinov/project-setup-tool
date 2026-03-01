"""Project setup pipeline.

SetupService is a plain Python class with no Qt dependency.
The GUI wires Qt signals in as ``on_message`` / ``on_progress`` callbacks.
"""

from __future__ import annotations

import os
import subprocess
import threading
from typing import Callable

import requests

from editor import open_in_editor
from generators import create_ruff_config, setup_vscode
from profiles import ALL_PROFILES, ProfileContext

BASE_PATH: str = os.environ.get(
    "PROJECT_BASE_PATH", os.path.join(os.path.expanduser("~"), "projects")
)


class SetupService:
    """Executes the full project-setup pipeline step by step."""

    def __init__(
        self,
        project_name: str,
        profile_index: int,
        on_message: Callable[[str], None],
        on_progress: Callable[[int], None],
        cancel_event: threading.Event,
        open_editor: bool = True,
        base_path: str | None = None,
    ) -> None:
        self._name = project_name
        self._profile_cls = ALL_PROFILES[profile_index]
        self._emit = on_message
        self._progress = on_progress
        self._cancel = cancel_event
        self._open_editor = open_editor
        self._base_path = base_path or BASE_PATH
        self._project_dir: str = ""
        self._venv_dir: str = ""

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Run the full setup. All exceptions are caught and reported via on_message."""
        total = 9
        step = 0

        def advance() -> None:
            nonlocal step
            step += 1
            self._progress(int(step / total * 100))

        def check() -> None:
            if self._cancel.is_set():
                raise InterruptedError("Setup cancelled by user.")

        try:
            os.makedirs(self._base_path, exist_ok=True)
            self._project_dir = os.path.join(self._base_path, self._name)
            if os.path.exists(self._project_dir):
                raise FileExistsError(
                    f'Project directory "{self._project_dir}" already exists.'
                )
            os.makedirs(self._project_dir)
            self._emit(f'SUCCESS: Created project directory "{self._project_dir}".')
            advance()
            check()

            self._venv_dir = os.path.join(self._project_dir, ".venv")
            result = subprocess.run(
                ["uv", "venv", self._venv_dir],
                check=True,
                cwd=self._project_dir,
                capture_output=True,
                text=True,
            )
            if result.stderr:
                self._emit(result.stderr.strip())
            self._emit("SUCCESS: Virtual environment created.")
            advance()
            check()

            self._download_gitignore()
            advance()
            check()

            self._init_git()
            advance()
            check()

            create_ruff_config(self._project_dir)
            self._emit("SUCCESS: ruff.toml created.")
            advance()
            check()

            ctx = ProfileContext(project_name=self._name, emit=self._emit)
            self._profile_cls().setup(self._project_dir, ctx)
            advance()
            check()

            setup_vscode(self._project_dir)
            self._emit("SUCCESS: VS Code settings configured.")
            advance()
            check()

            self._install_dependencies()
            advance()
            check()

            if self._open_editor:
                _ok, msg = open_in_editor(self._project_dir)
                self._emit(msg)
            self._progress(100)

        except InterruptedError as e:
            self._emit(f"INFO: {e}")
        except Exception as e:
            self._emit(f"ERROR: {e}")

    # ------------------------------------------------------------------
    # Individual steps — also tested directly in unit tests
    # ------------------------------------------------------------------

    def _download_gitignore(self) -> None:
        url = "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            raise Exception("Failed to download .gitignore file.")
        with open(
            os.path.join(self._project_dir, ".gitignore"), "w", encoding="utf-8"
        ) as f:
            f.write(response.text)
        self._emit("SUCCESS: .gitignore downloaded.")

    def _init_git(self) -> None:
        result = subprocess.run(
            ["git", "init"],
            check=True,
            cwd=self._project_dir,
            capture_output=True,
            text=True,
        )
        if result.stdout:
            self._emit(result.stdout.strip())
        self._emit("SUCCESS: Git repository initialized.")

    def _install_dependencies(self) -> None:
        self._emit("INFO: Installing dependencies...")
        python_bin = (
            os.path.join(self._venv_dir, "Scripts", "python.exe")
            if os.name == "nt"
            else os.path.join(self._venv_dir, "bin", "python")
        )
        result = subprocess.run(
            ["uv", "pip", "install", "--python", python_bin, "-r", "requirements.txt"],
            check=True,
            cwd=self._project_dir,
            capture_output=True,
            text=True,
        )
        if result.stderr:
            self._emit(result.stderr.strip())
        self._emit("SUCCESS: Dependencies installed.")
