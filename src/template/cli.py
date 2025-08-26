"""Typer CLI for Template Project."""

import os

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


@app.callback()
def main(verbose: bool = False):
    """Main entry point for the template CLI project."""
    if verbose:
        print("Will write verbose output")
        state["verbose"] = True


@app.command()
def version() -> None:
    """Show the version of template."""
    print(f"template version {_get_version()}")


if __name__ == "__main__":
    app()
