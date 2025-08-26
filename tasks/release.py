"""Release workflow tasks."""

import json
import sys

from invoke.collection import Collection
from invoke.context import Context
from invoke.tasks import task

from tasks import ci

dev_branch = "dev"
main_branch = "main"
change_log_file = "docs/changelog.md"


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


def assert_github_cli(c: Context) -> None:
    """Assert that the GitHub CLI is installed and authenticated."""
    result = c.run("gh auth status --active", hide=True, warn=True)
    if result.failed:  # type: ignore
        print("❌ Warning: GitHub CLI is not authenticated. Aborting.")
        sys.exit(1)
    print("✅ GitHub CLI is authenticated.")


def create_label(c: Context, label_name: str, description: str) -> None:
    """Create a GitHub label if it does not exist."""
    result = c.run("gh label list --json name", hide=True, warn=True)
    existing_labels = [label["name"] for label in json.loads(result.stdout)]  # type: ignore
    if label_name in existing_labels:
        print(f"✅ Label '{label_name}' already exists.")
    else:
        c.run(f"gh label create {label_name} --description '{description}'")
        print(f"✅ Created label '{label_name}'.")


def get_current_version(c: Context) -> str:
    """Get the current version from the pyproject.toml file."""
    return c.run("poetry version --short", hide=True).stdout.strip()  # type: ignore


def get_new_version(c: Context, version_type: str) -> str:
    """Get the new version based on the current version.

    Args:
        c (Context): The Invoke context.
        version_type (str): The type of version to release (e.g.,
        patch, minor, major, prepatch, preminor, premajor, prerelease).
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


def get_latest_tag(c: Context) -> str:
    """Get the latest Git tag."""
    return c.run("git describe --tags --abbrev=0", hide=True).stdout.strip()  # type: ignore


@task
def release(c: Context) -> None:
    """Create a new release.

    - create a release branch from main'release/<version>'
    - merge dev into release branch using theirs and squash
    - Commit merge
    - Create changelog
    - Run CI
    - create a new git tag
    - create a PR to dev to auto merge the latest commit
    -- push the changes to the remote repository
    -- create a PR into `main`

    Args:
        c (Context): The Invoke context.
    """
    version = get_current_version(c)
    release_branch = get_release_branch(version)
    tag = f"v{version}"

    print(f"\n👟 Creating {version} release\n")
    print("Do you want to proceed? [y/n]")
    if input().strip().lower() != "y":
        print("Aborting release.")
        sys.exit(0)
    assert_no_uncommitted(c)
    git_switch_branch(c, dev_branch)
    c.run(f"git pull origin {dev_branch}")
    git_switch_branch(c, release_branch)
    c.run(f"git-cliff --tag {tag}")
    c.run(f"git add {change_log_file}")
    print(f"❓️ Created {change_log_file}: Do you want to commit it? [y/n]")
    if input().strip().lower() == "y":
        c.run("git commit -m 'doc: update changelog.md'")
        c.run(f"git-cliff --tag {tag}")
        c.run(f"git add {change_log_file}")
        c.run("git commit --amend --no-edit")
        c.run(f"git tag -a {tag} -m '🔖 Release {tag}'")
        git_switch_branch(c, main_branch)
        c.run(f"git pull origin {main_branch}")
        c.run(f"git reset --hard {tag}")
        c.run(f"git push --set-upstream origin {main_branch} --force")
        c.run(f"git push origin {tag}")
        git_switch_branch(c, dev_branch)
        c.run(f"git merge {release_branch}")
        c.run(f"git branch -D {release_branch}")
        c.run(f"git push origin {dev_branch}")
    else:
        print(
            "Aborting commit.\n"
            "Update the changelog file.\n"
            "Then run:\n"
            f"git add {change_log_file}\n"
            "git commit -m 'chore: update changelog.md'\n"
            f"git tag -a {tag} -m '🔖 Release {tag}'\n"
            f"git switch {main_branch}\n"
            f"git pull origin {main_branch}\n"
            f"git reset --hard {tag}\n"
            f"git push --set-upstream origin {main_branch} --force\n"
            f"git push origin {tag}\n"
            f"git switch {dev_branch}\n"
            f"git merge {release_branch}\n"
            f"git push origin {dev_branch}\n"
        )
        sys.exit(0)


@task
def create_pr(c: Context, type: str, title: str, version_type: str = "patch"):
    """Create a PR based on the type.

    - Bumps the version of the package.
    - Pushes changes.
    - Opens the PR into the `dev` branch.

    Args:
        c: The context object.
        type: The type of the PR (doc | feat | fix | refactor).
        title: The title of the PR.
        version_type: The type of version bump (default is "patch").
            [patch | minor | major | prepatch | preminor | premajor | prerelease]
    """
    if type not in ["fix", "feat", "doc", "refactor"]:
        print(f"🛑 PR type: {type}, Not [doc | feat | fix | refactor]")
        sys.exit(1)
    tag = ""
    body = ""
    bump = False
    if type == "fix":
        tag = "fix: "
        bump = True
        body = "Fixes a bug in the codebase."
    elif type == "doc":
        tag = "doc: "
        body = "Adds or updates documentation."
    elif type == "feat":
        tag = "feat: "
        bump = True
        body = "Introduces a new feature."
    elif type == "refactor":
        tag = "refactor: "
        body = "Refactors existing code without changing its behavior."
    else:
        print(f"🛑 PR type unknown: {type}")
        sys.exit(1)
    title = tag + " " + title
    print(f"Creating PR: {title}")
    feature_branch = get_current_branch(c)
    pr_branch = f"pr/{feature_branch}"
    assert_no_uncommitted(c)
    assert_merge_test(c, feature_branch, dev_branch)
    """Creating the branch for the PR"""
    git_switch_branch(c, dev_branch)
    git_switch_branch(c, pr_branch)
    c.run(f"git merge --squash {feature_branch}")
    c.run(f"git commit -m '🔀 merge {feature_branch} into {pr_branch}'")
    if bump:
        assert_version_type(c, version_type)
        new_version = get_new_version(c, version_type)
        print(f"Bumping version to {new_version}")
        bump_version(c, version_type)
        c.run("git add pyproject.toml")
        c.run(f"git commit -m 'build: ⬆️ Bump version to v{new_version}'")
    ci.dev_ci(c)
    c.run(f"git push --set-upstream origin {pr_branch}")
    assert_github_cli(c)
    c.run(
        f"gh pr create \
        --base {dev_branch} \
        --head {pr_branch} \
        --title '{title}' \
        --body '{body}'"
    )


release_ns = Collection("release")
release_ns.add_task(release, name="release")  # type: ignore[arg-type]
release_ns.add_task(create_pr, name="create_pr")  # type: ignore
