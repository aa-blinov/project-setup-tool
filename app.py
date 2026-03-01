"""
Project Setup Tool

This script automates the process of initializing new projects by creating project directories,
setting up virtual environments, initializing Git repositories, and generating essential
configuration files. The tool supports different types of projects, including basic Python
projects, data analytics projects, and FastAPI projects.

Author: aa.blinov
"""

import sys
import re
import threading
from PyQt5 import QtWidgets, QtGui, QtCore

from profiles import ALL_PROFILES
from setup_service import BASE_PATH, SetupService

_INVALID_NAME_RE = re.compile(r'[\\/:*?"<>|]')


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
    buttons_signal = QtCore.pyqtSignal(bool)

    def __init__(self) -> None:
        super().__init__()
        self.project_name: str = ""
        self.project_type: int = 0
        self._cancel_event = threading.Event()
        self._setup_running = False
        self.init_ui()

        # Connect signals to slots
        self.output_signal.connect(self.append_output)
        self.progress_signal.connect(self.update_progress)
        self.buttons_signal.connect(self._set_buttons_enabled)

    def init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("Project Setup Tool")
        self.resize(820, 640)

        self.apply_dark_theme()

        main_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        main_layout.setSpacing(8)
        form_layout: QtWidgets.QFormLayout = QtWidgets.QFormLayout()
        form_layout.setSpacing(6)

        # Project name
        self.name_input: QtWidgets.QLineEdit = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("my-awesome-project")
        form_layout.addRow("Project Name:", self.name_input)

        # Project type — show slug in brackets
        self.type_combo: QtWidgets.QComboBox = QtWidgets.QComboBox()
        self.type_combo.addItems(
            [f"{i + 1} — {p.label}  [{p.slug}]" for i, p in enumerate(ALL_PROFILES)]
        )
        self.type_combo.currentIndexChanged.connect(self._on_profile_changed)
        form_layout.addRow("Project Type:", self.type_combo)

        # Output directory with Browse button
        dir_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        self.dir_input: QtWidgets.QLineEdit = QtWidgets.QLineEdit(BASE_PATH)
        self.dir_input.setToolTip("Directory where the project folder will be created")
        browse_btn: QtWidgets.QPushButton = QtWidgets.QPushButton("Browse…")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._browse_dir)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(browse_btn)
        form_layout.addRow("Output Dir:", dir_layout)

        # Open in editor checkbox
        self.open_editor_check: QtWidgets.QCheckBox = QtWidgets.QCheckBox(
            "Open in editor after creation"
        )
        self.open_editor_check.setChecked(True)
        form_layout.addRow("", self.open_editor_check)

        # Profile hint label
        self.profile_hint: QtWidgets.QLabel = QtWidgets.QLabel()
        self.profile_hint.setStyleSheet("color: #90A4AE; font-size: 11px;")
        self.profile_hint.setWordWrap(True)
        form_layout.addRow("", self.profile_hint)
        self._on_profile_changed(0)  # populate initial hint

        # Action buttons
        button_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        self.create_button: QtWidgets.QPushButton = QtWidgets.QPushButton(
            "Create Project"
        )
        self.create_button.clicked.connect(self.create_project)
        self.cancel_button: QtWidgets.QPushButton = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.cancel_button)

        # Output console
        self.output_text: QtWidgets.QTextEdit = QtWidgets.QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFontFamily("Consolas")
        self.highlighter: OutputHighlighter = OutputHighlighter(
            self.output_text.document()
        )

        # Output console header with Clear button
        output_header: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        output_header.addWidget(QtWidgets.QLabel("Output:"))
        output_header.addStretch()
        clear_btn: QtWidgets.QPushButton = QtWidgets.QPushButton("Clear")
        clear_btn.setFixedWidth(55)
        clear_btn.clicked.connect(self.output_text.clear)
        output_header.addWidget(clear_btn)

        # Progress bar
        self.progress_bar: QtWidgets.QProgressBar = QtWidgets.QProgressBar()
        self.progress_bar.setValue(0)

        # Assemble
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(output_header)
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
        dark_palette.setColor(
            QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255)
        )
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

    def _set_buttons_enabled(self, enabled: bool) -> None:
        """Enable/disable create button; toggle cancel button label."""
        self.create_button.setEnabled(enabled)
        self.cancel_button.setText("Cancel" if enabled else "Abort")

    def _browse_dir(self) -> None:
        """Open a folder picker and update the output dir field."""
        chosen = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select output directory", self.dir_input.text()
        )
        if chosen:
            self.dir_input.setText(chosen)

    def _on_profile_changed(self, index: int) -> None:
        """Update the hint label when the selected profile changes."""
        _HINTS: dict[str, str] = {
            "basic": "Minimal Python project — main.py, tests, ruff, .gitignore.",
            "data": "Jupyter Notebook + pandas + matplotlib + seaborn.",
            "fastapi": "Async REST API with FastAPI, uvicorn, pytest + ASGI transport.",
            "fastapi-db": "FastAPI + async SQLAlchemy 2.0 + Alembic migrations + aiosqlite.",
            "flask": "Flask 3 app-factory pattern, Blueprint, pytest test_client.",
            "streamlit": "Interactive dashboard — pandas + plotly, file upload, charts.",
            "cli": "CLI tool with Click, subcommands scaffold, rich output.",
            "telegram": "Telegram bot via python-telegram-bot (async handlers).",
            "discord": "Discord.py bot with Cogs architecture and .env token.",
            "django": "Django project with settings split, apps/, Dockerfile.",
            "grpc": "gRPC service with proto scaffold, servicer, client stub.",
            "celery": "Celery worker + Redis broker, beat scheduler stub.",
            "ml": "ML project — sklearn/torch, data/, models/, notebooks/.",
            "scraper": "Web scraper — requests + BeautifulSoup + Playwright stub.",
            "pypi": "Publishable PyPI package — pyproject.toml, CHANGELOG, CI.",
            "langchain": "LangChain agent — chains, tools, prompts, .env vars.",
            "llama": "LlamaIndex RAG — indices, ingestion pipeline, ReActAgent.",
            "mcp": "MCP server (Anthropic) with FastMCP tools and resources.",
            "lambda": "AWS Lambda — SAM template, powertools Logger/Tracer, local invoke.",
            "pytest-plugin": "pytest plugin — fixture, hook, pytest11 entry point, hatchling build.",
        }
        profile = ALL_PROFILES[index]
        hint = _HINTS.get(profile.slug, "")
        deps = profile.deps
        if deps:
            hint += "\nPackages: " + ",  ".join(deps)
        else:
            hint += "\nPackages: (only dev/test tools)"
        self.profile_hint.setText(hint)

    def _on_cancel(self) -> None:
        """Abort running setup or close the window."""
        if self._setup_running:
            self._cancel_event.set()
            self.output_signal.emit("INFO: Cancellation requested...")
        else:
            self.close()

    def create_project(self) -> None:
        """Start the project creation process."""
        self.project_name = self.name_input.text().strip()
        self.project_type = self.type_combo.currentIndex() + 1

        if not self.project_name:
            QtWidgets.QMessageBox.warning(
                self, "Input Error", "Please enter a project name."
            )
            return
        if _INVALID_NAME_RE.search(self.project_name) or ".." in self.project_name:
            QtWidgets.QMessageBox.warning(
                self,
                "Input Error",
                'Project name contains invalid characters (\\/:*?"<>| or ..).',
            )
            return

        self._cancel_event.clear()
        self._setup_running = True
        self.buttons_signal.emit(False)
        self.progress_bar.setValue(0)
        self.output_text.clear()

        threading.Thread(target=self.run_setup, daemon=True).start()

    def run_setup(self) -> None:
        """Execute the project setup process via SetupService."""
        service = SetupService(
            project_name=self.project_name,
            profile_index=self.project_type - 1,
            on_message=self.output_signal.emit,
            on_progress=self.progress_signal.emit,
            cancel_event=self._cancel_event,
            base_path=self.dir_input.text().strip() or None,
            open_editor=self.open_editor_check.isChecked(),
        )
        try:
            service.run()
        finally:
            self._setup_running = False
            self.buttons_signal.emit(True)


def main() -> None:
    app: QtWidgets.QApplication = QtWidgets.QApplication(
        sys.argv + ["-platform", "windows:darkmode=1"]
    )
    window: ProjectSetupApp = ProjectSetupApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
