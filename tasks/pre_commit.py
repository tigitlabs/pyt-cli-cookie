"""pre-commit workflow tasks."""

from invoke.collection import Collection
from invoke.context import Context
from invoke.tasks import task


@task
def update_hooks(c: Context) -> None:
    """Update the pre-commit hooks."""
    c.run("pre-commit autoupdate")
    c.run("pre-commit validate-config")
    c.run("pre-commit validate-manifest")


@task
def pre_commit(c: Context) -> None:
    """Run the pre-commit hooks."""
    print("\n👟 Running pre-commit hooks\n")
    c.run("pre-commit run --all-files", pty=True)


@task
def ci_pre_commit(c: Context) -> None:
    """Run the pre-commit tasks as part of the CI pipeline."""
    update_hooks(c)
    pre_commit(c)


pre_commit_ns = Collection("pre_commit")
pre_commit_ns.add_task(pre_commit, name="run")  # type: ignore[arg-type]
pre_commit_ns.add_task(update_hooks, name="update")  # type: ignore[arg-type]
pre_commit_ns.add_task(ci_pre_commit, name="ci")  # type: ignore[arg-type]
