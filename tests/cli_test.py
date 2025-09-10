"""Tests for the cli module."""

import subprocess
import sys

from typer.testing import CliRunner

import template.cli as cli

runner = CliRunner()


def test_get_version_helper() -> None:
    """Test the get_version function."""
    ver = cli._get_version()
    print(f"Version: {ver}")
    assert isinstance(ver, str)
    assert "." in ver


def test_help_arg() -> None:
    """Test the --help argument."""
    result = runner.invoke(cli.app, ["--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


def test_help_no_args() -> None:
    """Test the help message when no arguments are provided."""
    result = runner.invoke(cli.app, [])
    assert result.exit_code == 2
    assert "Show this message and exit" in result.output


def test_get_version() -> None:
    """Test the get_version function."""
    result = runner.invoke(cli.app, ["version"])
    assert result.exit_code == 0
    assert "template version" in result.output


def test_version_flag() -> None:
    """Test the --version flag."""
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert "template version" in result.output


def test_verbose_flag() -> None:
    """Test the --verbose flag."""
    result = runner.invoke(cli.app, ["--verbose", "version"])
    assert result.exit_code == 0
    assert "Will write verbose output" in result.output


def test_ctx_context() -> None:
    """Test if the main callback context is set correctly."""
    result = runner.invoke(cli.app, ["version"])
    assert result.exit_code == 0
    assert "Subcommand invoked" in result.output

    result = runner.invoke(cli.app, ["--verbose"])
    assert result.exit_code == 0
    assert "No subcommand invoked" in result.output


def test_main_py_entrypoint():
    """Test the __main__.py entry point."""
    result = subprocess.run(
        [sys.executable, "-m", "template", "--help"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    assert result.returncode == 0
    assert "Show this message and exit" in result.stdout
