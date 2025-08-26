"""Version control tasks."""

import sys

from invoke.collection import Collection
from invoke.context import Context
from invoke.tasks import task

dev_branch = "dev"
main_branch = "main"


@task
def get_repo_name(c: Context) -> str:
    """Get the name of the current Git repository."""
    return c.run("basename `git rev-parse --show-toplevel`", hide=True).stdout.strip()  # type: ignore


def get_current_branch(c: Context) -> str:
    """Get the name of the current Git branch."""
    return c.run("git rev-parse --abbrev-ref HEAD", hide=True).stdout.strip()  # type: ignore


def assert_no_uncommitted(c) -> None:
    """Assert that the git working directory is clean."""
    result = c.run("git status --porcelain", hide=True, warn=True).stdout.strip()  # type: ignore
    if result:
        print("❌ Warning: You have uncommitted changes. Aborting.")
        sys.exit(1)
    print("✅ No uncommitted changes found.")


def assert_merge_test(c: Context, base: str, head: str) -> None:
    """Test if a PR would cause merge conflicts.

    Args:
        c (Context): The Invoke context.
        base (str): The feature/fix branch.
        head (str): The head branch
    """
    tmp_head = f"temp/{head}"
    git_switch_branch(c, head)
    c.run(f"git pull origin {head}")
    git_switch_branch(c, tmp_head)
    print("👟 Testing merge conflicts...\n")
    result = c.run(f"git merge --no-commit --no-ff {base}", hide=True, warn=True)  # type: ignore
    output = (getattr(result, "stdout", "") or "") + (getattr(result, "stderr", "") or "")  # type: ignore
    c.run("git merge --abort")
    git_switch_branch(c, base)
    c.run(f"git branch -D {tmp_head}")
    if "Automatic merge went well" in output:
        print("✅ Merge test was successful.")
    else:
        print(f"🛑Merge test {base} -> {head} failed. Resolve Merge Conflict.\nRun: git merge --no-commit {base}")
        sys.exit(1)


def assert_version_type(c: Context, version_type: str) -> None:
    """Assert that the version type is valid.

    Args:
        c (Context): The Invoke context.
        version_type (str): The version type to check.
    """
    valid_types = ["patch", "minor", "major", "prepatch", "preminor", "premajor", "prerelease"]
    if version_type not in valid_types:
        print(f"❌ Invalid version type: {version_type}. Must be one of: {', '.join(valid_types)}.")
        sys.exit(1)


def get_current_version(c: Context) -> str:
    """Get the current version from the pyproject.toml file."""
    return c.run("poetry version --short", hide=True).stdout.strip()  # type: ignore


def get_new_version(c: Context, version_type: str) -> str:
    """Get the new version based on the current version.

    Args:
        c (Context): The Invoke context.
        version_type (str): \
            The type of version to release (e.g., patch, minor, major, prepatch, preminor, premajor, prerelease).
    """
    assert_version_type(c, version_type)
    return c.run(f"poetry version {version_type} --dry-run --short", hide=True).stdout.strip()  # type: ignore


def get_release_branch(version: str) -> str:
    """Get the release branch name based on the new version."""
    return f"release/v{version}"


def git_switch_branch(c: Context, branch_name: str) -> None:
    """Switch to the specified Git branch."""
    print(f"👟 Switching to branch {branch_name}")
    exists = c.run(f"git branch --list {branch_name}", hide=True).stdout.strip()  # type: ignore
    if branch_name == get_current_branch(c):
        return
    if exists:
        c.run(f"git switch {branch_name}")
        return
    else:
        c.run(f"git switch -c {branch_name}")


def bump_version(c: Context, version_type: str) -> None:
    """Bump the project version."""
    assert_version_type(c, version_type)
    print("👟 Bumping version to\n")
    c.run(f"poetry version {version_type}")


@task
def commit_feat(c: Context, message: str):
    """Commit a feature change.

    Args:
        c: The context object.
        message: The commit message.
    """
    c.run("git commit -m 'feat: add new feature'")


@task
def commit_tool(c: Context, message: str):
    """Commit a tool change.

    Args:
        c: The context object.
        message: The commit message.
    """
    c.run("git commit -m 'tool: add new feature'")


git_ns = Collection("git")
git_ns.add_task(commit_feat, name="commit_feat")  # type: ignore
git_ns.add_task(commit_tool, name="commit_tool")  # type: ignore
