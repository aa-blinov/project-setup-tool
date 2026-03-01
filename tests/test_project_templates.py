import json
from profiles import BasicPythonProfile, DataAnalyticsProfile, FastAPIProfile


class TestBasicPythonProject:
    def test_directory_structure(self, ctx, tmp_path):
        BasicPythonProfile().setup(str(tmp_path), ctx)
        assert (tmp_path / "app" / "__init__.py").exists()
        assert (tmp_path / "app" / "main.py").exists()
        assert (tmp_path / "tests" / "test_basic.py").exists()
        assert (tmp_path / "requirements.txt").exists()
        assert (tmp_path / "README.md").exists()
        assert (tmp_path / "Dockerfile").exists()
        assert (tmp_path / "docker-compose.yml").exists()

    def test_main_py_prints_hello(self, ctx, tmp_path):
        BasicPythonProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "app" / "main.py").read_text()
        assert "Hello, World!" in content

    def test_test_file_is_runnable(self, ctx, tmp_path):
        BasicPythonProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "tests" / "test_basic.py").read_text()
        assert "def test_" in content
        assert "assert" in content

    def test_requirements_includes_base_packages(self, ctx, tmp_path):
        BasicPythonProfile().setup(str(tmp_path), ctx)
        lines = (tmp_path / "requirements.txt").read_text().splitlines()
        assert any(line.startswith("pytest") for line in lines)


class TestDataAnalyticsProject:
    def test_directory_structure(self, ctx, tmp_path):
        DataAnalyticsProfile().setup(str(tmp_path), ctx)
        assert (tmp_path / "notebooks" / "analysis.ipynb").exists()
        assert (tmp_path / "tests" / "test_notebook.py").exists()
        assert (tmp_path / "requirements.txt").exists()
        assert (tmp_path / "README.md").exists()

    def test_notebook_is_valid_json(self, ctx, tmp_path):
        DataAnalyticsProfile().setup(str(tmp_path), ctx)
        notebook = json.loads((tmp_path / "notebooks" / "analysis.ipynb").read_text())
        assert isinstance(notebook, dict)

    def test_notebook_format_version(self, ctx, tmp_path):
        DataAnalyticsProfile().setup(str(tmp_path), ctx)
        notebook = json.loads((tmp_path / "notebooks" / "analysis.ipynb").read_text())
        assert notebook["nbformat"] == 4

    def test_requirements_includes_jupyter(self, ctx, tmp_path):
        DataAnalyticsProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "requirements.txt").read_text()
        assert "jupyter" in content
        assert "pytest" in content


class TestFastapiProject:
    def test_directory_structure(self, ctx, tmp_path):
        FastAPIProfile().setup(str(tmp_path), ctx)
        assert (tmp_path / "app" / "__init__.py").exists()
        assert (tmp_path / "app" / "main.py").exists()
        assert (tmp_path / "tests" / "test_app.py").exists()
        assert (tmp_path / "requirements.txt").exists()
        assert (tmp_path / "README.md").exists()
        assert (tmp_path / "Dockerfile").exists()
        assert (tmp_path / "docker-compose.yml").exists()

    def test_main_has_fastapi_import(self, ctx, tmp_path):
        FastAPIProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "app" / "main.py").read_text()
        assert "from fastapi import FastAPI" in content

    def test_main_has_root_endpoint(self, ctx, tmp_path):
        FastAPIProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "app" / "main.py").read_text()
        assert '@app.get("/")' in content

    def test_test_file_uses_asgi_transport(self, ctx, tmp_path):
        FastAPIProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "tests" / "test_app.py").read_text()
        assert "ASGITransport" in content

    def test_requirements_includes_fastapi(self, ctx, tmp_path):
        FastAPIProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "requirements.txt").read_text()
        assert "fastapi" in content
        assert "uvicorn" in content

    def test_compose_exposes_port_8000(self, ctx, tmp_path):
        FastAPIProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "docker-compose.yml").read_text()
        assert "8000" in content
