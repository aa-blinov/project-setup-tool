"""
Project Setup Tool

This script automates the process of initializing new projects by creating project directories,
setting up virtual environments, initializing Git repositories, and generating essential
configuration files. The tool supports different types of projects, including basic Python
projects, data analytics projects, and FastAPI projects.

Author: aa.blinov
"""

import sys
import os
import subprocess
import threading
import json
import venv
import requests
from PyQt5 import QtWidgets, QtGui, QtCore

BASE_PATH: str = r"D:\eora"
VSCODE_PATH: str = r"C:\Program Files\Microsoft VS Code\Code.exe"


class OutputHighlighter(QtGui.QSyntaxHighlighter):
    """Syntax highlighter for the output console."""

    def __init__(self, document: QtGui.QTextDocument) -> None:
        super().__init__(document)
        self._formats: dict = {}
        self._setup_formats()

    def _setup_formats(self) -> None:
        """Set up formats for different logging levels."""
        self._formats["ERROR"] = self._create_format("#FF5252")  # Red
        self._formats["SUCCESS"] = self._create_format("#4CAF50")  # Green
        self._formats["INFO"] = self._create_format("#FFFFFF")  # White

    def _create_format(self, color: str) -> QtGui.QTextCharFormat:
        """Create a QTextCharFormat with the given color."""
        format: QtGui.QTextCharFormat = QtGui.QTextCharFormat()
        format.setForeground(QtGui.QColor(color))
        return format

    def highlightBlock(self, text: str) -> None:
        """Apply syntax highlighting to a block of text."""
        for level, format in self._formats.items():
            if text.startswith(level):
                self.setFormat(0, len(text), format)
                break


class ProjectSetupApp(QtWidgets.QWidget):
    """Main application class for project setup."""

    output_signal = QtCore.pyqtSignal(str)
    progress_signal = QtCore.pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        self.project_name: str = ""
        self.project_type: int = 0
        self.process = None
        self.init_ui()

        # Connect signals to slots
        self.output_signal.connect(self.append_output)
        self.progress_signal.connect(self.update_progress)

    def init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("Project Setup Tool")
        self.resize(800, 600)

        # Apply dark theme in Material Design style
        self.apply_dark_theme()

        # Create layouts
        main_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        form_layout: QtWidgets.QFormLayout = QtWidgets.QFormLayout()

        # Project name input field
        self.name_input: QtWidgets.QLineEdit = QtWidgets.QLineEdit()
        form_layout.addRow("Project Name:", self.name_input)

        # Project type selection
        self.type_combo: QtWidgets.QComboBox = QtWidgets.QComboBox()
        self.type_combo.addItems(["1 - Basic Python Project", "2 - Data Analytics Project", "3 - FastAPI Project"])
        form_layout.addRow("Project Type:", self.type_combo)

        # "Create" and "Cancel" buttons
        button_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        self.create_button: QtWidgets.QPushButton = QtWidgets.QPushButton("Create Project")
        self.create_button.clicked.connect(self.create_project)
        self.cancel_button: QtWidgets.QPushButton = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.cancel_button)

        # Output console
        self.output_text: QtWidgets.QTextEdit = QtWidgets.QTextEdit()
        self.output_text.setReadOnly(True)
        self.highlighter: OutputHighlighter = OutputHighlighter(self.output_text.document())

        # Progress bar
        self.progress_bar: QtWidgets.QProgressBar = QtWidgets.QProgressBar()
        self.progress_bar.setValue(0)

        # Assemble layouts
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(QtWidgets.QLabel("Output:"))
        main_layout.addWidget(self.output_text)
        main_layout.addWidget(self.progress_bar)

        self.setLayout(main_layout)

    def apply_dark_theme(self) -> None:
        """Apply a dark theme in Material Design style."""
        dark_palette: QtGui.QPalette = QtGui.QPalette()
        dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(38, 50, 56))
        dark_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 255, 255))
        dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(33, 33, 33))
        dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(38, 50, 56))
        dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(255, 255, 255))
        dark_palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(255, 255, 255))
        dark_palette.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))
        dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(38, 50, 56))
        dark_palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(255, 255, 255))
        dark_palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 0, 0))
        dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(41, 128, 185))
        dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(41, 128, 185))
        dark_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
        self.setPalette(dark_palette)

        # Set Fusion style
        QtWidgets.QApplication.setStyle("Fusion")

    def append_output(self, text: str) -> None:
        """Add text to the output console."""
        self.output_text.append(text)
        self.output_text.ensureCursorVisible()

    def update_progress(self, value: int) -> None:
        """Update the progress bar."""
        self.progress_bar.setValue(value)

    def create_project(self) -> None:
        """Start the project creation process."""
        self.project_name = self.name_input.text().strip()
        self.project_type = self.type_combo.currentIndex() + 1

        if not self.project_name:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter a project name.")
            return

        # Disable buttons during execution
        self.create_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.output_text.clear()

        # Start setup in a separate thread
        threading.Thread(target=self.run_setup, daemon=True).start()

    def run_setup(self) -> None:
        """Execute the project setup process."""
        try:
            total_steps: int = 9  # Total number of steps for progress tracking
            current_step: int = 0

            project_dir: str = os.path.join(BASE_PATH, self.project_name)

            if os.path.exists(project_dir):
                raise FileExistsError(f'ERROR: Project directory "{project_dir}" already exists.')

            os.makedirs(project_dir)
            os.chdir(project_dir)
            self.output_signal.emit(f'SUCCESS: Created project directory "{project_dir}".')
            current_step += 1
            self.progress_signal.emit(int((current_step / total_steps) * 100))

            # Create virtual environment
            venv_dir: str = os.path.join(project_dir, ".venv")
            venv.create(venv_dir, with_pip=True)
            self.output_signal.emit("SUCCESS: Virtual environment created.")
            current_step += 1
            self.progress_signal.emit(int((current_step / total_steps) * 100))

            # Download .gitignore
            self.download_gitignore()
            current_step += 1
            self.progress_signal.emit(int((current_step / total_steps) * 100))

            # Initialize Git repository
            self.init_git()
            current_step += 1
            self.progress_signal.emit(int((current_step / total_steps) * 100))

            # Create ruff configuration
            self.create_ruff_config()
            current_step += 1
            self.progress_signal.emit(int((current_step / total_steps) * 100))

            # Set up the project based on type
            if self.project_type == 1:
                self.setup_basic_python_project()
            elif self.project_type == 2:
                self.setup_data_analytics_project()
            elif self.project_type == 3:
                self.setup_fastapi_project()
            else:
                raise ValueError("ERROR: Invalid project type selected.")
            current_step += 1
            self.progress_signal.emit(int((current_step / total_steps) * 100))

            # Configure VS Code
            self.setup_vscode()
            self.output_signal.emit("SUCCESS: VS Code settings configured.")
            current_step += 1
            self.progress_signal.emit(int((current_step / total_steps) * 100))

            # Install dependencies
            self.install_dependencies(venv_dir)
            current_step += 1
            self.progress_signal.emit(int((current_step / total_steps) * 100))

            # Open the project in VS Code
            self.open_in_vscode(project_dir)
            current_step += 1
            self.progress_signal.emit(100)

            # Re-enable buttons after completion
            self.create_button.setEnabled(True)
            self.cancel_button.setEnabled(True)

        except Exception as e:
            self.output_signal.emit(f"ERROR: {e}")
            self.create_button.setEnabled(True)
            self.cancel_button.setEnabled(True)

    def download_gitignore(self) -> None:
        """Download .gitignore file."""
        gitignore_url: str = "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore"
        response: requests.Response = requests.get(gitignore_url)
        if response.status_code == 200:
            with open(".gitignore", "w", encoding="utf-8") as f:
                f.write(response.text)
            self.output_signal.emit("SUCCESS: .gitignore file downloaded.")
        else:
            raise Exception("ERROR: Failed to download .gitignore file.")

    def init_git(self) -> None:
        """Initialize Git repository."""
        subprocess.run(["git", "init"], check=True)
        self.output_signal.emit("SUCCESS: Git repository initialized.")

    def create_ruff_config(self) -> None:
        """Create ruff configuration."""
        ruff_config: str = "[tool.ruff]\n" "line-length = 88\n" 'select = ["E", "F", "W", "B", "C"]\n' "ignore = []\n"
        with open("ruff.toml", "w", encoding="utf-8") as f:
            f.write(ruff_config)
        self.output_signal.emit("SUCCESS: ruff.toml file created.")

    def setup_basic_python_project(self) -> None:
        """Set up a basic Python project."""
        os.makedirs("app", exist_ok=True)
        os.makedirs("tests", exist_ok=True)

        main_py_content: str = 'print("Hello, World!")\n'
        with open(os.path.join("app", "main.py"), "w", encoding="utf-8") as f:
            f.write(main_py_content)

        test_basic_content: str = "def test_true():\n" "    assert True\n"
        with open(os.path.join("tests", "test_basic.py"), "w", encoding="utf-8") as f:
            f.write(test_basic_content)

        self.create_readme("python app/main.py")
        self.create_docker_files("python app/main.py")
        self.create_requirements(
            ["pytest", "pytest-cov", "pytest-mock", "pytest-xdist", "pytest-asyncio", "pytest-profiling"]
        )

        self.output_signal.emit("SUCCESS: Basic Python project set up.")

    def setup_data_analytics_project(self) -> None:
        """Set up a data analytics project."""
        os.makedirs("notebooks", exist_ok=True)
        os.makedirs("tests", exist_ok=True)

        # Create a basic Jupyter notebook
        notebook_content: dict = {
            "cells": [
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": ['print("Hello, World!")'],
                }
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        with open(os.path.join("notebooks", "analysis.ipynb"), "w", encoding="utf-8") as f:
            json.dump(notebook_content, f)

        test_notebook_content: str = "def test_true():\n" "    assert True\n"
        with open(os.path.join("tests", "test_notebook.py"), "w", encoding="utf-8") as f:
            f.write(test_notebook_content)

        self.create_readme("jupyter notebook notebooks/analysis.ipynb")
        self.create_docker_files(None, is_data_project=True)
        self.create_requirements(
            ["jupyter", "pytest", "pytest-cov", "pytest-mock", "pytest-xdist", "pytest-asyncio", "pytest-profiling"]
        )

        self.output_signal.emit("SUCCESS: Data analytics project set up.")

    def setup_fastapi_project(self) -> None:
        """Set up a FastAPI project."""
        os.makedirs("app", exist_ok=True)
        os.makedirs("tests", exist_ok=True)

        main_py_content: str = (
            "from fastapi import FastAPI\n"
            "\n"
            "app = FastAPI()\n"
            "\n"
            '@app.get("/")\n'
            "async def read_root():\n"
            '    return {"Hello": "World"}\n'
        )
        with open(os.path.join("app", "main.py"), "w", encoding="utf-8") as f:
            f.write(main_py_content)

        test_app_content: str = (
            "import pytest\n"
            "from httpx import AsyncClient\n"
            "from app.main import app\n"
            "\n"
            "@pytest.mark.asyncio\n"
            "async def test_read_root():\n"
            '    async with AsyncClient(app=app, base_url="http://test") as ac:\n'
            '        response = await ac.get("/")\n'
            "    assert response.status_code == 200\n"
            '    assert response.json() == {"Hello": "World"}\n'
        )
        with open(os.path.join("tests", "test_app.py"), "w", encoding="utf-8") as f:
            f.write(test_app_content)

        self.create_readme("uvicorn app.main:app --reload")
        self.create_docker_files("uvicorn app.main:app --host 0.0.0.0 --port 8000", is_fastapi=True)
        self.create_requirements(
            [
                "fastapi",
                "uvicorn",
                "pytest",
                "pytest-cov",
                "pytest-mock",
                "pytest-xdist",
                "pytest-asyncio",
                "pytest-profiling",
                "httpx",
            ]
        )

        self.output_signal.emit("SUCCESS: FastAPI project set up.")

    def create_readme(self, run_command: str) -> None:
        """Create the README.md file."""
        readme_content: str = (
            f"# {self.project_name}\n\n"
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
            f"docker build -t {self.project_name} .\n"
            "\n"
            "### Run Docker Container\n"
            "\n"
        )
        if "uvicorn" in run_command:
            readme_content += f"docker run -p 8000:8000 {self.project_name}\n"
        elif "jupyter" in run_command:
            readme_content += f"docker run -p 8888:8888 {self.project_name}\n"
        else:
            readme_content += f"docker run --rm {self.project_name}\n"
        readme_content += "\n" "## Docker Compose Usage\n" "\n" "docker-compose up --build\n" "\n"

        with open("README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)

    def create_docker_files(self, command: str | None, is_data_project: bool = False, is_fastapi: bool = False) -> None:
        """Create Dockerfile and docker-compose.yml."""
        if is_data_project:
            dockerfile_content: str = (
                "FROM jupyter/base-notebook:python-3.11.6\n" "COPY notebooks/ /home/jovyan/work/\n"
            )
            with open("Dockerfile", "w", encoding="utf-8") as f:
                f.write(dockerfile_content)

            docker_compose_content: str = (
                "services:\n"
                "  jupyter:\n"
                "    build: .\n"
                "    ports:\n"
                '      - "8888:8888"\n'
                "    volumes:\n"
                "      - ./notebooks:/home/jovyan/work\n"
            )
            with open("docker-compose.yml", "w", encoding="utf-8") as f:
                f.write(docker_compose_content)
        else:
            dockerfile_content: str = (
                "FROM python:3.9-slim\n"
                "WORKDIR /app\n"
                "COPY requirements.txt .\n"
                "RUN pip install --no-cache-dir -r requirements.txt\n"
                "COPY . .\n"
            )
            if command:
                cmd_list: list = command.split()
                dockerfile_content += "CMD ["
                dockerfile_content += ", ".join(f'"{arg}"' for arg in cmd_list)
                dockerfile_content += "]\n"
            else:
                dockerfile_content += 'CMD ["python", "app/main.py"]\n'

            with open("Dockerfile", "w", encoding="utf-8") as f:
                f.write(dockerfile_content)

            docker_compose_content: str = "services:\n" "  app:\n" "    build: .\n"
            if is_fastapi:
                docker_compose_content += "    ports:\n" '      - "8000:8000"\n'
            docker_compose_content += f"    command: {command}\n"

            with open("docker-compose.yml", "w", encoding="utf-8") as f:
                f.write(docker_compose_content)

    def create_requirements(self, packages: list) -> None:
        """Create the requirements.txt file."""
        requirements_content: str = "\n".join(packages) + "\n"
        with open("requirements.txt", "w", encoding="utf-8") as f:
            f.write(requirements_content)

    def install_dependencies(self, venv_dir: str) -> None:
        """Install dependencies in the virtual environment."""
        self.output_signal.emit("INFO: Installing dependencies...")
        pip_executable: str = (
            os.path.join(venv_dir, "Scripts", "pip.exe") if os.name == "nt" else os.path.join(venv_dir, "bin", "pip")
        )
        try:
            subprocess.run([pip_executable, "install", "-r", "requirements.txt"], check=True)
            self.output_signal.emit("SUCCESS: Dependencies installed.")
        except subprocess.CalledProcessError as e:
            self.output_signal.emit(f"ERROR: Failed to install dependencies: {e}")

    def setup_vscode(self) -> None:
        """Configure VS Code settings."""
        vscode_dir: str = os.path.join(".vscode")
        os.makedirs(vscode_dir, exist_ok=True)
        settings: dict = {
            "python.pythonPath": ".venv\\Scripts\\python.exe" if os.name == "nt" else ".venv/bin/python",
            "editor.formatOnSave": True,
            "python.linting.enabled": True,
            "python.linting.ruffEnabled": True,
            "python.linting.ruffPath": ".venv\\Scripts\\ruff.exe" if os.name == "nt" else ".venv/bin/ruff",
            "python.testing.pytestEnabled": True,
            "python.testing.pytestArgs": ["tests"],
        }
        with open(os.path.join(vscode_dir, "settings.json"), "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)

    def open_in_vscode(self, project_dir: str) -> None:
        """Open the project in VS Code."""
        code_command: list = [VSCODE_PATH, project_dir]
        try:
            subprocess.run(code_command, check=True)
            self.output_signal.emit("SUCCESS: Project opened in VS Code.")
        except FileNotFoundError:
            self.output_signal.emit("ERROR: Could not find VS Code. Ensure that the path is correct.")
        except subprocess.CalledProcessError as e:
            self.output_signal.emit(f"ERROR: Failed to open VS Code: {e}")


if __name__ == "__main__":
    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv + ["-platform", "windows:darkmode=1"])

    # Apply dark theme
    dark_palette: QtGui.QPalette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(38, 50, 56))
    dark_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(33, 33, 33))
    dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(38, 50, 56))
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(38, 50, 56))
    dark_palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 0, 0))
    dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(41, 128, 185))
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(41, 128, 185))
    dark_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
    app.setPalette(dark_palette)

    app.setStyle("Fusion")

    window: ProjectSetupApp = ProjectSetupApp()
    window.show()
    sys.exit(app.exec_())
