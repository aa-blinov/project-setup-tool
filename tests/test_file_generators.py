import json
from generators import (
    create_ruff_config,
    create_requirements,
    create_readme,
    create_docker_files,
    setup_vscode,
)


class TestCreateRuffConfig:
    def test_creates_file(self, tmp_path):
        create_ruff_config(str(tmp_path))
        assert (tmp_path / "ruff.toml").exists()

    def test_content(self, tmp_path):
        create_ruff_config(str(tmp_path))
        content = (tmp_path / "ruff.toml").read_text()
        assert "line-length = 88" in content
        assert "[lint]" in content
        assert 'select = ["E", "F", "W", "B", "C"]' in content

    def test_no_tool_ruff_wrapper(self, tmp_path):
        # ruff.toml must not use [tool.ruff] — that's pyproject.toml syntax
        create_ruff_config(str(tmp_path))
        content = (tmp_path / "ruff.toml").read_text()
        assert "[tool.ruff]" not in content


class TestCreateRequirements:
    def test_creates_file(self, tmp_path):
        create_requirements(str(tmp_path), ["pytest", "requests"])
        assert (tmp_path / "requirements.txt").exists()

    def test_all_packages_present(self, tmp_path):
        packages = ["pytest", "requests", "fastapi"]
        create_requirements(str(tmp_path), packages)
        content = (tmp_path / "requirements.txt").read_text()
        for pkg in packages:
            assert pkg in content

    def test_newline_separated(self, tmp_path):
        create_requirements(str(tmp_path), ["a", "b", "c"])
        lines = (tmp_path / "requirements.txt").read_text().splitlines()
        assert lines == ["a", "b", "c"]


class TestCreateReadme:
    def test_creates_file(self, tmp_path):
        create_readme(str(tmp_path), "test-project", "python app/main.py")
        assert (tmp_path / "README.md").exists()

    def test_contains_project_name(self, tmp_path):
        create_readme(str(tmp_path), "test-project", "python app/main.py")
        content = (tmp_path / "README.md").read_text()
        assert "test-project" in content

    def test_fastapi_docker_port(self, tmp_path):
        create_readme(str(tmp_path), "test-project", "uvicorn app.main:app --reload")
        content = (tmp_path / "README.md").read_text()
        assert "8000" in content

    def test_jupyter_docker_port(self, tmp_path):
        create_readme(
            str(tmp_path), "test-project", "jupyter notebook notebooks/analysis.ipynb"
        )
        content = (tmp_path / "README.md").read_text()
        assert "8888" in content

    def test_basic_docker_run(self, tmp_path):
        create_readme(str(tmp_path), "test-project", "python app/main.py")
        content = (tmp_path / "README.md").read_text()
        assert "docker run --rm" in content


class TestCreateDockerFiles:
    def test_creates_both_files(self, tmp_path):
        create_docker_files(str(tmp_path), "python app/main.py")
        assert (tmp_path / "Dockerfile").exists()
        assert (tmp_path / "docker-compose.yml").exists()

    def test_dockerfile_uses_uv(self, tmp_path):
        create_docker_files(str(tmp_path), "python app/main.py")
        content = (tmp_path / "Dockerfile").read_text()
        assert "uv" in content

    def test_dockerfile_cmd_array(self, tmp_path):
        create_docker_files(str(tmp_path), "python app/main.py")
        content = (tmp_path / "Dockerfile").read_text()
        assert 'CMD ["python", "app/main.py"]' in content

    def test_fastapi_compose_has_port(self, tmp_path):
        create_docker_files(
            str(tmp_path),
            "uvicorn app.main:app --host 0.0.0.0 --port 8000",
            is_fastapi=True,
        )
        content = (tmp_path / "docker-compose.yml").read_text()
        assert "8000" in content

    def test_data_project_uses_jupyter_image(self, tmp_path):
        create_docker_files(str(tmp_path), None, is_data_project=True)
        content = (tmp_path / "Dockerfile").read_text()
        assert "jupyter" in content

    def test_no_command_none_in_compose(self, tmp_path):
        create_docker_files(str(tmp_path), None)
        content = (tmp_path / "docker-compose.yml").read_text()
        assert "None" not in content


class TestSetupVscode:
    def test_creates_settings_file(self, tmp_path):
        setup_vscode(str(tmp_path))
        assert (tmp_path / ".vscode" / "settings.json").exists()

    def test_settings_are_valid_json(self, tmp_path):
        setup_vscode(str(tmp_path))
        settings = json.loads((tmp_path / ".vscode" / "settings.json").read_text())
        assert isinstance(settings, dict)

    def test_required_keys(self, tmp_path):
        setup_vscode(str(tmp_path))
        settings = json.loads((tmp_path / ".vscode" / "settings.json").read_text())
        assert "python.defaultInterpreterPath" in settings
        assert settings["editor.formatOnSave"] is True
        assert settings["python.testing.pytestEnabled"] is True
        assert settings["ruff.enable"] is True

    def test_no_deprecated_keys(self, tmp_path):
        setup_vscode(str(tmp_path))
        settings = json.loads((tmp_path / ".vscode" / "settings.json").read_text())
        assert "python.pythonPath" not in settings
        assert "python.linting.enabled" not in settings
        assert "python.linting.ruffEnabled" not in settings
