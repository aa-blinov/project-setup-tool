"""Editor auto-open with system file-explorer fallback."""

from __future__ import annotations

import os
import platform
import subprocess

VSCODE_PATH: str = os.environ.get(
    "VSCODE_PATH", r"C:\Program Files\Microsoft VS Code\Code.exe"
)

_CANDIDATES: list[str] = [
    "code",  # VS Code stable
    "code-insiders",  # VS Code Insiders
    "cursor",  # Cursor AI editor
    "windsurf",  # Windsurf (Codeium)
    "codium",  # VSCodium
    "code-oss",  # VS Code OSS (Linux)
    VSCODE_PATH,  # explicit path from env
]


def open_in_editor(project_dir: str) -> tuple[bool, str]:
    """Try to open *project_dir* in a code editor; fall back to the system file explorer.

    Returns ``(success, message)`` where *success* is ``True`` when the directory
    was opened (either in an editor or the file explorer).
    """
    for executable in _CANDIDATES:
        try:
            subprocess.Popen([executable, project_dir])
            return True, f"SUCCESS: Project opened in '{executable}'."
        except FileNotFoundError:
            continue

    try:
        system = platform.system()
        if system == "Windows":
            subprocess.Popen(["explorer", project_dir])
        elif system == "Darwin":
            subprocess.Popen(["open", project_dir])
        else:
            subprocess.Popen(["xdg-open", project_dir])
        return True, (
            "INFO: No supported editor found — project opened in file explorer. "
            "Install VS Code, Cursor, or Windsurf to open it in an editor automatically."
        )
    except Exception:
        return False, (
            "ERROR: No supported editor found. Install VS Code, Cursor, Windsurf or "
            "set VSCODE_PATH to the editor executable."
        )
