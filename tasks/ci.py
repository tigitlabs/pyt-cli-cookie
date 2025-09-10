"""Invoke tasks for managing the project."""

from invoke.collection import Collection
from invoke.context import Context
from invoke.tasks import task

from tasks import docker, docs, github_actions, pre_commit, python


@task
def dev_ci(c: Context) -> None:
    """Run tests that run quickly."""
    pre_commit.spell_check_commit_msg(c)
    pre_commit.pre_commit(c)
    docs.ci_docs(c)
    python.test_static(c)
    python.test_unit(c)


@task
def full_ci(c: Context) -> None:
    """Run all CI checks."""
    c.run("git clean -fdx -e .devcontainer/.github_token")
    pre_commit.ci_pre_commit(c)
    docs.ci_docs(c)
    python.ci_python(c)
    github_actions.ci(c)
    docker.ci_docker(c)


ci_ns = Collection("ci")
ci_ns.add_task(dev_ci, name="dev")  # type: ignore[arg-type]
ci_ns.add_task(full_ci, name="full")  # type: ignore[arg-type]
