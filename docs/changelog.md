## v0.0.6 (2025-09-11)

### ✨ Features

- **commitizen**: added cz_gitmoji as convention

### ♻️ Refactorings

- **invoke**: added comments and improved commit messages
- **commitizen**: moved config to pyproject.toml

### fix

- **git**: changelog creation is done using the --unreleased-version option
- **git**: fixed git_push with tag method

### style

- **cli**: linter fix for reassigned variable name

### 🎨🏗️ Style & Architecture

- **git**: fixed commit messaged for release

### 💚👷 CI & Build

- **github-actions**: release workflow works for push and pr

### 📝💡 Documentation

- **README**: added usage section

## v0.0.5 (2025-09-10)

### docs

- update changelog for release

### fix

- **cli**: using metadata to retrieve version

### style

- **pre-commit**: added double quotes for linter fix

### test

- **invoke**: added act.python-ci tasks

## v0.0.4 (2025-09-10)

### build

- **pre-commit**: update dependencies
- **ci**: target branch for dependabot changed to dev
- **deepsource**: added secrets check
- **pre-commit**: skipping poetry-lock on pre-commit.ci
- **poetry**: dependencies updated

### docs

- update changelog for release
- **README**: added Changelog link

### feat

- **ci**: added e2e test
- **invoke**: added git.flow-release-pr
- Invoke task for PR creation added
- **invoke**: added pr creation tasks
- **invoke**: added git-flow-release-finish task

### fix

- **invoke**: branch delete always using -D option now
- **README**: setup/update script handles existing files now

### style

- **pre-commit**: Github Action pre-commit causing error shellcheck
- **vscode**: hiding cache dirs

## v0.0.3 (2025-09-09)

## v0.0.2 (2025-09-08)

### build

- **poetry**: upgraded poetry.lock

### chore

- fixed typo

### ci

- update .deepsource.toml
- add .deepsource.toml
- **docker**: updated docker.ci task to build devcontainer
- **devcontainer**: added devcontainer cli to devcontainer.json
- **pre-commit**: removed pre-commit autoupdate from ci task because of typo being downgraded
- **pre-commit**: bumped version of typo -> v1.35.5
- **pre-commit**: added typo hook

### docs

- **changelog**: updated changelog

### feat

- **docker**: dynamic container name added to docker.py

### fix

- **docker**: add git-flow installation to Dockerfile
- **commitize**: fix version provider
- **commitize**: fix output path

### style

- **changelog**: fixed typo

## v0.0.1 (2025-09-09)
