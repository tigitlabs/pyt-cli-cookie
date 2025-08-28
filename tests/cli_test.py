"""Tests for the cli module."""

from typer.testing import CliRunner

import template.cli
from template.cli import app

runner = CliRunner()


def test_get_version_helper() -> None:
    """Test the get_version function."""
    ver = template.cli._get_version()
    assert isinstance(ver, str)
    assert "." in ver


def test_help_arg() -> None:
    """Test the --help argument."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


def test_help_no_args() -> None:
    """Test the help message when no arguments are provided."""
    result = runner.invoke(app, [])
    assert result.exit_code == 2
    assert "Show this message and exit" in result.output


def test_get_version() -> None:
    """Test the get_version function."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "template version" in result.output
