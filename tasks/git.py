"""Version control tasks."""

import json
import sys

from invoke.collection import Collection
from invoke.context import Context
from invoke.tasks import task

from tasks import ci

readme_file = "README.md"
dev_branch = "dev"
main_branch = "main"
branch_prefix_feature = "feat/"
commit_prefix_feature = "feat:"
branch_prefix_bugfix = "fix/"
commit_prefix_bugfix = "fix:"
branch_prefix_release = "release/"
commit_prefix_release = "release:"
branch_prefix_pr = "pr/"

BUMP_EMOJI = "🔖"
BUMP_VERSION_PROVIDER = "commitizen"  # The tool used to bump versions [poetry | commitizen]


class GithubCli:
    """Collector class to manage GitHub CLI operations."""

    def __init__(self, c: Context):
        """Initialize the GithubCli class.

        Args:
            c: The context object.
        """
        self.c = c

    def assert_github_cli(self) -> None:
        """Assert that the GitHub CLI is installed and authenticated."""
        result = self.c.run("gh auth status --active", hide=True, warn=True)
        if result.failed:  # type: ignore
            print("❌ Warning: GitHub CLI is not authenticated. Aborting.")
            sys.exit(1)
        print("✅ GitHub CLI is authenticated.")

    def create_label(self, label_name: str, description: str) -> None:
        """Create a GitHub label if it does not exist."""
        result = self.c.run("gh label list --json name", hide=True, warn=True)
        existing_labels = [label["name"] for label in json.loads(result.stdout)]  # type: ignore
        if label_name in existing_labels:
            print(f"✅ Label '{label_name}' already exists.")
        else:
            self.c.run(f"gh label create {label_name} --description '{description}'")
            print(f"✅ Created label '{label_name}'.")

    def create_pr(self, head_branch: str, base_branch: str, title: str, body: str) -> None:
        """Create a pull request.

        Args:
            head_branch (str): The feature/fix branch.
            base_branch (str): The base branch to merge into.
            title (str): The title of the pull request.
            body (str): The body of the pull request.
        """
        cmd = f"gh pr create --head {head_branch} --base {base_branch} --title '{title}' --body '{body}'"
        print("👟 Creating PR")
        self.c.run(cmd)


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

    def merge_test(self, base: str, head: str) -> None:
        """Test if a PR would cause merge conflicts.

        Args:
            base (str): The feature/fix branch.
            head (str): The head branch
        """
        tmp_head = f"temp/{head}"
        self.git_switch_branch(head)
        self.c.run(f"git pull origin {head}")
        self.git_switch_branch(tmp_head)
        print(f"👟 Testing merge conflicts {head} -> {base}")
        result = self.c.run(f"git merge --no-commit --no-ff {base}", hide=True, warn=True)  # type: ignore
        output = (getattr(result, "stdout", "") or "") + (getattr(result, "stderr", "") or "")  # type: ignore
        self.c.run("git merge --abort", hide=True, warn=True)
        self.git_switch_branch(base)
        self.branch_delete(tmp_head)
        if "Automatic merge went well" in output:
            print("✅ Merge test was successful.")
        else:
            print(f"🛑Merge test {base} -> {head} failed. Resolve Merge Conflict.\nRun: git merge --no-commit {base}")
            sys.exit(1)

    def assert_version_type(self, version_type: str, provider: str) -> None:
        """Assert that the version type is valid.

        Args:
            version_type (str): The version type to check.
            provider (str): The provider to check against.
        """
        if provider == "poetry":
            valid_types = ["patch", "minor", "major", "prepatch", "preminor", "premajor", "prerelease"]
        elif provider == "commitizen":
            valid_types = ["patch", "minor", "major"]
        else:
            raise ValueError(f"Unknown BUMP_VERSION_PROVIDER: {provider}")
        if version_type not in valid_types:
            print(f"❌ Invalid version type: {version_type}. Must be one of: {', '.join(valid_types)}.")
            sys.exit(1)

    def get_current_version(self) -> str:
        """Get the current version from the pyproject.toml file."""
        return self.c.run("poetry version --short", hide=True).stdout.strip()  # type: ignore

    def get_new_pip_version(self, version_type: str) -> str:
        """Get the new version of the package based on the current version.

        Args:
            version_type (str): \
                The type of version to release (e.g., patch, minor, major, prepatch, preminor, premajor, prerelease).
        """
        self.assert_version_type(version_type, BUMP_VERSION_PROVIDER)
        if BUMP_VERSION_PROVIDER == "commitizen":
            version_type = version_type.lower()
        self.assert_version_type(version_type, "poetry")
        return self.c.run(f"poetry version {version_type} --dry-run --short", hide=True).stdout.strip()  # type: ignore

    def get_new_version(self, version_type: str) -> str:
        """Get the new version based on the current version.

        This is the version with a prefix.

        Args:
            version_type (str): \
                The type of version to release (e.g., patch, minor, major, prepatch, preminor, premajor, prerelease).
        """
        v = "v" + self.get_new_pip_version(version_type)
        return v

    def get_release_branch(self, version: str) -> str:
        """Get the release branch name based on the new version."""
        return f"{branch_prefix_release}{version}"

    def git_switch_branch(self, branch_name: str) -> None:
        """Switch to the specified Git branch."""
        print(f"👟 Switching to branch {branch_name}")
        self.c.run("git fetch origin")
        exists_locally = self.c.run(f"git branch --list {branch_name}", hide=True).stdout.strip()  # type: ignore
        remote_branch = f"origin/{branch_name}"
        remote_exists = self.c.run(f"git ls-remote --heads origin {branch_name}", hide=True).stdout.strip()  # type: ignore
        if exists_locally:
            self.c.run(f"git switch {branch_name}", hide=True)
            if remote_exists:
                print(f"Updating {branch_name} from {remote_branch}")
                self.c.run(f"git pull origin {branch_name}", hide=True)
        else:
            if remote_exists:
                print(f"Creating and tracking {branch_name} from {remote_branch}")
                self.c.run(f"git switch --track {remote_branch}", hide=True)
            else:
                print(f"Creating new branch {branch_name} from current HEAD")
                self.c.run(f"git switch -c {branch_name}", hide=True)

    def update_readme_version(self, new_version: str) -> None:
        """Update the version in the README file."""
        print(f"👟 Updating README version to {new_version}\n")
        try:
            import re

            pattern = r'^VERSION="([^"]+)"'
            replacement = f'VERSION="{new_version}"'
            with open(readme_file) as file:
                content = file.read()
                new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                if new_content == content:
                    print(f"Error: Could not find or update the 'VERSION' variable in '{readme_file}'.")
                    sys.exit(1)
            with open(readme_file, "w") as file:
                file.write(new_content)
        except FileNotFoundError:
            print(f"Error: The file '{readme_file}' does not exist.")
            sys.exit(1)

    def update_changelog(self, new_version: str) -> None:
        """Update the changelog for the new version."""
        print(f"👟 Updating changelog for version {new_version}")
        self.c.run(f"cz changelog --unreleased-version={new_version}")

    def bump_version(self, increment: str, provider: str) -> None:
        """Bump the project version."""
        self.assert_version_type(increment, provider)
        new_tag_version = self.get_new_version(increment)
        new_pip_version = self.get_new_pip_version(increment)
        print(f"👟 Bumping version to {new_tag_version}\n")
        if provider == "poetry":
            self.c.run(f"poetry version {increment}")
        elif provider == "commitizen":
            self.update_changelog(new_tag_version)
            self.c.run(f"cz bump --files-only --increment {increment.upper()}")
        else:
            raise ValueError(f"Unknown BUMP_VERSION_PROVIDER: {provider}")
        self.update_readme_version(new_pip_version)

    def get_feature_branch_name(self, feature_name: str) -> str:
        """Get the feature branch name based on the feature name."""
        return f"{branch_prefix_feature}{feature_name}"

    def get_pull_request_branch(self, feature_branch: str) -> str:
        """Get the pull request branch name based on the feature branch."""
        return f"{branch_prefix_pr}{feature_branch}"

    def get_fix_branch_name(self, fix_name: str) -> str:
        """Get the fix branch name based on the fix name."""
        return f"{branch_prefix_bugfix}{fix_name}"

    def get_release_branch_name(self, version: str) -> str:
        """Get the release branch name based on the new version."""
        return f"{branch_prefix_release}{version}"

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

    def branch_delete(self, branch_name: str) -> None:
        """Delete the specified Git branch."""
        print(f"👟 Deleting branch {branch_name}")
        self.c.run(f"git branch -D {branch_name}", hide=True, warn=True)

    def git_pull(self, branch: str) -> None:
        """Pull the latest changes from the remote repository."""
        print("👟 Pulling latest changes from remote")
        self.c.run(f"git pull origin {branch}", hide=True)

    def git_tag(self, version: str) -> None:
        """Create a Git tag for the specified version."""
        print(f"👟 Creating Git tag {version}")
        self.c.run(f"git tag {version}")

    def git_push(self, branch: str, tag: str = "") -> None:
        """Push the specified branch to the remote repository.

        If a tag is provided, it will be pushed as well.

        Args:
            branch: The name of the branch to push.
            tag: The tag to push (optional).
        """
        print(f"👟 Pushing branch {branch} to remote")
        cmd = f"git push origin {branch}"
        if tag != "":
            cmd = f"git push origin {branch} --atomic {tag}"
        self.c.run(cmd)

    def git_tag_push(self, version: str) -> None:
        """Push the Git tag to the remote repository."""
        print(f"👟 Pushing Git tag {version}")
        self.c.run(f"git push origin {version}")

    def flow_finish(self, task_type: str, pr_title: str = "") -> None:
        """Finish a feature branch.

        This method handles merge checks before merging the feature branch or creating a pull request.

        Args:
            task_type: The type of task to finish (e.g., feature, fix).
            pr_title: The title of the pull request.
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
        self.merge_test(task_branch, dev_branch)
        self.switch_from(dev_branch, pr_branch)
        if self.get_current_branch() != pr_branch:
            print(f"Failed to switch to pull request branch: {pr_branch}")
            sys.exit(1)
        self.git_merge(head=task_branch)
        ci.dev_ci(self.c)
        if pr_title == "":
            self.git_switch_branch(dev_branch)
            self.git_merge(head=pr_branch)
            self.git_push(dev_branch)
        else:
            self.git_push(pr_branch)
            github = GithubCli(self.c)
            github.assert_github_cli()
            github.create_pr(
                head_branch=pr_branch,
                base_branch=dev_branch,
                title=pr_title,
                body="",
            )
        """
        If the pr_branch was merged successfully, delete the branch with -d.
        The working branch has to be deleted with -D because it is not fully merged.
        """
        self.branch_delete(pr_branch)
        self.branch_delete(task_branch)

    def flow_release_start(self, increment: str):
        """Start a new release.

        Args:
            increment: The version increment for the new release branch.
        """
        self.assert_version_type(increment, BUMP_VERSION_PROVIDER)
        new_version = self.get_new_version(increment)
        release_branch = self.get_release_branch_name(new_version)
        if self.get_current_branch() != dev_branch:
            print(f"❌ You must be on the {dev_branch} branch to start a release.")
            sys.exit(1)
        self.git_pull(dev_branch)
        print(f"New version for release: {new_version}")
        self.assert_no_uncommitted()
        self.git_switch_branch(release_branch)
        print("\n👟 Bumping version & updating changelog\n")
        # Perform bump version tasks
        self.bump_version(increment, BUMP_VERSION_PROVIDER)
        self.c.run("git add pyproject.toml")
        self.c.run("git add docs/changelog.md")
        self.c.run(f"git add {readme_file}")
        self.c.run("git commit -m 'docs: update changelog for release'")
        print(
            "🔥 The changelog has been updated and committed.\n"
            "Please review and commit them with: git commit --amend --no-edit"
        )
        print("❓️ Do you want to continue the release process? (y/n)")
        if input().strip().lower() != "y":
            print("❌ Release process aborted.")
            sys.exit(1)
        # Test and merge into dev
        ci.dev_ci(self.c)
        self.merge_test(release_branch, dev_branch)
        self.git_switch_branch(dev_branch)
        self.git_merge(head=release_branch, message=f"merge: {release_branch} -> {dev_branch}")
        self.merge_test(dev_branch, main_branch)
        # Merge into main and tag
        self.git_switch_branch(main_branch)
        self.git_pull(main_branch)
        self.c.run(f"git merge --squash {dev_branch}")
        self.c.run(f"git commit -m '{BUMP_EMOJI}: {release_branch}'")
        self.git_tag(version=new_version)
        # Merge back into dev and cleanup
        self.git_switch_branch(dev_branch)
        self.git_merge(head=main_branch, message=f"merge: {main_branch}/{new_version} -> {dev_branch}")
        self.branch_delete(release_branch)
        print("✅ Release flow successful. After review, push the changes with:\ninv git.flow-release-finish")

    def flow_release_create_pr(self, increment: str):
        """Start a new release.

        This method does following steps:
        - Creates a release branch from the development branch.
        - Performs the bump version tasks according to the specified increment.
        - Merges the release branch into a temporary main branch.
        - Runs release CI checks on the temporary main branch.
        - Pushes the release branch to the remote repository.
        - Creates a pull request from the release branch into the main branch.
        - Cleans up local branches.

        Args:
            increment: The version increment for the new release branch.
        """
        self.assert_version_type(increment, BUMP_VERSION_PROVIDER)
        new_version = self.get_new_version(increment)
        release_branch = self.get_release_branch_name(new_version)
        tmp_main_branch = f"temp_{new_version}/{main_branch}"
        if self.get_current_branch() != dev_branch:
            print(f"❌ You must be on the {dev_branch} branch to start a release.")
            sys.exit(1)
        self.assert_no_uncommitted()
        print(f"New version for release: {new_version}")

        # Perform bump version tasks
        self.git_pull(dev_branch)
        self.git_switch_branch(release_branch)
        print("👟 Bumping version & updating changelog")
        self.bump_version(increment, BUMP_VERSION_PROVIDER)
        self.c.run("git add pyproject.toml")
        self.c.run("git add docs/changelog.md")
        self.c.run(f"git add {readme_file}")
        self.c.run("git commit -m 'docs: update changelog for release'")
        print(
            "🔥 The changelog has been updated and committed.\n"
            "Please review and commit them with: git commit --amend --no-edit"
        )
        print("❓️ Do you want to continue the release process? (y/n)")
        if input().strip().lower() != "y":
            print("❌ Release process aborted.")
            sys.exit(1)

        # Merge test and run CI on main branch
        self.git_switch_branch(main_branch)
        self.git_pull(main_branch)
        self.git_switch_branch(tmp_main_branch)
        self.git_merge(head=release_branch, message=f"merge: {release_branch} -> {tmp_main_branch}")
        ci.dev_ci(self.c)

        # Create PR
        self.git_switch_branch(release_branch)
        self.git_push(release_branch)
        github = GithubCli(self.c)
        github.assert_github_cli()
        github.create_pr(
            head_branch=release_branch,
            base_branch=main_branch,
            title=f"{BUMP_EMOJI} Release {new_version}",
            body=f"This PR merges the {release_branch} branch into the {main_branch} branch.",
        )
        # Cleanup local branches
        self.git_switch_branch(dev_branch)
        self.branch_delete(tmp_main_branch)
        self.branch_delete(release_branch)

    def flow_release_finish(self) -> None:
        """Finish the release process."""
        self.assert_no_uncommitted()
        tag = "v" + self.get_current_version()
        result = self.c.run(f"git tag --list {tag}", hide=True).stdout.strip()  # type: ignore
        if tag not in result:
            print(f"🛑 The tag {tag} does not exist. Are you on the correct branch?")
            sys.exit(1)
        self.git_push(dev_branch)
        self.git_push(main_branch, tag)


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
def flow_fix_start(c: Context, fix_name: str):
    """Start a new fix branch.

    Args:
        c: The context object.
        fix_name: The name for the new fix branch.
    """
    git = GitFlow(c)
    git.switch_from(dev_branch, git.get_fix_branch_name(fix_name))


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
    git = GitFlow(c)
    git.flow_release_start(increment)


@task
def flow_release_finish(c: Context):
    """Finish a release branch.

    Args:
        c: The context object.
    """
    git = GitFlow(c)
    git.flow_release_finish()


@task
def flow_release_pr(c: Context, increment: str):
    """Create a pull request for the next release.

    Args:
        c: The context object.
        increment: The version increment for the new release branch.
    """
    git = GitFlow(c)
    git.flow_release_create_pr(increment)


@task
def flow_feature_finish(c: Context):
    """Finish a feature branch.

    Args:
        c: The context object.
    """
    git = GitFlow(c)
    git.flow_finish(task_type="feature")


@task
def flow_feature_pr(c: Context, pr_title: str):
    """Create a pull request for the current feature branch.

    Args:
        c: The context object.
        pr_title: The title of the pull request, without the prefix.
    """
    git = GitFlow(c)
    if pr_title.startswith(commit_prefix_feature):
        print(f"🛑 Remove the {commit_prefix_feature} prefix from the PR title.")
        sys.exit(1)
    pr_title = "feat: " + pr_title.strip()
    c.run(f"cz check --message '{pr_title}'")
    git.flow_finish(task_type="feature", pr_title=pr_title)


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
git_ns.add_task(flow_feature_pr, name="flow_feature_pr")  # type: ignore
git_ns.add_task(flow_fix_start, name="flow_fix_start")  # type: ignore
git_ns.add_task(flow_fix_finish, name="flow_fix_finish")  # type: ignore
git_ns.add_task(flow_release_start, name="flow_release_start")  # type: ignore
git_ns.add_task(flow_release_finish, name="flow_release_finish")  # type: ignore
git_ns.add_task(flow_release_pr, name="flow_release_pr")  # type: ignore
