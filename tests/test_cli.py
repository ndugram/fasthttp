import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from fasthttp.cli import commands
from fasthttp.cli.client import CLIResponse as ClientResponse


class TestParseHeaders:
    """Tests for parse_headers function."""

    def test_parse_headers_single(self) -> None:
        """Test parsing single header."""
        result = commands.parse_headers("Content-Type: application/json")
        assert result == {"Content-Type": "application/json"}

    def test_parse_headers_multiple(self) -> None:
        """Test parsing multiple headers."""
        result = commands.parse_headers("Content-Type: application/json,Authorization: Bearer token")
        assert result == {
            "Content-Type": "application/json",
            "Authorization": "Bearer token",
        }

    def test_parse_headers_none(self) -> None:
        """Test parsing None."""
        result = commands.parse_headers(None)
        assert result is None

    def test_parse_headers_empty(self) -> None:
        """Test parsing empty string."""
        result = commands.parse_headers("")
        assert result is None


class TestGetOutput:
    """Tests for get_output function."""

    def test_output_status(self) -> None:
        """Test status output."""
        resp = ClientResponse(
            status=200,
            text="OK",
            headers={},
            json_data=None,
            elapsed_ms=100.0,
        )
        result = commands.get_output(resp, "status")
        assert result == "200"

    def test_output_headers(self) -> None:
        """Test headers output."""
        resp = ClientResponse(
            status=200,
            text="OK",
            headers={"Content-Type": "application/json"},
            json_data=None,
            elapsed_ms=100.0,
        )
        result = commands.get_output(resp, "headers")
        assert "Content-Type" in result

    def test_output_json(self) -> None:
        """Test JSON output."""
        resp = ClientResponse(
            status=200,
            text='{"key": "value"}',
            headers={},
            json_data={"key": "value"},
            elapsed_ms=100.0,
        )
        result = commands.get_output(resp, "json")
        assert "key" in result
        assert "value" in result

    def test_output_json_no_data(self) -> None:
        """Test JSON output with no JSON data."""
        resp = ClientResponse(
            status=200,
            text="plain text",
            headers={},
            json_data=None,
            elapsed_ms=100.0,
        )
        result = commands.get_output(resp, "json")
        assert "(no JSON in response)" in result

    def test_output_text(self) -> None:
        """Test text output."""
        resp = ClientResponse(
            status=200,
            text="plain text response",
            headers={},
            json_data=None,
            elapsed_ms=100.0,
        )
        result = commands.get_output(resp, "text")
        assert result == "plain text response"

    def test_output_all(self) -> None:
        """Test all output."""
        resp = ClientResponse(
            status=200,
            text="response body",
            headers={"Content-Type": "text/plain"},
            json_data=None,
            elapsed_ms=150.5,
        )
        result = commands.get_output(resp, "all")
        assert "200" in result
        assert "150.50ms" in result
        assert "response body" in result

    def test_output_unknown(self) -> None:
        """Test unknown output type."""
        resp = ClientResponse(
            status=200,
            text="OK",
            headers={},
            json_data=None,
            elapsed_ms=100.0,
        )
        result = commands.get_output(resp, "unknown")
        assert "Unknown output type" in result


class TestCLICommands:
    """Tests for CLI commands using CliRunner."""

    def test_cli_runner_get_help(self) -> None:
        """Test CLI runner shows help."""
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(commands.app, ["get", "--help"])
        assert result.exit_code == 0
        assert "url" in result.stdout.lower()

    def test_cli_runner_post_help(self) -> None:
        """Test CLI runner shows post help."""
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(commands.app, ["post", "--help"])
        assert result.exit_code == 0

    def test_cli_runner_put_help(self) -> None:
        """Test CLI runner shows put help."""
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(commands.app, ["put", "--help"])
        assert result.exit_code == 0

    def test_cli_runner_patch_help(self) -> None:
        """Test CLI runner shows patch help."""
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(commands.app, ["patch", "--help"])
        assert result.exit_code == 0

    def test_cli_runner_delete_help(self) -> None:
        """Test CLI runner shows delete help."""
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(commands.app, ["delete", "--help"])
        assert result.exit_code == 0

    def test_cli_runner_version(self) -> None:
        """Test CLI version command."""
        from typer.testing import CliRunner
        from fasthttp.cli.main import app

        runner = CliRunner()
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
