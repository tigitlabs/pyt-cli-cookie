"""Typer CLI for Template Project."""

import importlib.metadata
import sys
from datetime import datetime
from typing import Annotated

import typer
from loguru import logger

logger.remove()

from template.config import config, config_app  # noqa: E402

state = {"verbose": False}


def _configure_logging() -> None:
    logger.remove()
    log_level = config.model.log_level
    if state["verbose"] is True:
        log_level = "DEBUG"
    log_filepath = config.model.logs_dir / datetime.now().strftime("%Y-%m-%d.log")
    logger.add(log_filepath, level="DEBUG", retention="10 days", rotation="00:00")
    logger.add(sys.stderr, format="<green>{time}</green> | <level>{message}</level>", level=log_level)


def _get_version() -> str:
    """Get version from package metadata.

    Returns:
        str: The version of the project.
    """
    version = importlib.metadata.version("pyt-template")
    logger.debug(f"Loaded version {version} from package metadata")
    return version


def version_callback(value: bool):
    """Print the version."""
    if value:
        logger.debug("Version callback called")
        print(f"template version {_get_version()}")
        raise typer.Exit(0)


def verbose_callback(verbose: bool):
    """Callback for verbose flag."""
    if verbose:
        print("Will write verbose output")
        state["verbose"] = True


app = typer.Typer(
    name="template",
    no_args_is_help=True,
    help="Template - A CLI template project",
)
app.add_typer(config_app)


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
    """Main entry point for the CLI."""
    _configure_logging()
    if ctx.invoked_subcommand is None:
        print("No subcommand invoked")
    else:
        print(f"Subcommand invoked: {ctx.info_name}")
