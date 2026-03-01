"""Tests for profiles added in the second batch: flask, fastapi-db, streamlit, mcp, discord, lambda, pytest-plugin."""

from profiles import (
    FlaskProfile,
    FastAPISQLProfile,
    StreamlitProfile,
    MCPServerProfile,
    DiscordBotProfile,
    AWSLambdaProfile,
    PytestPluginProfile,
)


# ---------------------------------------------------------------------------
# Flask
# ---------------------------------------------------------------------------


class TestFlaskProfile:
    def test_directory_structure(self, ctx, tmp_path):
        FlaskProfile().setup(str(tmp_path), ctx)
        assert (tmp_path / "app" / "__init__.py").exists()
        assert (tmp_path / "app" / "routes.py").exists()
        assert (tmp_path / "app" / "main.py").exists()
        assert (tmp_path / "tests" / "test_routes.py").exists()
        assert (tmp_path / "requirements.txt").exists()
        assert (tmp_path / "README.md").exists()
        assert (tmp_path / "Dockerfile").exists()
        assert (tmp_path / "docker-compose.yml").exists()

    def test_init_uses_app_factory(self, ctx, tmp_path):
        FlaskProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "app" / "__init__.py").read_text()
        assert "create_app" in content
        assert "Flask" in content

    def test_routes_has_blueprint(self, ctx, tmp_path):
        FlaskProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "app" / "routes.py").read_text()
        assert "Blueprint" in content
        assert "/health" in content

    def test_test_file_uses_test_client(self, ctx, tmp_path):
        FlaskProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "tests" / "test_routes.py").read_text()
        assert "test_client" in content
        assert "def test_health" in content

    def test_requirements_includes_flask(self, ctx, tmp_path):
        FlaskProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "requirements.txt").read_text()
        assert "flask" in content
        assert "pytest" in content

    def test_compose_exposes_port_8000(self, ctx, tmp_path):
        FlaskProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "docker-compose.yml").read_text()
        assert "8000" in content


# ---------------------------------------------------------------------------
# FastAPI + SQLAlchemy + Alembic
# ---------------------------------------------------------------------------


class TestFastAPISQLProfile:
    def test_directory_structure(self, ctx, tmp_path):
        FastAPISQLProfile().setup(str(tmp_path), ctx)
        assert (tmp_path / "app" / "main.py").exists()
        assert (tmp_path / "app" / "database.py").exists()
        assert (tmp_path / "app" / "models.py").exists()
        assert (tmp_path / "app" / "schemas.py").exists()
        assert (tmp_path / "app" / "routers" / "items.py").exists()
        assert (tmp_path / "alembic" / "env.py").exists()
        assert (tmp_path / "alembic" / "versions").is_dir()
        assert (tmp_path / "alembic.ini").exists()
        assert (tmp_path / "tests" / "test_health.py").exists()
        assert (tmp_path / ".env.example").exists()

    def test_main_includes_router(self, ctx, tmp_path):
        FastAPISQLProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "app" / "main.py").read_text()
        assert "include_router" in content
        assert "/health" in content

    def test_database_has_async_engine(self, ctx, tmp_path):
        FastAPISQLProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "app" / "database.py").read_text()
        assert "create_async_engine" in content
        assert "AsyncSession" in content
        assert "get_db" in content

    def test_models_use_mapped_column(self, ctx, tmp_path):
        FastAPISQLProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "app" / "models.py").read_text()
        assert "mapped_column" in content
        assert "class Item" in content

    def test_schemas_use_pydantic_v2(self, ctx, tmp_path):
        FastAPISQLProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "app" / "schemas.py").read_text()
        assert "model_config" in content
        assert "from_attributes" in content

    def test_router_has_crud_endpoints(self, ctx, tmp_path):
        FastAPISQLProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "app" / "routers" / "items.py").read_text()
        assert "@router.get" in content
        assert "@router.post" in content

    def test_alembic_env_is_async(self, ctx, tmp_path):
        FastAPISQLProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "alembic" / "env.py").read_text()
        assert "create_async_engine" in content
        assert "target_metadata" in content

    def test_test_uses_anyio(self, ctx, tmp_path):
        FastAPISQLProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "tests" / "test_health.py").read_text()
        assert "anyio" in content
        assert "AsyncClient" in content

    def test_requirements_includes_sqlalchemy_and_alembic(self, ctx, tmp_path):
        FastAPISQLProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "requirements.txt").read_text()
        assert "sqlalchemy" in content
        assert "alembic" in content
        assert "fastapi" in content

    def test_env_example_has_database_url(self, ctx, tmp_path):
        FastAPISQLProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / ".env.example").read_text()
        assert "DATABASE_URL" in content


# ---------------------------------------------------------------------------
# Streamlit
# ---------------------------------------------------------------------------


class TestStreamlitProfile:
    def test_directory_structure(self, ctx, tmp_path):
        StreamlitProfile().setup(str(tmp_path), ctx)
        assert (tmp_path / "app" / "main.py").exists()
        assert (tmp_path / "data" / ".gitkeep").exists()
        assert (tmp_path / "tests").is_dir()
        assert (tmp_path / "requirements.txt").exists()
        assert (tmp_path / "README.md").exists()

    def test_main_imports_streamlit(self, ctx, tmp_path):
        StreamlitProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "app" / "main.py").read_text()
        assert "import streamlit as st" in content

    def test_main_uses_plotly(self, ctx, tmp_path):
        StreamlitProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "app" / "main.py").read_text()
        assert "plotly" in content

    def test_main_has_file_uploader(self, ctx, tmp_path):
        StreamlitProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "app" / "main.py").read_text()
        assert "file_uploader" in content

    def test_requirements_includes_streamlit(self, ctx, tmp_path):
        StreamlitProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "requirements.txt").read_text()
        assert "streamlit" in content
        assert "pandas" in content
        assert "plotly" in content

    def test_readme_has_run_command(self, ctx, tmp_path):
        StreamlitProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "README.md").read_text()
        assert "streamlit run" in content


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------


class TestMCPServerProfile:
    def test_directory_structure(self, ctx, tmp_path):
        MCPServerProfile().setup(str(tmp_path), ctx)
        assert (tmp_path / "app" / "server.py").exists()
        assert (tmp_path / "tests" / "test_tools.py").exists()
        assert (tmp_path / "requirements.txt").exists()
        assert (tmp_path / "README.md").exists()

    def test_server_uses_fastmcp(self, ctx, tmp_path):
        MCPServerProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "app" / "server.py").read_text()
        assert "FastMCP" in content
        assert "@mcp.tool()" in content

    def test_server_has_resource(self, ctx, tmp_path):
        MCPServerProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "app" / "server.py").read_text()
        assert "@mcp.resource" in content

    def test_test_file_tests_tool_directly(self, ctx, tmp_path):
        MCPServerProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "tests" / "test_tools.py").read_text()
        assert "def test_add" in content
        assert "assert add(2, 3) == 5" in content

    def test_requirements_includes_mcp(self, ctx, tmp_path):
        MCPServerProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "requirements.txt").read_text()
        assert "mcp" in content


# ---------------------------------------------------------------------------
# Discord Bot
# ---------------------------------------------------------------------------


class TestDiscordBotProfile:
    def test_directory_structure(self, ctx, tmp_path):
        DiscordBotProfile().setup(str(tmp_path), ctx)
        assert (tmp_path / "bot" / "main.py").exists()
        assert (tmp_path / "bot" / "cogs" / "general.py").exists()
        assert (tmp_path / "tests" / "test_bot.py").exists()
        assert (tmp_path / ".env.example").exists()
        assert (tmp_path / "requirements.txt").exists()
        assert (tmp_path / "README.md").exists()

    def test_main_uses_commands_bot(self, ctx, tmp_path):
        DiscordBotProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "bot" / "main.py").read_text()
        assert "commands.Bot" in content
        assert "DISCORD_TOKEN" in content

    def test_main_uses_dotenv(self, ctx, tmp_path):
        DiscordBotProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "bot" / "main.py").read_text()
        assert "load_dotenv" in content

    def test_cog_has_ping_command(self, ctx, tmp_path):
        DiscordBotProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "bot" / "cogs" / "general.py").read_text()
        assert "@commands.command()" in content
        assert "def ping" in content

    def test_cog_has_setup_function(self, ctx, tmp_path):
        DiscordBotProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "bot" / "cogs" / "general.py").read_text()
        assert "async def setup" in content

    def test_env_example_has_token(self, ctx, tmp_path):
        DiscordBotProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / ".env.example").read_text()
        assert "DISCORD_TOKEN" in content

    def test_requirements_includes_discordpy(self, ctx, tmp_path):
        DiscordBotProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "requirements.txt").read_text()
        assert "discord" in content
        assert "python-dotenv" in content


# ---------------------------------------------------------------------------
# AWS Lambda
# ---------------------------------------------------------------------------


class TestAWSLambdaProfile:
    def test_slug_and_label(self):
        assert AWSLambdaProfile.slug == "lambda"
        assert "Lambda" in AWSLambdaProfile.label

    def test_directory_structure(self, ctx, tmp_path):
        AWSLambdaProfile().setup(str(tmp_path), ctx)
        assert (tmp_path / "src" / "handler.py").exists()
        assert (tmp_path / "template.yaml").exists()
        assert (tmp_path / "Makefile").exists()
        assert (tmp_path / "events" / "hello.json").exists()
        assert (tmp_path / "tests" / "test_handler.py").exists()
        assert (tmp_path / ".env.example").exists()
        assert (tmp_path / "requirements.txt").exists()
        assert (tmp_path / "README.md").exists()

    def test_handler_uses_powertools(self, ctx, tmp_path):
        AWSLambdaProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "src" / "handler.py").read_text()
        assert "aws_lambda_powertools" in content
        assert "Logger" in content
        assert "Tracer" in content

    def test_handler_returns_status_code(self, ctx, tmp_path):
        AWSLambdaProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "src" / "handler.py").read_text()
        assert "statusCode" in content
        assert "200" in content

    def test_template_yaml_is_sam(self, ctx, tmp_path):
        AWSLambdaProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "template.yaml").read_text()
        assert "AWS::Serverless-2016-10-31" in content
        assert "AWS::Serverless::Function" in content

    def test_test_file_covers_default_and_custom_name(self, ctx, tmp_path):
        AWSLambdaProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "tests" / "test_handler.py").read_text()
        assert "def test_handler_default_name" in content
        assert "def test_handler_body_contains_name" in content

    def test_requirements_includes_powertools(self, ctx, tmp_path):
        AWSLambdaProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "requirements.txt").read_text()
        assert "aws-lambda-powertools" in content
        assert "boto3" in content

    def test_deps_class_attribute(self):
        assert "boto3" in AWSLambdaProfile.deps
        assert "aws-lambda-powertools" in AWSLambdaProfile.deps


# ---------------------------------------------------------------------------
# pytest Plugin
# ---------------------------------------------------------------------------


class TestPytestPluginProfile:
    def test_slug_and_label(self):
        assert PytestPluginProfile.slug == "pytest-plugin"
        assert "pytest" in PytestPluginProfile.label.lower()

    def test_directory_structure(self, ctx, tmp_path):
        PytestPluginProfile().setup(str(tmp_path), ctx)
        pkg = ctx.project_name.replace("-", "_")
        assert (tmp_path / "src" / pkg / "__init__.py").exists()
        assert (tmp_path / "src" / pkg / "plugin.py").exists()
        assert (tmp_path / "tests" / "conftest.py").exists()
        assert (tmp_path / "tests" / "test_plugin.py").exists()
        assert (tmp_path / "pyproject.toml").exists()
        assert (tmp_path / "CHANGELOG.md").exists()
        assert (tmp_path / "requirements.txt").exists()
        assert (tmp_path / "README.md").exists()

    def test_plugin_registers_marker(self, ctx, tmp_path):
        PytestPluginProfile().setup(str(tmp_path), ctx)
        pkg = ctx.project_name.replace("-", "_")
        content = (tmp_path / "src" / pkg / "plugin.py").read_text()
        assert "pytest_configure" in content
        assert "addinivalue_line" in content

    def test_pyproject_has_pytest11_entrypoint(self, ctx, tmp_path):
        PytestPluginProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "pyproject.toml").read_text()
        assert "pytest11" in content

    def test_pyproject_uses_hatchling(self, ctx, tmp_path):
        PytestPluginProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "pyproject.toml").read_text()
        assert "hatchling" in content

    def test_changelog_exists(self, ctx, tmp_path):
        PytestPluginProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "CHANGELOG.md").read_text()
        assert "0.1.0" in content

    def test_requirements_includes_pytest(self, ctx, tmp_path):
        PytestPluginProfile().setup(str(tmp_path), ctx)
        content = (tmp_path / "requirements.txt").read_text()
        assert "pytest" in content

    def test_deps_class_attribute(self):
        assert "hatchling" in PytestPluginProfile.deps
