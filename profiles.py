"""Project profile definitions.

Each profile encapsulates the file structure and dependencies for a specific
type of Python project.  To add a new profile, subclass ``BaseProfile`` and
append it to ``ALL_PROFILES``.
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

from generators import (
    create_readme as _gen_readme,
    create_docker_files as _gen_docker,
    create_requirements as _gen_reqs,
)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_BASE_TEST_DEPS: list[str] = [
    "pytest",
    "pytest-cov",
    "pytest-mock",
    "pytest-xdist",
    "pytest-asyncio",
    "pytest-profiling",
]


def _write(project_dir: str, relative_path: str, content: str) -> None:
    """Write *content* to *relative_path* inside *project_dir*, creating parents."""
    full = os.path.join(project_dir, *relative_path.split("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)


# ---------------------------------------------------------------------------
# Context & base class
# ---------------------------------------------------------------------------


@dataclass
class ProfileContext:
    """Shared state passed to each profile's ``setup``.  Helper methods delegate
    to the pure functions in ``generators.py`` so profiles and tests never
    depend on the Qt widget.
    """

    project_name: str
    emit: Callable[[str], None]

    def create_readme(self, project_dir: str, run_command: str) -> None:
        _gen_readme(project_dir, self.project_name, run_command)

    def create_docker_files(
        self,
        project_dir: str,
        command: str | None,
        is_data_project: bool = False,
        is_fastapi: bool = False,
    ) -> None:
        _gen_docker(
            project_dir, command, is_data_project=is_data_project, is_fastapi=is_fastapi
        )

    def create_requirements(self, project_dir: str, packages: list) -> None:
        _gen_reqs(project_dir, packages)


class BaseProfile(ABC):
    """Abstract base for a project profile."""

    label: str  # shown in the combo box
    slug: str  # short keyword for CLI, e.g. "fastapi", "django"
    deps: list[
        str
    ] = []  # runtime packages (shown in GUI; test deps added automatically)

    @abstractmethod
    def setup(self, project_dir: str, ctx: ProfileContext) -> None: ...


# ---------------------------------------------------------------------------
# Existing profiles
# ---------------------------------------------------------------------------


class BasicPythonProfile(BaseProfile):
    label = "Basic Python Project"
    slug = "basic"
    deps = []

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        _write(project_dir, "app/__init__.py", "")
        _write(
            project_dir,
            "app/main.py",
            'def main() -> None:\n    print("Hello, World!")\n\n\nif __name__ == "__main__":\n    main()\n',
        )
        _write(project_dir, "tests/__init__.py", "")
        _write(
            project_dir, "tests/test_basic.py", "def test_true():\n    assert True\n"
        )
        ctx.create_readme(project_dir, "python app/main.py")
        ctx.create_docker_files(project_dir, "python app/main.py")
        ctx.create_requirements(project_dir, self.deps + _BASE_TEST_DEPS)
        ctx.emit("SUCCESS: Basic Python project set up.")


class DataAnalyticsProfile(BaseProfile):
    label = "Data Analytics Project"
    slug = "data"
    deps = ["jupyter", "pandas", "numpy", "matplotlib"]

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        os.makedirs(os.path.join(project_dir, "data"), exist_ok=True)
        notebook_content = {
            "cells": [
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "import pandas as pd\nimport matplotlib.pyplot as plt\n"
                    ],
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3",
                }
            },
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        nb_path = os.path.join(project_dir, "notebooks", "analysis.ipynb")
        os.makedirs(os.path.dirname(nb_path), exist_ok=True)
        with open(nb_path, "w", encoding="utf-8") as f:
            json.dump(notebook_content, f, indent=2)

        _write(project_dir, "tests/__init__.py", "")
        _write(
            project_dir, "tests/test_notebook.py", "def test_true():\n    assert True\n"
        )
        ctx.create_readme(project_dir, "jupyter notebook notebooks/analysis.ipynb")
        ctx.create_docker_files(project_dir, None, is_data_project=True)
        ctx.create_requirements(project_dir, self.deps + _BASE_TEST_DEPS)
        ctx.emit("SUCCESS: Data Analytics project set up.")


class FastAPIProfile(BaseProfile):
    label = "FastAPI Project"
    slug = "fastapi"
    deps = ["fastapi", "uvicorn", "httpx"]

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        _write(project_dir, "app/__init__.py", "")
        _write(
            project_dir,
            "app/main.py",
            'from fastapi import FastAPI\n\napp = FastAPI()\n\n\n@app.get("/")\nasync def read_root():\n    return {"Hello": "World"}\n',
        )
        _write(project_dir, "tests/__init__.py", "")
        _write(
            project_dir,
            "tests/test_app.py",
            "import pytest\n"
            "from httpx import AsyncClient, ASGITransport\n"
            "from app.main import app\n"
            "\n"
            "\n"
            "@pytest.mark.asyncio\n"
            "async def test_read_root():\n"
            '    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:\n'
            '        response = await ac.get("/")\n'
            "    assert response.status_code == 200\n"
            '    assert response.json() == {"Hello": "World"}\n',
        )
        ctx.create_readme(project_dir, "uvicorn app.main:app --reload")
        ctx.create_docker_files(
            project_dir,
            "uvicorn app.main:app --host 0.0.0.0 --port 8000",
            is_fastapi=True,
        )
        ctx.create_requirements(project_dir, self.deps + _BASE_TEST_DEPS)
        ctx.emit("SUCCESS: FastAPI project set up.")


# ---------------------------------------------------------------------------
# New profiles
# ---------------------------------------------------------------------------


class CLIToolProfile(BaseProfile):
    label = "CLI Tool (Typer)"
    slug = "cli"
    deps = ["typer", "rich"]

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        _write(project_dir, "app/__init__.py", "")
        _write(
            project_dir,
            "app/main.py",
            "import typer\n"
            "from rich.console import Console\n"
            "\n"
            "app = typer.Typer()\n"
            "console = Console()\n"
            "\n"
            "\n"
            "@app.command()\n"
            'def main(name: str = typer.Argument("World", help="Name to greet")) -> None:\n'
            '    """Greet someone."""\n'
            '    console.print(f"[bold green]Hello, {name}![/bold green]")\n'
            "\n"
            "\n"
            'if __name__ == "__main__":\n'
            "    app()\n",
        )
        _write(project_dir, "tests/__init__.py", "")
        _write(
            project_dir,
            "tests/test_cli.py",
            "from typer.testing import CliRunner\n"
            "from app.main import app\n"
            "\n"
            "runner = CliRunner()\n"
            "\n"
            "\n"
            "def test_main_no_args():\n"
            "    result = runner.invoke(app, [])\n"
            "    assert result.exit_code == 0\n"
            '    assert "Hello" in result.output\n'
            "\n"
            "\n"
            "def test_main_with_name():\n"
            '    result = runner.invoke(app, ["Alice"])\n'
            "    assert result.exit_code == 0\n"
            '    assert "Alice" in result.output\n',
        )
        ctx.create_readme(project_dir, "python app/main.py --help")
        ctx.create_docker_files(project_dir, "python app/main.py")
        ctx.create_requirements(project_dir, self.deps + _BASE_TEST_DEPS)
        ctx.emit("SUCCESS: CLI Tool project set up.")


class TelegramBotProfile(BaseProfile):
    label = "Telegram Bot (aiogram 3)"
    slug = "telegram"
    deps = ["aiogram", "python-dotenv"]

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        _write(project_dir, "bot/__init__.py", "")
        _write(
            project_dir,
            "bot/main.py",
            "import asyncio\n"
            "import os\n"
            "from aiogram import Bot, Dispatcher\n"
            "from bot.handlers import common\n"
            "from dotenv import load_dotenv\n"
            "\n"
            "load_dotenv()\n"
            "\n"
            "\n"
            "async def main() -> None:\n"
            '    bot = Bot(token=os.environ["BOT_TOKEN"])\n'
            "    dp = Dispatcher()\n"
            "    dp.include_router(common.router)\n"
            "    await dp.start_polling(bot)\n"
            "\n"
            "\n"
            'if __name__ == "__main__":\n'
            "    asyncio.run(main())\n",
        )
        _write(project_dir, "bot/handlers/__init__.py", "")
        _write(
            project_dir,
            "bot/handlers/common.py",
            "from aiogram import Router\n"
            "from aiogram.filters import CommandStart\n"
            "from aiogram.types import Message\n"
            "\n"
            "router = Router()\n"
            "\n"
            "\n"
            "@router.message(CommandStart())\n"
            "async def cmd_start(message: Message) -> None:\n"
            '    await message.answer("Hello! I am your bot.")\n',
        )
        _write(project_dir, "tests/__init__.py", "")
        _write(
            project_dir, "tests/test_handlers.py", "def test_true():\n    assert True\n"
        )
        _write(project_dir, ".env.example", "BOT_TOKEN=your_token_here\n")
        _write(
            project_dir,
            "Dockerfile",
            "FROM python:3.12-slim\n"
            "COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv\n"
            "WORKDIR /app\n"
            "COPY requirements.txt .\n"
            "RUN uv pip install --system --no-cache -r requirements.txt\n"
            "COPY . .\n"
            'CMD ["python", "bot/main.py"]\n',
        )
        _write(
            project_dir,
            "docker-compose.yml",
            "services:\n"
            "  bot:\n"
            "    build: .\n"
            "    env_file: .env\n"
            "    restart: unless-stopped\n",
        )
        ctx.create_readme(project_dir, "python bot/main.py")
        ctx.create_requirements(project_dir, self.deps + _BASE_TEST_DEPS)
        ctx.emit("SUCCESS: Telegram Bot project set up.")


class DjangoProfile(BaseProfile):
    label = "Django Web App"
    slug = "django"
    deps = ["django", "gunicorn", "python-dotenv", "pytest-django"]

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        _write(
            project_dir,
            "manage.py",
            "#!/usr/bin/env python\n"
            '"""Django command-line utility for administrative tasks."""\n'
            "import os\n"
            "import sys\n"
            "\n"
            "\n"
            "def main():\n"
            '    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")\n'
            "    from django.core.management import execute_from_command_line\n"
            "    execute_from_command_line(sys.argv)\n"
            "\n"
            "\n"
            'if __name__ == "__main__":\n'
            "    main()\n",
        )
        _write(project_dir, "config/__init__.py", "")
        _write(
            project_dir,
            "config/settings.py",
            "import os\n"
            "from pathlib import Path\n"
            "from dotenv import load_dotenv\n"
            "\n"
            "load_dotenv()\n"
            "\n"
            "BASE_DIR = Path(__file__).resolve().parent.parent\n"
            'SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")\n'
            'DEBUG = os.environ.get("DEBUG", "True") == "True"\n'
            'ALLOWED_HOSTS = ["*"]\n'
            "\n"
            "INSTALLED_APPS = [\n"
            '    "django.contrib.admin",\n'
            '    "django.contrib.auth",\n'
            '    "django.contrib.contenttypes",\n'
            '    "django.contrib.sessions",\n'
            '    "django.contrib.messages",\n'
            '    "django.contrib.staticfiles",\n'
            '    "apps.core",\n'
            "]\n"
            "\n"
            "MIDDLEWARE = [\n"
            '    "django.middleware.security.SecurityMiddleware",\n'
            '    "django.contrib.sessions.middleware.SessionMiddleware",\n'
            '    "django.middleware.common.CommonMiddleware",\n'
            '    "django.middleware.csrf.CsrfViewMiddleware",\n'
            '    "django.contrib.auth.middleware.AuthenticationMiddleware",\n'
            '    "django.contrib.messages.middleware.MessageMiddleware",\n'
            '    "django.middleware.clickjacking.XFrameOptionsMiddleware",\n'
            "]\n"
            "\n"
            'ROOT_URLCONF = "config.urls"\n'
            "\n"
            "DATABASES = {\n"
            '    "default": {\n'
            '        "ENGINE": "django.db.backends.sqlite3",\n'
            '        "NAME": BASE_DIR / "db.sqlite3",\n'
            "    }\n"
            "}\n"
            "\n"
            'STATIC_URL = "/static/"\n'
            'WSGI_APPLICATION = "config.wsgi.application"\n',
        )
        _write(
            project_dir,
            "config/urls.py",
            "from django.contrib import admin\n"
            "from django.urls import path, include\n"
            "\n"
            "urlpatterns = [\n"
            '    path("admin/", admin.site.urls),\n'
            '    path("", include("apps.core.urls")),\n'
            "]\n",
        )
        _write(
            project_dir,
            "config/wsgi.py",
            "import os\n"
            "from django.core.wsgi import get_wsgi_application\n"
            '\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")\n'
            "application = get_wsgi_application()\n",
        )
        _write(project_dir, "apps/__init__.py", "")
        _write(project_dir, "apps/core/__init__.py", "")
        _write(
            project_dir,
            "apps/core/views.py",
            "from django.http import HttpResponse\n"
            "\n"
            "\n"
            "def index(request):\n"
            '    return HttpResponse("Hello, World!")\n',
        )
        _write(
            project_dir,
            "apps/core/urls.py",
            "from django.urls import path\n"
            "from . import views\n"
            "\n"
            "urlpatterns = [\n"
            '    path("", views.index, name="index"),\n'
            "]\n",
        )
        os.makedirs(os.path.join(project_dir, "static"), exist_ok=True)
        _write(project_dir, "tests/__init__.py", "")
        _write(
            project_dir,
            "tests/test_views.py",
            "import pytest\n"
            "\n"
            "\n"
            "@pytest.mark.django_db\n"
            "def test_index(client):\n"
            '    response = client.get("/")\n'
            "    assert response.status_code == 200\n",
        )
        _write(
            project_dir,
            ".env.example",
            "SECRET_KEY=change-me-in-production\n"
            "DEBUG=True\n"
            "DATABASE_URL=sqlite:///db.sqlite3\n",
        )
        ctx.create_readme(project_dir, "python manage.py runserver")
        ctx.create_docker_files(
            project_dir,
            "gunicorn config.wsgi:application --bind 0.0.0.0:8000",
            is_fastapi=True,  # reuse port-8000 flag
        )
        ctx.create_requirements(project_dir, self.deps + _BASE_TEST_DEPS)
        ctx.emit("SUCCESS: Django Web App project set up.")


class GRPCServiceProfile(BaseProfile):
    label = "gRPC Service"
    slug = "grpc"
    deps = ["grpcio", "grpcio-tools", "protobuf"]

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        _write(
            project_dir,
            "proto/service.proto",
            'syntax = "proto3";\n'
            "\n"
            "package service;\n"
            "\n"
            "service Greeter {\n"
            "  rpc SayHello (HelloRequest) returns (HelloReply);\n"
            "}\n"
            "\n"
            "message HelloRequest {\n"
            "  string name = 1;\n"
            "}\n"
            "\n"
            "message HelloReply {\n"
            "  string message = 1;\n"
            "}\n",
        )
        _write(project_dir, "app/__init__.py", "")
        _write(project_dir, "app/generated/__init__.py", "")
        _write(
            project_dir,
            "app/server.py",
            "import grpc\n"
            "from concurrent import futures\n"
            "# from app.generated import service_pb2, service_pb2_grpc  # uncomment after `make proto`\n"
            "\n"
            "\n"
            "def serve() -> None:\n"
            "    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))\n"
            '    server.add_insecure_port("[::]:50051")\n'
            "    server.start()\n"
            '    print("gRPC server listening on :50051")\n'
            "    server.wait_for_termination()\n"
            "\n"
            "\n"
            'if __name__ == "__main__":\n'
            "    serve()\n",
        )
        _write(project_dir, "tests/__init__.py", "")
        _write(
            project_dir, "tests/test_service.py", "def test_true():\n    assert True\n"
        )
        _write(
            project_dir,
            "Makefile",
            "proto:\n"
            "\tpython -m grpc_tools.protoc -I proto"
            " --python_out=app/generated"
            " --grpc_python_out=app/generated"
            " proto/service.proto\n",
        )
        ctx.create_readme(project_dir, "python app/server.py")
        ctx.create_docker_files(project_dir, "python app/server.py")
        ctx.create_requirements(project_dir, self.deps + _BASE_TEST_DEPS)
        ctx.emit("SUCCESS: gRPC Service project set up.")


class CeleryWorkerProfile(BaseProfile):
    label = "Celery Worker"
    slug = "celery"
    deps = ["celery", "redis", "python-dotenv"]

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        _write(project_dir, "app/__init__.py", "")
        _write(
            project_dir,
            "app/celery.py",
            "import os\n"
            "from celery import Celery\n"
            "from dotenv import load_dotenv\n"
            "\n"
            "load_dotenv()\n"
            "\n"
            f"app = Celery(\n"
            f'    "{ctx.project_name}",\n'
            '    broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),\n'
            '    backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),\n'
            ")\n"
            '\napp.autodiscover_tasks(["app.tasks"])\n',
        )
        _write(project_dir, "app/tasks/__init__.py", "")
        _write(
            project_dir,
            "app/tasks/example.py",
            "from app.celery import app\n"
            "\n"
            "\n"
            "@app.task\n"
            "def add(x: int, y: int) -> int:\n"
            "    return x + y\n",
        )
        _write(project_dir, "tests/__init__.py", "")
        _write(
            project_dir,
            "tests/test_tasks.py",
            "from app.tasks.example import add\n"
            "\n"
            "\n"
            "def test_add():\n"
            "    result = add.apply(args=[3, 4])\n"
            "    assert result.get() == 7\n",
        )
        _write(
            project_dir,
            ".env.example",
            "CELERY_BROKER_URL=redis://localhost:6379/0\n"
            "CELERY_RESULT_BACKEND=redis://localhost:6379/0\n",
        )
        _write(
            project_dir,
            "Dockerfile",
            "FROM python:3.12-slim\n"
            "COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv\n"
            "WORKDIR /app\n"
            "COPY requirements.txt .\n"
            "RUN uv pip install --system --no-cache -r requirements.txt\n"
            "COPY . .\n"
            'CMD ["celery", "-A", "app.celery", "worker", "--loglevel=info"]\n',
        )
        _write(
            project_dir,
            "docker-compose.yml",
            "services:\n"
            "  redis:\n"
            "    image: redis:7-alpine\n"
            "    ports:\n"
            '      - "6379:6379"\n'
            "  worker:\n"
            "    build: .\n"
            "    env_file: .env\n"
            "    command: celery -A app.celery worker --loglevel=info\n"
            "    depends_on:\n"
            "      - redis\n",
        )
        ctx.create_readme(project_dir, "celery -A app.celery worker --loglevel=info")
        ctx.create_requirements(project_dir, self.deps + _BASE_TEST_DEPS)
        ctx.emit("SUCCESS: Celery Worker project set up.")


class MLProjectProfile(BaseProfile):
    label = "ML Project (scikit-learn)"
    slug = "ml"
    deps = ["scikit-learn", "pandas", "numpy", "matplotlib", "jupyter", "mlflow"]

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        for d in ["data/raw", "data/processed", "models", "tests"]:
            os.makedirs(os.path.join(project_dir, d), exist_ok=True)

        notebook_content = {
            "cells": [
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "import pandas as pd\n",
                        "import numpy as np\n",
                        "import matplotlib.pyplot as plt\n",
                        "\n",
                        "# df = pd.read_csv('../data/raw/dataset.csv')\n",
                    ],
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3",
                }
            },
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        nb_path = os.path.join(project_dir, "notebooks", "exploration.ipynb")
        os.makedirs(os.path.dirname(nb_path), exist_ok=True)
        with open(nb_path, "w", encoding="utf-8") as f:
            json.dump(notebook_content, f, indent=2)

        _write(project_dir, "src/__init__.py", "")
        _write(
            project_dir,
            "src/train.py",
            "import pickle\n"
            "from pathlib import Path\n"
            "from sklearn.datasets import load_iris\n"
            "from sklearn.ensemble import RandomForestClassifier\n"
            "from sklearn.model_selection import train_test_split\n"
            "from sklearn.metrics import accuracy_score\n"
            "\n"
            "\n"
            "def train() -> None:\n"
            "    X, y = load_iris(return_X_y=True)\n"
            "    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n"
            "    model = RandomForestClassifier(n_estimators=100, random_state=42)\n"
            "    model.fit(X_train, y_train)\n"
            "    score = accuracy_score(y_test, model.predict(X_test))\n"
            '    print(f"Accuracy: {score:.3f}")\n'
            '    Path("models").mkdir(exist_ok=True)\n'
            '    with open("models/model.pkl", "wb") as f:\n'
            "        pickle.dump(model, f)\n"
            "\n"
            "\n"
            'if __name__ == "__main__":\n'
            "    train()\n",
        )
        _write(
            project_dir,
            "src/evaluate.py",
            "import pickle\n"
            "from sklearn.datasets import load_iris\n"
            "from sklearn.model_selection import train_test_split\n"
            "from sklearn.metrics import classification_report\n"
            "\n"
            "\n"
            "def evaluate() -> None:\n"
            '    with open("models/model.pkl", "rb") as f:\n'
            "        model = pickle.load(f)\n"
            "    X, y = load_iris(return_X_y=True)\n"
            "    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n"
            "    print(classification_report(y_test, model.predict(X_test)))\n"
            "\n"
            "\n"
            'if __name__ == "__main__":\n'
            "    evaluate()\n",
        )
        _write(project_dir, "tests/__init__.py", "")
        _write(
            project_dir, "tests/test_model.py", "def test_true():\n    assert True\n"
        )
        ctx.create_readme(project_dir, "python src/train.py")
        ctx.create_docker_files(project_dir, None, is_data_project=True)
        ctx.create_requirements(project_dir, self.deps + _BASE_TEST_DEPS)
        ctx.emit("SUCCESS: ML Project set up.")


class ScraperProfile(BaseProfile):
    label = "Web Scraper (httpx + BS4)"
    slug = "scraper"
    deps = ["httpx", "beautifulsoup4", "lxml"]

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        os.makedirs(os.path.join(project_dir, "data"), exist_ok=True)
        _write(project_dir, "app/__init__.py", "")
        _write(
            project_dir,
            "app/scraper.py",
            "import httpx\n"
            "from bs4 import BeautifulSoup\n"
            "\n"
            "\n"
            "def fetch(url: str) -> BeautifulSoup:\n"
            '    """Fetch a page and return a parsed BeautifulSoup object."""\n'
            "    response = httpx.get(url, timeout=10, follow_redirects=True)\n"
            "    response.raise_for_status()\n"
            '    return BeautifulSoup(response.text, "lxml")\n',
        )
        _write(project_dir, "app/parsers/__init__.py", "")
        _write(project_dir, "tests/__init__.py", "")
        _write(
            project_dir,
            "tests/test_scraper.py",
            "from unittest.mock import patch, MagicMock\n"
            "from app.scraper import fetch\n"
            "\n"
            "\n"
            "def test_fetch_parses_html():\n"
            "    mock_response = MagicMock()\n"
            '    mock_response.text = "<html><body><h1>Test</h1></body></html>"\n'
            "    mock_response.raise_for_status = lambda: None\n"
            '    with patch("app.scraper.httpx.get", return_value=mock_response):\n'
            '        soup = fetch("https://example.com")\n'
            '    assert soup.find("h1").text == "Test"\n',
        )
        ctx.create_readme(project_dir, "python app/scraper.py")
        ctx.create_docker_files(project_dir, "python app/scraper.py")
        ctx.create_requirements(project_dir, self.deps + _BASE_TEST_DEPS)
        ctx.emit("SUCCESS: Web Scraper project set up.")


class PyPIPackageProfile(BaseProfile):
    label = "PyPI Package"
    slug = "pypi"
    deps = ["build", "twine", "hatchling"]

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        pkg_name = ctx.project_name.replace("-", "_")
        _write(project_dir, f"src/{pkg_name}/__init__.py", '__version__ = "0.1.0"\n')
        _write(
            project_dir,
            f"src/{pkg_name}/main.py",
            'def greet(name: str = "World") -> str:\n'
            '    """Return a greeting string."""\n'
            '    return f"Hello, {name}!"\n',
        )
        _write(project_dir, "tests/__init__.py", "")
        _write(
            project_dir,
            "tests/test_main.py",
            f"from {pkg_name}.main import greet\n"
            "\n"
            "\n"
            "def test_greet_default():\n"
            '    assert greet() == "Hello, World!"\n'
            "\n"
            "\n"
            "def test_greet_with_name():\n"
            '    assert greet("Alice") == "Hello, Alice!"\n',
        )
        _write(
            project_dir,
            "pyproject.toml",
            "[build-system]\n"
            'requires = ["hatchling"]\n'
            'build-backend = "hatchling.build"\n'
            "\n"
            "[project]\n"
            f'name = "{ctx.project_name}"\n'
            'version = "0.1.0"\n'
            'description = "A short description of your package."\n'
            'requires-python = ">=3.10"\n'
            'readme = "README.md"\n'
            'license = "MIT"\n'
            "dependencies = []\n"
            "\n"
            "[project.urls]\n"
            f'Homepage = "https://github.com/your-username/{ctx.project_name}"\n'
            "\n"
            "[tool.hatch.build.targets.wheel]\n"
            f'packages = ["src/{pkg_name}"]\n',
        )
        _write(
            project_dir,
            "CHANGELOG.md",
            "# Changelog\n\n## [0.1.0] - Unreleased\n\n### Added\n\n- Initial release.\n",
        )
        ctx.create_readme(
            project_dir,
            f'python -c "from {pkg_name}.main import greet; print(greet())"',
        )
        ctx.create_requirements(project_dir, self.deps + _BASE_TEST_DEPS)
        ctx.emit("SUCCESS: PyPI Package project set up.")


class LangChainAgentProfile(BaseProfile):
    label = "LangChain Agent"
    slug = "langchain"
    deps = [
        "langchain",
        "langchain-openai",
        "langchain-community",
        "langchain-core",
        "python-dotenv",
    ]

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        _write(project_dir, "app/__init__.py", "")
        _write(
            project_dir,
            "app/agent.py",
            "import os\n"
            "from dotenv import load_dotenv\n"
            "from langchain_openai import ChatOpenAI\n"
            "from langchain.agents import AgentExecutor, create_tool_calling_agent\n"
            "from langchain_core.prompts import ChatPromptTemplate\n"
            "from app.tools.example import get_current_time\n"
            "\n"
            "load_dotenv()\n"
            "\n"
            "# Set LLM_PROVIDER=openrouter in .env to use OpenRouter instead of OpenAI\n"
            "_PROVIDER = os.environ.get('LLM_PROVIDER', 'openai')\n"
            "\n"
            "\n"
            "def _build_llm() -> ChatOpenAI:\n"
            "    if _PROVIDER == 'openrouter':\n"
            "        return ChatOpenAI(\n"
            "            model=os.environ.get('OPENROUTER_MODEL', 'openai/gpt-4o-mini'),\n"
            "            api_key=os.environ['OPENROUTER_API_KEY'],\n"
            "            base_url='https://openrouter.ai/api/v1',\n"
            "            default_headers={\n"
            "                'HTTP-Referer': os.environ.get('APP_URL', 'http://localhost'),\n"
            "                'X-Title': os.environ.get('APP_NAME', 'LangChain Agent'),\n"
            "            },\n"
            "        )\n"
            "    return ChatOpenAI(\n"
            "        model=os.environ.get('OPENAI_MODEL', 'gpt-4o-mini'),\n"
            "        api_key=os.environ['OPENAI_API_KEY'],\n"
            "    )\n"
            "\n"
            "\n"
            "def build_agent() -> AgentExecutor:\n"
            "    tools = [get_current_time]\n"
            "    prompt = ChatPromptTemplate.from_messages([\n"
            "        ('system', 'You are a helpful assistant.'),\n"
            "        ('human', '{input}'),\n"
            "        ('placeholder', '{agent_scratchpad}'),\n"
            "    ])\n"
            "    agent = create_tool_calling_agent(_build_llm(), tools, prompt)\n"
            "    return AgentExecutor(agent=agent, tools=tools, verbose=True)\n"
            "\n"
            "\n"
            "if __name__ == '__main__':\n"
            "    executor = build_agent()\n"
            "    result = executor.invoke({'input': 'What time is it?'})\n"
            "    print(result['output'])\n",
        )
        _write(project_dir, "app/tools/__init__.py", "")
        _write(
            project_dir,
            "app/tools/example.py",
            "from datetime import datetime, timezone\n"
            "from langchain_core.tools import tool\n"
            "\n"
            "\n"
            "@tool\n"
            "def get_current_time() -> str:\n"
            '    """Return the current UTC time."""\n'
            '    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")\n',
        )
        _write(project_dir, "tests/__init__.py", "")
        _write(
            project_dir,
            "tests/test_agent.py",
            "from unittest.mock import patch\n"
            "from app.agent import build_agent\n"
            "\n"
            "\n"
            "def test_build_agent_returns_executor():\n"
            "    from langchain.agents import AgentExecutor\n"
            '    with patch("app.agent.ChatOpenAI"):\n'
            "        agent = build_agent()\n"
            "    assert isinstance(agent, AgentExecutor)\n",
        )
        _write(
            project_dir,
            ".env.example",
            "# --- OpenAI (default) ---\n"
            "LLM_PROVIDER=openai\n"
            "OPENAI_API_KEY=sk-...\n"
            "OPENAI_MODEL=gpt-4o-mini\n"
            "\n"
            "# --- OpenRouter (set LLM_PROVIDER=openrouter to use) ---\n"
            "# LLM_PROVIDER=openrouter\n"
            "# OPENROUTER_API_KEY=sk-or-...\n"
            "# OPENROUTER_MODEL=openai/gpt-4o-mini\n"
            "# APP_URL=http://localhost\n"
            "# APP_NAME=LangChain Agent\n",
        )
        ctx.create_readme(project_dir, "python app/agent.py")
        ctx.create_docker_files(project_dir, "python app/agent.py")
        ctx.create_requirements(project_dir, self.deps + _BASE_TEST_DEPS)
        ctx.emit("SUCCESS: LangChain Agent project set up.")


class LlamaIndexAgentProfile(BaseProfile):
    label = "LlamaIndex Agent"
    slug = "llama"
    deps = [
        "llama-index",
        "llama-index-llms-openai",
        "llama-index-embeddings-openai",
        "python-dotenv",
    ]

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        os.makedirs(os.path.join(project_dir, "data"), exist_ok=True)
        _write(project_dir, "data/.gitkeep", "")
        _write(project_dir, "app/__init__.py", "")
        _write(
            project_dir,
            "app/agent.py",
            "import os\n"
            "from dotenv import load_dotenv\n"
            "from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings\n"
            "from llama_index.llms.openai import OpenAI\n"
            "from llama_index.core.agent import ReActAgent\n"
            "from llama_index.core.tools import QueryEngineTool, ToolMetadata\n"
            "\n"
            "load_dotenv()\n"
            "\n"
            "\n"
            'def build_agent(data_dir: str = "data") -> ReActAgent:\n'
            '    """Build a ReAct agent backed by an indexed document store."""\n'
            '    Settings.llm = OpenAI(model="gpt-4o-mini")\n'
            "    documents = SimpleDirectoryReader(data_dir).load_data()\n"
            "    index = VectorStoreIndex.from_documents(documents)\n"
            "    query_engine = index.as_query_engine()\n"
            "    tool = QueryEngineTool(\n"
            "        query_engine=query_engine,\n"
            "        metadata=ToolMetadata(\n"
            '            name="document_search",\n'
            '            description="Search through the indexed documents.",\n'
            "        ),\n"
            "    )\n"
            "    return ReActAgent.from_tools([tool], verbose=True)\n"
            "\n"
            "\n"
            'if __name__ == "__main__":\n'
            "    agent = build_agent()\n"
            '    response = agent.chat("What are the main topics in the documents?")\n'
            "    print(response)\n",
        )
        _write(project_dir, "app/indices/__init__.py", "")
        _write(project_dir, "tests/__init__.py", "")
        _write(
            project_dir,
            "tests/test_agent.py",
            "from unittest.mock import patch, MagicMock\n"
            "\n"
            "\n"
            "def test_build_agent_mocked():\n"
            '    with patch("app.agent.SimpleDirectoryReader") as mock_reader, \\\n'
            '         patch("app.agent.VectorStoreIndex") as mock_index, \\\n'
            '         patch("app.agent.OpenAI"), \\\n'
            '         patch("app.agent.ReActAgent") as mock_agent_cls:\n'
            "        mock_reader.return_value.load_data.return_value = []\n"
            "        mock_index.from_documents.return_value.as_query_engine.return_value = MagicMock()\n"
            "        mock_agent_cls.from_tools.return_value = MagicMock()\n"
            "        from app.agent import build_agent\n"
            "        agent = build_agent()\n"
            "    assert agent is not None\n",
        )
        _write(project_dir, ".env.example", "OPENAI_API_KEY=sk-...\n")
        ctx.create_readme(project_dir, "python app/agent.py")
        ctx.create_docker_files(project_dir, "python app/agent.py")
        ctx.create_requirements(
            project_dir,
            self.deps + _BASE_TEST_DEPS,
        )
        ctx.emit("SUCCESS: LlamaIndex Agent project set up.")


class FlaskProfile(BaseProfile):
    label = "Flask Web App"
    slug = "flask"
    deps = ["flask", "flask-cors"]

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        _write(
            project_dir,
            "app/__init__.py",
            "from flask import Flask\n"
            "\n"
            "\n"
            "def create_app() -> Flask:\n"
            "    app = Flask(__name__)\n"
            "    from app.routes import bp\n"
            "    app.register_blueprint(bp)\n"
            "    return app\n",
        )
        _write(
            project_dir,
            "app/routes.py",
            "from flask import Blueprint, jsonify\n"
            "\n"
            "bp = Blueprint('main', __name__)\n"
            "\n"
            "\n"
            "@bp.get('/health')\n"
            "def health():\n"
            "    return jsonify({'status': 'ok'})\n",
        )
        _write(
            project_dir,
            "app/main.py",
            "from app import create_app\n"
            "\n"
            "app = create_app()\n"
            "\n"
            "if __name__ == '__main__':\n"
            "    app.run(debug=True)\n",
        )
        _write(project_dir, "tests/__init__.py", "")
        _write(
            project_dir,
            "tests/test_routes.py",
            "import pytest\n"
            "from app import create_app\n"
            "\n"
            "\n"
            "@pytest.fixture\n"
            "def client():\n"
            "    app = create_app()\n"
            "    app.config['TESTING'] = True\n"
            "    with app.test_client() as c:\n"
            "        yield c\n"
            "\n"
            "\n"
            "def test_health(client):\n"
            "    resp = client.get('/health')\n"
            "    assert resp.status_code == 200\n"
            "    assert resp.get_json()['status'] == 'ok'\n",
        )
        ctx.create_readme(project_dir, "flask --app app.main run")
        ctx.create_docker_files(
            project_dir, "flask --app app.main run --host 0.0.0.0", is_fastapi=True
        )
        ctx.create_requirements(project_dir, self.deps + _BASE_TEST_DEPS)
        ctx.emit("SUCCESS: Flask Web App project set up.")


class StreamlitProfile(BaseProfile):
    label = "Streamlit Dashboard"
    slug = "streamlit"
    deps = ["streamlit", "pandas", "plotly"]

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        os.makedirs(os.path.join(project_dir, "data"), exist_ok=True)
        _write(project_dir, "data/.gitkeep", "")
        _write(project_dir, "app/__init__.py", "")
        _write(
            project_dir,
            "app/main.py",
            "import streamlit as st\n"
            "import pandas as pd\n"
            "import plotly.express as px\n"
            "\n"
            "st.set_page_config(page_title='Dashboard', layout='wide')\n"
            "st.title('📊 Dashboard')\n"
            "\n"
            "uploaded = st.file_uploader('Upload a CSV', type='csv')\n"
            "if uploaded:\n"
            "    df = pd.read_csv(uploaded)\n"
            "    st.dataframe(df)\n"
            "    numeric = df.select_dtypes('number').columns.tolist()\n"
            "    if numeric:\n"
            "        col = st.selectbox('Column to plot', numeric)\n"
            "        fig = px.histogram(df, x=col)\n"
            "        st.plotly_chart(fig, use_container_width=True)\n"
            "else:\n"
            "    st.info('Upload a CSV file to get started.')\n",
        )
        _write(project_dir, "tests/__init__.py", "")
        _write(
            project_dir,
            "tests/test_placeholder.py",
            "# Streamlit apps are best tested with streamlit.testing.v1\n"
            "def test_placeholder():\n"
            "    assert True\n",
        )
        ctx.create_readme(project_dir, "streamlit run app/main.py")
        ctx.create_docker_files(
            project_dir,
            "streamlit run app/main.py --server.port 8501 --server.address 0.0.0.0",
            is_fastapi=True,
        )
        ctx.create_requirements(project_dir, self.deps + _BASE_TEST_DEPS)
        ctx.emit("SUCCESS: Streamlit Dashboard project set up.")


class MCPServerProfile(BaseProfile):
    label = "MCP Server (Model Context Protocol)"
    slug = "mcp"
    deps = ["mcp[cli]"]

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        _write(project_dir, "app/__init__.py", "")
        _write(
            project_dir,
            "app/server.py",
            "from mcp.server.fastmcp import FastMCP\n"
            "\n"
            "mcp = FastMCP('my-mcp-server')\n"
            "\n"
            "\n"
            "@mcp.tool()\n"
            "def add(a: int, b: int) -> int:\n"
            '    """Add two integers."""\n'
            "    return a + b\n"
            "\n"
            "\n"
            "@mcp.resource('greeting://{name}')\n"
            "def greet(name: str) -> str:\n"
            '    """Return a greeting for *name*."""\n'
            "    return f'Hello, {name}!'\n"
            "\n"
            "\n"
            "if __name__ == '__main__':\n"
            "    mcp.run(transport='stdio')\n",
        )
        _write(project_dir, "tests/__init__.py", "")
        _write(
            project_dir,
            "tests/test_tools.py",
            "from app.server import add\n"
            "\n"
            "\n"
            "def test_add():\n"
            "    assert add(2, 3) == 5\n"
            "\n"
            "\n"
            "def test_add_negative():\n"
            "    assert add(-1, 1) == 0\n",
        )
        ctx.create_readme(project_dir, "python app/server.py")
        ctx.create_docker_files(project_dir, "python app/server.py")
        ctx.create_requirements(project_dir, self.deps + _BASE_TEST_DEPS)
        ctx.emit("SUCCESS: MCP Server project set up.")


class DiscordBotProfile(BaseProfile):
    label = "Discord Bot (discord.py)"
    slug = "discord"
    deps = ["discord.py", "python-dotenv"]

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        _write(project_dir, "bot/__init__.py", "")
        _write(
            project_dir,
            "bot/main.py",
            "import os\n"
            "import discord\n"
            "from discord.ext import commands\n"
            "from dotenv import load_dotenv\n"
            "\n"
            "load_dotenv()\n"
            "\n"
            "intents = discord.Intents.default()\n"
            "intents.message_content = True\n"
            "\n"
            "bot = commands.Bot(command_prefix='!', intents=intents)\n"
            "\n"
            "\n"
            "@bot.event\n"
            "async def on_ready():\n"
            "    print(f'Logged in as {bot.user} ({bot.user.id})')\n"
            "    await bot.load_extension('bot.cogs.general')\n"
            "\n"
            "\n"
            "if __name__ == '__main__':\n"
            "    bot.run(os.environ['DISCORD_TOKEN'])\n",
        )
        _write(project_dir, "bot/cogs/__init__.py", "")
        _write(
            project_dir,
            "bot/cogs/general.py",
            "import discord\n"
            "from discord.ext import commands\n"
            "\n"
            "\n"
            "class General(commands.Cog):\n"
            "    def __init__(self, bot: commands.Bot) -> None:\n"
            "        self.bot = bot\n"
            "\n"
            "    @commands.command()\n"
            "    async def ping(self, ctx: commands.Context) -> None:\n"
            '        """Responds with Pong!"""\n'
            "        await ctx.send(f'Pong! {round(self.bot.latency * 1000)}ms')\n"
            "\n"
            "\n"
            "async def setup(bot: commands.Bot) -> None:\n"
            "    await bot.add_cog(General(bot))\n",
        )
        _write(project_dir, "tests/__init__.py", "")
        _write(
            project_dir,
            "tests/test_bot.py",
            "def test_cog_loads():\n"
            '    """Smoke-test: import the cog without a running bot."""\n'
            "    from bot.cogs.general import General\n"
            "    assert General\n",
        )
        _write(project_dir, ".env.example", "DISCORD_TOKEN=your-bot-token-here\n")
        ctx.create_readme(project_dir, "python bot/main.py")
        ctx.create_docker_files(project_dir, "python bot/main.py")
        ctx.create_requirements(project_dir, self.deps + _BASE_TEST_DEPS)
        ctx.emit("SUCCESS: Discord Bot project set up.")


class FastAPISQLProfile(BaseProfile):
    label = "FastAPI + SQLAlchemy + Alembic"
    slug = "fastapi-db"
    deps = [
        "fastapi",
        "uvicorn[standard]",
        "sqlalchemy[asyncio]",
        "alembic",
        "aiosqlite",
        "asyncpg",
        "pydantic",
        "anyio[trio]",
        "httpx",
    ]

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        # app package
        _write(project_dir, "app/__init__.py", "")
        _write(
            project_dir,
            "app/main.py",
            "from fastapi import FastAPI\n"
            "from app.routers import items\n"
            "\n"
            "app = FastAPI(title='FastAPI + SQLAlchemy')\n"
            "app.include_router(items.router, prefix='/items', tags=['items'])\n"
            "\n"
            "\n"
            "@app.get('/health')\n"
            "async def health():\n"
            "    return {'status': 'ok'}\n",
        )
        _write(
            project_dir,
            "app/database.py",
            "from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine\n"
            "from sqlalchemy.orm import sessionmaker, DeclarativeBase\n"
            "import os\n"
            "\n"
            "DATABASE_URL = os.environ.get(\n"
            "    'DATABASE_URL', 'sqlite+aiosqlite:///./dev.db'\n"
            ")\n"
            "\n"
            "engine = create_async_engine(DATABASE_URL, echo=False)\n"
            "AsyncSessionLocal = sessionmaker(\n"
            "    engine, class_=AsyncSession, expire_on_commit=False\n"
            ")\n"
            "\n"
            "\n"
            "class Base(DeclarativeBase):\n"
            "    pass\n"
            "\n"
            "\n"
            "async def get_db() -> AsyncSession:\n"
            "    async with AsyncSessionLocal() as session:\n"
            "        yield session\n",
        )
        _write(
            project_dir,
            "app/models.py",
            "from sqlalchemy import Integer, String\n"
            "from sqlalchemy.orm import Mapped, mapped_column\n"
            "from app.database import Base\n"
            "\n"
            "\n"
            "class Item(Base):\n"
            "    __tablename__ = 'items'\n"
            "\n"
            "    id: Mapped[int] = mapped_column(Integer, primary_key=True)\n"
            "    name: Mapped[str] = mapped_column(String(255), nullable=False)\n"
            "    description: Mapped[str | None] = mapped_column(String(1024))\n",
        )
        _write(
            project_dir,
            "app/schemas.py",
            "from pydantic import BaseModel\n"
            "\n"
            "\n"
            "class ItemCreate(BaseModel):\n"
            "    name: str\n"
            "    description: str | None = None\n"
            "\n"
            "\n"
            "class ItemRead(ItemCreate):\n"
            "    id: int\n"
            "\n"
            "    model_config = {'from_attributes': True}\n",
        )
        _write(project_dir, "app/routers/__init__.py", "")
        _write(
            project_dir,
            "app/routers/items.py",
            "from fastapi import APIRouter, Depends\n"
            "from sqlalchemy import select\n"
            "from sqlalchemy.ext.asyncio import AsyncSession\n"
            "from app.database import get_db\n"
            "from app.models import Item\n"
            "from app.schemas import ItemCreate, ItemRead\n"
            "\n"
            "router = APIRouter()\n"
            "\n"
            "\n"
            "@router.get('/', response_model=list[ItemRead])\n"
            "async def list_items(db: AsyncSession = Depends(get_db)):\n"
            "    result = await db.execute(select(Item))\n"
            "    return result.scalars().all()\n"
            "\n"
            "\n"
            "@router.post('/', response_model=ItemRead, status_code=201)\n"
            "async def create_item(\n"
            "    payload: ItemCreate, db: AsyncSession = Depends(get_db)\n"
            "):\n"
            "    item = Item(**payload.model_dump())\n"
            "    db.add(item)\n"
            "    await db.commit()\n"
            "    await db.refresh(item)\n"
            "    return item\n",
        )
        # Alembic scaffold
        os.makedirs(os.path.join(project_dir, "alembic", "versions"), exist_ok=True)
        _write(project_dir, "alembic/versions/.gitkeep", "")
        _write(
            project_dir,
            "alembic/env.py",
            "import asyncio\n"
            "from logging.config import fileConfig\n"
            "from alembic import context\n"
            "from sqlalchemy.ext.asyncio import create_async_engine\n"
            "from app.database import DATABASE_URL\n"
            "from app.models import Base\n"
            "\n"
            "config = context.config\n"
            "if config.config_file_name:\n"
            "    fileConfig(config.config_file_name)\n"
            "\n"
            "target_metadata = Base.metadata\n"
            "\n"
            "\n"
            "def run_migrations_offline():\n"
            "    context.configure(\n"
            "        url=DATABASE_URL,\n"
            "        target_metadata=target_metadata,\n"
            "        literal_binds=True,\n"
            "    )\n"
            "    with context.begin_transaction():\n"
            "        context.run_migrations()\n"
            "\n"
            "\n"
            "async def run_migrations_online():\n"
            "    engine = create_async_engine(DATABASE_URL)\n"
            "    async with engine.begin() as conn:\n"
            "        await conn.run_sync(\n"
            "            lambda sync_conn: context.configure(\n"
            "                connection=sync_conn,\n"
            "                target_metadata=target_metadata,\n"
            "            )\n"
            "        )\n"
            "        with context.begin_transaction():\n"
            "            context.run_migrations()\n"
            "    await engine.dispose()\n"
            "\n"
            "\n"
            "if context.is_offline_mode():\n"
            "    run_migrations_offline()\n"
            "else:\n"
            "    asyncio.run(run_migrations_online())\n",
        )
        _write(
            project_dir,
            "alembic.ini",
            "[alembic]\n"
            "script_location = alembic\n"
            "prepend_sys_path = .\n"
            "sqlalchemy.url =\n"
            "\n"
            "[post_write_hooks]\n"
            "\n"
            "[loggers]\n"
            "keys = root,sqlalchemy,alembic\n"
            "\n"
            "[handlers]\n"
            "keys = console\n"
            "\n"
            "[formatters]\n"
            "keys = generic\n"
            "\n"
            "[logger_root]\n"
            "level = WARN\n"
            "handlers = console\n"
            "qualname =\n"
            "\n"
            "[logger_sqlalchemy]\n"
            "level = WARN\n"
            "handlers =\n"
            "qualname = sqlalchemy.engine\n"
            "\n"
            "[logger_alembic]\n"
            "level = INFO\n"
            "handlers =\n"
            "qualname = alembic\n"
            "\n"
            "[handler_console]\n"
            "class = StreamHandler\n"
            "args = (sys.stderr,)\n"
            "level = NOTSET\n"
            "formatter = generic\n"
            "\n"
            "[formatter_generic]\n"
            "format = %(levelname)-5.5s [%(name)s] %(message)s\n"
            "datefmt = %%H:%%M:%%S\n",
        )
        # tests
        _write(project_dir, "tests/__init__.py", "")
        _write(
            project_dir,
            "tests/test_health.py",
            "import pytest\n"
            "from httpx import AsyncClient, ASGITransport\n"
            "from app.main import app\n"
            "\n"
            "\n"
            "@pytest.mark.anyio\n"
            "async def test_health():\n"
            "    async with AsyncClient(\n"
            "        transport=ASGITransport(app=app), base_url='http://test'\n"
            "    ) as ac:\n"
            "        resp = await ac.get('/health')\n"
            "    assert resp.status_code == 200\n"
            "    assert resp.json()['status'] == 'ok'\n",
        )
        _write(
            project_dir,
            ".env.example",
            "DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname\n",
        )
        ctx.create_readme(project_dir, "uvicorn app.main:app --reload")
        ctx.create_docker_files(
            project_dir,
            "uvicorn app.main:app --host 0.0.0.0 --port 8000",
            is_fastapi=True,
        )
        ctx.create_requirements(project_dir, self.deps + _BASE_TEST_DEPS)
        ctx.emit("SUCCESS: FastAPI + SQLAlchemy + Alembic project set up.")


class AWSLambdaProfile(BaseProfile):
    label = "AWS Lambda (Serverless)"
    slug = "lambda"
    deps = ["boto3", "aws-lambda-powertools", "python-dotenv"]

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        os.makedirs(os.path.join(project_dir, "src"), exist_ok=True)
        _write(project_dir, "src/__init__.py", "")
        _write(
            project_dir,
            "src/handler.py",
            "import json\n"
            "import logging\n"
            "from aws_lambda_powertools import Logger, Tracer\n"
            "from aws_lambda_powertools.utilities.typing import LambdaContext\n"
            "\n"
            "logger = Logger()\n"
            "tracer = Tracer()\n"
            "\n"
            "\n"
            "@logger.inject_lambda_context\n"
            "@tracer.capture_lambda_handler\n"
            "def handler(event: dict, context: LambdaContext) -> dict:\n"
            '    """Main Lambda entry point."""\n'
            "    logger.info('Event received', extra={'event': event})\n"
            "    name = event.get('queryStringParameters', {}).get('name', 'World')\n"
            "    return {\n"
            "        'statusCode': 200,\n"
            "        'headers': {'Content-Type': 'application/json'},\n"
            "        'body': json.dumps({'message': f'Hello, {name}!'}),\n"
            "    }\n",
        )
        _write(
            project_dir,
            "template.yaml",
            "AWSTemplateFormatVersion: '2010-09-09'\n"
            "Transform: AWS::Serverless-2016-10-31\n"
            "Description: SAM template\n"
            "\n"
            "Globals:\n"
            "  Function:\n"
            "    Timeout: 30\n"
            "    MemorySize: 256\n"
            "    Runtime: python3.12\n"
            "    Environment:\n"
            "      Variables:\n"
            "        POWERTOOLS_SERVICE_NAME: my-service\n"
            "        LOG_LEVEL: INFO\n"
            "\n"
            "Resources:\n"
            "  HelloFunction:\n"
            "    Type: AWS::Serverless::Function\n"
            "    Properties:\n"
            "      CodeUri: src/\n"
            "      Handler: handler.handler\n"
            "      Events:\n"
            "        HelloApi:\n"
            "          Type: Api\n"
            "          Properties:\n"
            "            Path: /hello\n"
            "            Method: get\n"
            "\n"
            "Outputs:\n"
            "  HelloApi:\n"
            "    Description: API Gateway endpoint URL\n"
            "    Value: !Sub 'https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/hello/'\n",
        )
        _write(
            project_dir,
            "Makefile",
            "build:\n"
            "\tsam build\n"
            "\n"
            "deploy:\n"
            "\tsam deploy --guided\n"
            "\n"
            "local:\n"
            "\tsam local start-api\n"
            "\n"
            "invoke:\n"
            "\tsam local invoke HelloFunction --event events/hello.json\n",
        )
        _write(
            project_dir,
            "events/hello.json",
            '{\n  "queryStringParameters": {\n    "name": "World"\n  }\n}\n',
        )
        _write(project_dir, "tests/__init__.py", "")
        _write(
            project_dir,
            "tests/test_handler.py",
            "import json\n"
            "from unittest.mock import MagicMock\n"
            "from src.handler import handler\n"
            "\n"
            "\n"
            "def _ctx() -> MagicMock:\n"
            "    ctx = MagicMock()\n"
            "    ctx.function_name = 'test-function'\n"
            "    ctx.aws_request_id = 'test-request-id'\n"
            "    return ctx\n"
            "\n"
            "\n"
            "def test_handler_returns_200():\n"
            "    event = {'queryStringParameters': {'name': 'Alice'}}\n"
            "    resp = handler(event, _ctx())\n"
            "    assert resp['statusCode'] == 200\n"
            "\n"
            "\n"
            "def test_handler_body_contains_name():\n"
            "    event = {'queryStringParameters': {'name': 'Alice'}}\n"
            "    resp = handler(event, _ctx())\n"
            "    body = json.loads(resp['body'])\n"
            "    assert 'Alice' in body['message']\n"
            "\n"
            "\n"
            "def test_handler_default_name():\n"
            "    resp = handler({}, _ctx())\n"
            "    body = json.loads(resp['body'])\n"
            "    assert 'World' in body['message']\n",
        )
        _write(
            project_dir,
            ".env.example",
            "AWS_ACCESS_KEY_ID=your-key-id\n"
            "AWS_SECRET_ACCESS_KEY=your-secret\n"
            "AWS_DEFAULT_REGION=us-east-1\n",
        )
        ctx.create_readme(project_dir, "sam local start-api")
        ctx.create_requirements(project_dir, self.deps + _BASE_TEST_DEPS)
        ctx.emit("SUCCESS: AWS Lambda project set up.")


class PytestPluginProfile(BaseProfile):
    label = "pytest Plugin"
    slug = "pytest-plugin"
    deps = ["pytest", "hatchling"]

    def setup(self, project_dir: str, ctx: ProfileContext) -> None:
        pkg_name = ctx.project_name.replace("-", "_")
        _write(
            project_dir,
            f"src/{pkg_name}/__init__.py",
            '__version__ = "0.1.0"\n',
        )
        _write(
            project_dir,
            f"src/{pkg_name}/plugin.py",
            "import pytest\n"
            "\n"
            "\n"
            "def pytest_configure(config: pytest.Config) -> None:\n"
            '    """Register the plugin markers."""\n'
            '    config.addinivalue_line("markers", "slow: mark test as slow")\n',
        )
        # conftest.py that registers the plugin
        _write(
            project_dir,
            f"src/{pkg_name}/conftest.py",
            f"from {pkg_name}.plugin import pytest_configure\n"
            "\n"
            "__all__ = ['pytest_configure']\n",
        )
        _write(project_dir, "tests/__init__.py", "")
        _write(
            project_dir,
            "tests/conftest.py",
            "import pytest\n"
            "\n"
            "\n"
            "@pytest.fixture\n"
            "def sample_fixture():\n"
            "    return 42\n",
        )
        _write(
            project_dir,
            "tests/test_plugin.py",
            "import pytest\n"
            "\n"
            "\n"
            "def test_marker_registered(pytestconfig):\n"
            '    markers = [m.name for m in pytestconfig.getini("markers")]\n'
            '    assert "slow" in " ".join(markers)\n'
            "\n"
            "\n"
            "def test_sample_fixture(sample_fixture):\n"
            "    assert sample_fixture == 42\n",
        )
        _write(
            project_dir,
            "pyproject.toml",
            "[build-system]\n"
            'requires = ["hatchling"]\n'
            'build-backend = "hatchling.build"\n'
            "\n"
            "[project]\n"
            f'name = "{ctx.project_name}"\n'
            'version = "0.1.0"\n'
            'description = "A pytest plugin."\n'
            'requires-python = ">=3.10"\n'
            'readme = "README.md"\n'
            'license = "MIT"\n'
            'dependencies = ["pytest>=7.0"]\n'
            "\n"
            "[project.entry-points.'pytest11']\n"
            f'{pkg_name} = "{pkg_name}.plugin"\n'
            "\n"
            "[tool.hatch.build.targets.wheel]\n"
            f'packages = ["src/{pkg_name}"]\n'
            "\n"
            "[tool.pytest.ini_options]\n"
            f'addopts = "--import-mode=importlib"\n',
        )
        _write(
            project_dir,
            "CHANGELOG.md",
            "# Changelog\n\n## [0.1.0] - Unreleased\n\n### Added\n\n- Initial release.\n",
        )
        ctx.create_readme(project_dir, "pytest --co -q")
        ctx.create_requirements(project_dir, self.deps + _BASE_TEST_DEPS)
        ctx.emit("SUCCESS: pytest Plugin project set up.")


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

ALL_PROFILES: list[type[BaseProfile]] = [
    BasicPythonProfile,
    DataAnalyticsProfile,
    FastAPIProfile,
    FastAPISQLProfile,
    FlaskProfile,
    StreamlitProfile,
    CLIToolProfile,
    TelegramBotProfile,
    DiscordBotProfile,
    DjangoProfile,
    GRPCServiceProfile,
    CeleryWorkerProfile,
    MLProjectProfile,
    ScraperProfile,
    PyPIPackageProfile,
    LangChainAgentProfile,
    LlamaIndexAgentProfile,
    MCPServerProfile,
    AWSLambdaProfile,
    PytestPluginProfile,
]
