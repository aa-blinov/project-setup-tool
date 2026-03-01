import os
import pytest
from unittest.mock import patch, MagicMock


class TestDownloadGitignore:
    def test_success_writes_file(self, service, tmp_path):
        service._project_dir = str(tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "*.pyc\n__pycache__/\n.env\n"
        with patch("setup_service.requests.get", return_value=mock_response):
            service._download_gitignore()
        assert (tmp_path / ".gitignore").exists()
        assert "*.pyc" in (tmp_path / ".gitignore").read_text()

    def test_timeout_is_set(self, service, tmp_path):
        service._project_dir = str(tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "*.pyc\n"
        with patch(
            "setup_service.requests.get", return_value=mock_response
        ) as mock_get:
            service._download_gitignore()
        _args, kwargs = mock_get.call_args
        assert "timeout" in kwargs

    def test_http_failure_raises(self, service, tmp_path):
        service._project_dir = str(tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 404
        with patch("setup_service.requests.get", return_value=mock_response):
            with pytest.raises(Exception, match="[Ff]ailed"):
                service._download_gitignore()


class TestInitGit:
    def test_runs_git_init(self, service, tmp_path):
        service._project_dir = str(tmp_path)
        mock_result = MagicMock(returncode=0, stdout="Initialized empty Git repository")
        with patch(
            "setup_service.subprocess.run", return_value=mock_result
        ) as mock_run:
            service._init_git()
        cmd = mock_run.call_args[0][0]
        assert cmd == ["git", "init"]

    def test_uses_correct_cwd(self, service, tmp_path):
        service._project_dir = str(tmp_path)
        mock_result = MagicMock(returncode=0, stdout="")
        with patch(
            "setup_service.subprocess.run", return_value=mock_result
        ) as mock_run:
            service._init_git()
        kwargs = mock_run.call_args[1]
        assert kwargs.get("cwd") == str(tmp_path)

    def test_capture_output(self, service, tmp_path):
        service._project_dir = str(tmp_path)
        mock_result = MagicMock(returncode=0, stdout="")
        with patch(
            "setup_service.subprocess.run", return_value=mock_result
        ) as mock_run:
            service._init_git()
        kwargs = mock_run.call_args[1]
        assert kwargs.get("capture_output") is True
        assert kwargs.get("text") is True


class TestInstallDependencies:
    def _make_venv(self, tmp_path):
        """Create a minimal venv structure so the method can locate the Python binary."""
        venv_dir = tmp_path / ".venv"
        if os.name == "nt":
            bin_dir = venv_dir / "Scripts"
            python_bin = bin_dir / "python.exe"
        else:
            bin_dir = venv_dir / "bin"
            python_bin = bin_dir / "python"
        bin_dir.mkdir(parents=True)
        python_bin.touch()
        return str(venv_dir), str(python_bin)

    def test_calls_uv_pip_install(self, service, tmp_path):
        venv_dir, _python_bin = self._make_venv(tmp_path)
        service._project_dir = str(tmp_path)
        service._venv_dir = venv_dir
        mock_result = MagicMock(stderr="")
        with patch(
            "setup_service.subprocess.run", return_value=mock_result
        ) as mock_run:
            service._install_dependencies()
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "uv"
        assert "pip" in cmd
        assert "install" in cmd

    def test_passes_python_binary_not_venv_dir(self, service, tmp_path):
        venv_dir, python_bin = self._make_venv(tmp_path)
        service._project_dir = str(tmp_path)
        service._venv_dir = venv_dir
        mock_result = MagicMock(stderr="")
        with patch(
            "setup_service.subprocess.run", return_value=mock_result
        ) as mock_run:
            service._install_dependencies()
        cmd = mock_run.call_args[0][0]
        python_arg_index = cmd.index("--python") + 1
        passed = cmd[python_arg_index]
        assert passed == python_bin, (
            "Should pass the Python executable, not the venv directory"
        )

    def test_installs_requirements_txt(self, service, tmp_path):
        venv_dir, _ = self._make_venv(tmp_path)
        service._project_dir = str(tmp_path)
        service._venv_dir = venv_dir
        (tmp_path / "requirements.txt").write_text("pytest\n")
        mock_result = MagicMock(stderr="")
        with patch(
            "setup_service.subprocess.run", return_value=mock_result
        ) as mock_run:
            service._install_dependencies()
        cmd = mock_run.call_args[0][0]
        assert "-r" in cmd
        assert "requirements.txt" in cmd

    def test_capture_output(self, service, tmp_path):
        venv_dir, _ = self._make_venv(tmp_path)
        service._project_dir = str(tmp_path)
        service._venv_dir = venv_dir
        mock_result = MagicMock(stderr="")
        with patch(
            "setup_service.subprocess.run", return_value=mock_result
        ) as mock_run:
            service._install_dependencies()
        kwargs = mock_run.call_args[1]
        assert kwargs.get("capture_output") is True
        assert kwargs.get("text") is True
