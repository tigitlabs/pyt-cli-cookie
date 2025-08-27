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
branch_prefix_release = "release/v"
branch_prefix_pr = "pr/"


BUMP_VERSION_PROVIDER = "commitizen"  # The tool used to bump versions [poetry | commitizen]


class GitFlow:
    """Collector class to manage Git flow operations."""

    def __init__(self, c: Context):
        """Initialize the GitFlow class.

        Args:
            c: The context object.
        """
        self.c = c

    def get_repo_name(self) -> str:
        """Get the name of the current Git repository."""
        return self.c.run("basename `git rev-parse --show-toplevel`", hide=True).stdout.strip()  # type: ignore

    def get_current_branch(self) -> str:
        """Get the name of the current Git branch."""
        return self.c.run("git rev-parse --abbrev-ref HEAD", hide=True).stdout.strip()  # type: ignore

    def assert_no_uncommitted(self) -> None:
        """Assert that the git working directory is clean."""
        result = self.c.run("git status --porcelain", hide=True, warn=True).stdout.strip()  # type: ignore
        if result:
            print("❌ Warning: You have uncommitted changes. Aborting.")
            sys.exit(1)
        print("✅ No uncommitted changes found.")

    def git_merge(self, head: str, message: str = "") -> None:
        """Merge the specified branches.

        Args:
            head (str): The head branch to merge into.
            message (str): The commit message for the merge. If not provided, a fast-forward merge will be performed.
        """
        if message != "":
            self.c.run(f"git merge --no-ff {head} -m '{message}'")
        else:
            self.c.run(f"git merge --ff {head}")

    def assert_merge_test(self, base: str, head: str) -> None:
        """Test if a PR would cause merge conflicts.

        Args:
            base (str): The feature/fix branch.
            head (str): The head branch
        """
        tmp_head = f"temp/{head}"
        self.git_switch_branch(head)
        self.c.run(f"git pull origin {head}")
        self.git_switch_branch(tmp_head)
        print("👟 Testing merge conflicts...\n")
        result = self.c.run(f"git merge --no-commit --no-ff {base}", hide=True, warn=True)  # type: ignore
        output = (getattr(result, "stdout", "") or "") + (getattr(result, "stderr", "") or "")  # type: ignore
        self.c.run("git merge --abort")
        self.git_switch_branch(base)
        self.c.run(f"git branch -D {tmp_head}")
        if "Automatic merge went well" in output:
            print("✅ Merge test was successful.")
        else:
            print(f"🛑Merge test {base} -> {head} failed. Resolve Merge Conflict.\nRun: git merge --no-commit {base}")
            sys.exit(1)

    def assert_version_type(self, version_type: str) -> None:
        """Assert that the version type is valid.

        Args:
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

    def get_current_version(self) -> str:
        """Get the current version from the pyproject.toml file."""
        return self.c.run("poetry version --short", hide=True).stdout.strip()  # type: ignore

    def get_new_version(self, version_type: str) -> str:
        """Get the new version based on the current version.

        Args:
            version_type (str): \
                The type of version to release (e.g., patch, minor, major, prepatch, preminor, premajor, prerelease).
        """
        self.assert_version_type(version_type)
        return self.c.run(f"poetry version {version_type} --dry-run --short", hide=True).stdout.strip()  # type: ignore

    def get_release_branch(self, version: str) -> str:
        """Get the release branch name based on the new version."""
        return f"{branch_prefix_release}{version}"

    def git_switch_branch(self, branch_name: str) -> None:
        """Switch to the specified Git branch."""
        print(f"👟 Switching to branch {branch_name}")
        exists = self.c.run(f"git branch --list {branch_name}", hide=True).stdout.strip()  # type: ignore
        if branch_name == self.get_current_branch():
            return
        if exists:
            self.c.run(f"git switch {branch_name}", hide=True)
            return
        else:
            self.c.run(f"git switch -c {branch_name}", hide=True)

    def bump_version(self, version_type: str) -> None:
        """Bump the project version."""
        self.assert_version_type(version_type)
        print("👟 Bumping version to\n")
        self.c.run(f"poetry version {version_type}")

    def get_feature_branch_name(self, feature_name: str) -> str:
        """Get the feature branch name based on the feature name."""
        return f"{branch_prefix_feature}{feature_name}"

    def get_pull_request_branch(self, feature_branch: str) -> str:
        """Get the pull request branch name based on the feature branch."""
        return f"{branch_prefix_pr}{feature_branch}"

    def get_fix_branch_name(self, fix_name: str) -> str:
        """Get the fix branch name based on the fix name."""
        return f"{branch_prefix_bugfix}{fix_name}"

    def is_feature_branch(self, branch_name: str) -> bool:
        """Check if the given branch name is a feature branch."""
        return branch_name.startswith(branch_prefix_feature)

    def is_fix_branch(self, branch_name: str) -> bool:
        """Check if the given branch name is a fix branch."""
        return branch_name.startswith(branch_prefix_bugfix)

    def switch_from(self, base: str, new: str):
        """Switch from a base branch to a new working branch.

        Args:
            base: The name of the base branch.
            new: The name of the new working branch.
        """
        self.assert_no_uncommitted()
        self.git_switch_branch(base)
        self.c.run(f"git pull origin {base}")
        self.git_switch_branch(new)

    def flow_finish(self, task_type: str):
        """Finish a feature branch.

        Args:
            c: The context object.
            task_type: The type of task to finish (e.g., feature, fix).
        """
        task_branch = self.get_current_branch()
        if task_type not in ["feature", "fix"]:
            print(f"Invalid task type: {task_type}")
            sys.exit(1)
        if task_type == "feature":
            if not self.is_feature_branch(task_branch):
                print(f"Current branch is not a feature branch: {task_branch}")
                sys.exit(1)
        elif task_type == "fix":
            if not self.is_fix_branch(task_branch):
                print(f"Current branch is not a fix branch: {task_branch}")
                sys.exit(1)
        pr_branch = self.get_pull_request_branch(task_branch)
        message = f"merge: {task_branch} -> {pr_branch}"
        self.assert_merge_test(task_branch, dev_branch)
        self.switch_from(dev_branch, pr_branch)
        if self.get_current_branch() != pr_branch:
            print(f"Failed to switch to pull request branch: {pr_branch}")
            sys.exit(1)
        self.git_merge(head=task_branch)
        self.git_merge(head=task_branch, message=message)
        ci.dev_ci(self.c)
        self.git_switch_branch(dev_branch)
        self.git_merge(head=pr_branch)
        self.c.run(f"git branch -d {task_branch}")
        self.c.run(f"git branch -d {pr_branch}")


@task
def flow_feature_start(c: Context, feature_name: str):
    """Start a new feature branch.

    Args:
        c: The context object.
        feature_name: The name for the new feature branch.
    """
    git = GitFlow(c)
    git.switch_from(dev_branch, git.get_feature_branch_name(feature_name))


@task
def flow_fix_start(c: Context, feature_name: str):
    """Start a new fix branch.

    Args:
        c: The context object.
        feature_name: The name for the new fix branch.
    """
    git = GitFlow(c)
    git.switch_from(dev_branch, git.get_feature_branch_name(feature_name))


@task
def flow_release_start(c: Context, increment: str):
    """Start a new release branch.

    - Creates a release branch from the development branch.
    - Performs merge test from dev into main.
    - Bumps the version according to the specified increment.
    - Updates the changelog for the new release.
      - Waits for user input to confirm the changelog.
    - Commits the changes for the new release.
    - Merges the release branch into the development branch.
    - Merges development changes into the main branch using squash.
    - Runs release CI checks on the main branch.
    - Tags the commit on the main branch with the new version.
    - Merges the main branch back into the development branch.
    - Pushes the changes to the remote repository.

    Args:
        c: The context object.
        increment: The version increment for the new release branch.
    """
    pass


@task
def flow_feature_finish(c: Context):
    """Finish a feature branch.

    Args:
        c: The context object.
    """
    git = GitFlow(c)
    git.flow_finish(task_type="feature")


@task
def flow_fix_finish(c: Context):
    """Finish a fix branch.

    Args:
        c: The context object.
    """
    git = GitFlow(c)
    git.flow_finish(task_type="fix")


git_ns = Collection("git")
git_ns.add_task(flow_feature_start, name="flow_feature_start")  # type: ignore
git_ns.add_task(flow_feature_finish, name="flow_feature_finish")  # type: ignore
git_ns.add_task(flow_fix_start, name="flow_fix_start")  # type: ignore
git_ns.add_task(flow_fix_finish, name="flow_fix_finish")  # type: ignore
