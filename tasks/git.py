"""Version control tasks."""

import sys

from invoke.collection import Collection
from invoke.context import Context
from invoke.tasks import task

from tasks import ci

dev_branch = "dev"
main_branch = "main"
branch_prefix_feature = "feat/"
branch_prefix_bugfix = "fix/"

BUMP_VERSION_PROVIDER = "commitizen"  # The tool used to bump versions [poetry | commitizen]


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


def git_merge(c: Context, head: str, message: str = "") -> None:
    """Merge the specified branches.

    Args:
        c (Context): The Invoke context.
        head (str): The head branch to merge into.
        message (str): The commit message for the merge. If not provided, a fast-forward merge will be performed.
    """
    if message != "":
        c.run(f"git merge --no-ff {head} -m '{message}'")
    else:
        c.run(f"git merge --ff {head}")


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
    if BUMP_VERSION_PROVIDER == "poetry":
        valid_types = ["patch", "minor", "major", "prepatch", "preminor", "premajor", "prerelease"]
    elif BUMP_VERSION_PROVIDER == "commitizen":
        valid_types = ["PATCH", "MINOR", "MAJOR"]
    else:
        raise ValueError(f"Unknown BUMP_VERSION_PROVIDER: {BUMP_VERSION_PROVIDER}")
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


def get_feature_branch_name(feature_name: str) -> str:
    """Get the feature branch name based on the feature name."""
    return f"{branch_prefix_feature}{feature_name}"


def get_pull_request_branch(feature_branch: str) -> str:
    """Get the pull request branch name based on the feature branch."""
    return f"pr/{feature_branch}"


def is_feature_branch(branch_name: str) -> bool:
    """Check if the given branch name is a feature branch."""
    return branch_name.startswith(branch_prefix_feature)


def switch_from_dev(c: Context, branch_name: str):
    """Switch from the development branch to a feature branch.

    Args:
        c: The context object.
        branch_name: The name of the feature branch.
    """
    assert_no_uncommitted(c)
    git_switch_branch(c, dev_branch)
    c.run(f"git pull origin {dev_branch}")
    git_switch_branch(c, branch_name)


@task
def flow_feature_start(c: Context, feature_name: str):
    """Start a new feature branch.

    Args:
        c: The context object.
        feature_name: The name for the new feature branch.
    """
    switch_from_dev(c, branch_name=get_feature_branch_name(feature_name))


@task
def flow_feature_finish(c: Context):
    """Finish a feature branch.

    Args:
        c: The context object.
    """
    feat_branch = get_current_branch(c)
    if not is_feature_branch(feat_branch):
        print(f"Current branch is not a feature branch: {feat_branch}")
        sys.exit(1)
    pr_branch = get_pull_request_branch(feat_branch)
    message = f"merge: {feat_branch} -> {pr_branch}"
    assert_merge_test(c, feat_branch, dev_branch)
    switch_from_dev(c, branch_name=pr_branch)
    if get_current_branch(c) != pr_branch:
        print(f"Failed to switch to pull request branch: {pr_branch}")
        sys.exit(1)
    git_merge(c, head=feat_branch)
    git_merge(c, head=feat_branch, message=message)
    ci.dev_ci(c)
    git_switch_branch(c, dev_branch)
    git_merge(c, head=pr_branch)
    c.run(f"git branch -d {feat_branch}")
    c.run(f"git branch -d {pr_branch}")


git_ns = Collection("git")
git_ns.add_task(flow_feature_start, name="flow_feature_start")  # type: ignore
git_ns.add_task(flow_feature_finish, name="flow_feature_finish")  # type: ignore
git_ns.add_task(commit_feat, name="commit_feat")  # type: ignore
git_ns.add_task(commit_tool, name="commit_tool")  # type: ignore
