"""Github Actions workflow tasks."""

from invoke.collection import Collection
from invoke.context import Context
from invoke.tasks import task

ON_PUSH_YML = ".github/workflows/on_push.yml"


def act(c: Context, cmd: str) -> None:
    """Run a GitHub Action command."""
    c.run(f"gh act {cmd}")


@task
def version(c: Context) -> None:
    """Show the version of the Nectos act."""
    act(c, " --version")


@task
def on_push(c: Context) -> None:
    """Trigger the on_push GitHub Action."""
    act(c, "push")


@task
def show_lists(c: Context) -> None:
    """Show the list of available GitHub Actions."""
    act(c, "--list")


act_ns = Collection("act")
act_ns.add_task(version, name="version")  # type: ignore[arg-type]
act_ns.add_task(on_push, name="on_push")  # type: ignore[arg-type]
act_ns.add_task(show_lists, name="list")  # type: ignore[arg-type]
