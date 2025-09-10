"""Github Actions workflow tasks."""

from invoke.collection import Collection
from invoke.context import Context
from invoke.tasks import task

python_ci_yml = ".github/workflows/python-ci.yml"
PRE_COMMIT_YML = ".github/workflows/pre-commit.yml"


class Act:
    """Class to run GitHub Actions commands using act."""

    def __init__(self, context: Context) -> None:
        """Initialize the Act class with a context."""
        self.context = context

    def run(self, cmd: str) -> None:
        """Run a GitHub Action command."""
        self.context.run(f"gh act {cmd}")

    def list(self) -> None:
        """List available GitHub Actions."""
        self.run("--list")

    def run_job(self, job: str) -> None:
        """Run a specific GitHub Action job."""
        self.run(f"--job {job}")


@task
def version(c: Context) -> None:
    """Show the version of the Nectos act."""
    act = Act(c)
    act.run("--version")


@task
def on_push(c: Context) -> None:
    """Trigger the on_push GitHub Action."""
    act = Act(c)
    act.run("push")


@task
def show_lists(c: Context) -> None:
    """Show the list of available GitHub Actions."""
    act = Act(c)
    act.list()


@task
def ci(c: Context) -> None:
    """Run the CI GitHub Action.

    This will run all jobs that are supported by act.
    """
    act = Act(c)
    act.run_job("python-ci")
    act.run_job("pre-commit")


act_ns = Collection("act")
act_ns.add_task(version, name="version")  # type: ignore[arg-type]
act_ns.add_task(on_push, name="on_push")  # type: ignore[arg-type]
act_ns.add_task(show_lists, name="list")  # type: ignore[arg-type]
act_ns.add_task(ci, name="ci")  # type: ignore[arg-type]
