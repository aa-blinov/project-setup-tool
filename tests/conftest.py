import sys
import threading
import pytest
from PyQt5 import QtWidgets
from app import ProjectSetupApp
from profiles import ProfileContext
from setup_service import SetupService


@pytest.fixture(scope="session")
def qt_app():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    yield app


@pytest.fixture
def widget(qt_app):
    w = ProjectSetupApp()
    w.project_name = "test-project"
    yield w
    w.close()


@pytest.fixture
def ctx():
    """Minimal ProfileContext for profile template tests."""
    return ProfileContext(project_name="test-project", emit=lambda msg: None)


@pytest.fixture
def service():
    """SetupService instance with a blank project_dir / venv_dir for unit tests."""
    s = SetupService(
        project_name="test-project",
        profile_index=0,
        on_message=lambda m: None,
        on_progress=lambda v: None,
        cancel_event=threading.Event(),
    )
    return s
