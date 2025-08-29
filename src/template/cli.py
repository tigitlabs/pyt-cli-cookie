"""Typer CLI for Template Project."""

import os
from typing import Annotated

import typer

state = {"verbose": False}

app = typer.Typer(
    name="template",
    no_args_is_help=True,
    help="Template - A CLI template project",
)


def _get_version() -> str:
    """Get version from pyproject.toml.

    Returns:
        str: The version of the project.
    """
    try:
        import tomllib

        pyproject_path = os.path.join(os.path.dirname(__file__), "..", "..", "pyproject.toml")
        pyproject_path = os.path.abspath(pyproject_path)
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data["project"]["version"]
    except ModuleNotFoundError:
        return ""


def version_callback(value: bool):
    """Print the version."""
    if value:
        print(f"template version {_get_version()}")
        raise typer.Exit(0)


def verbose_callback(verbose: bool):
    """Callback for verbose flag."""
    if verbose:
        print("Will write verbose output")
        state["verbose"] = True


@app.command()
def version() -> None:
    """Show the version of template."""
    version_callback(True)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            callback=verbose_callback,
            help="Enable verbose output.",
            rich_help_panel="Customization and Utils",
        ),
    ] = False,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Print version information.",
            rich_help_panel="Customization and Utils",
        ),
    ] = False,
):
    """Main entry point for the template CLI project."""
    if ctx.invoked_subcommand is None:
        print("No subcommand invoked")
    else:
        print(f"Subcommand invoked: {ctx.info_name}")
