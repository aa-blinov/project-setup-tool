import pytest
from app import _INVALID_NAME_RE


@pytest.mark.parametrize(
    "name",
    [
        "my-project",
        "my_project",
        "MyProject123",
        "project",
        "a",
    ],
)
def test_valid_project_names(name):
    assert not _INVALID_NAME_RE.search(name) and ".." not in name


@pytest.mark.parametrize(
    "name",
    [
        "my/project",
        "my\\project",
        "my:project",
        "my*project",
        "my?project",
        'my"project',
        "my<project",
        "my>project",
        "my|project",
        "../project",
        "project/../other",
        "../../etc/passwd",
    ],
)
def test_invalid_project_names(name):
    assert _INVALID_NAME_RE.search(name) or ".." in name
