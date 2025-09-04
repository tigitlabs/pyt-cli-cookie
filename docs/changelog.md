## 0.0.2 (2025-09-04)

### Feat

- **python**: added tox
- **docker**: added pyenv
- **cli**: added loguru module
- **cli**: added config module
- **cli**: added --version flag
- **pytest**: coverage report added
- **docker**: added docker CI invoke tasks
- **develop**: added activate.sh - used the activate a dev environment on local host
- **pre-commit**: added spell check for commit messages
- **git**: git push after merging a feature
- **docker**: added docker CI invoke tasks
- **develop**: added activate.sh - used the activate a dev environment on local host
- **pre-commit**: added spell check for commit messages
- **git**: git push after merging a feature
- **python**: add task to run all Python tests
- **git**: add flow_release_start task to initiate a new release flow
- **git**: add flow-fix-finish task to complete fix branches
- **invoke**: added flow-fix-start command
- **invoke**: added git-flow-start-feature task
- **git**: enhance version type validation based on bump provider

### Fix

- **git**: fixed merge commit getting lost during release
- **mkdocs**: pdf export fixed
- **invoke**: python tasks have colors enabled now
- **git**: argument for release task can be lower case now.
- **git**: argument for release task can be lower case now.
- **git**: delete merged release branch after squashing into main
- **git**: improved commit message
- **git**: fixed merge command
- **git**: fixed commit messages
- **git**: separate merge and commit commands in flow_finish method
- **git**: separate merge and commit commands in flow_finish method
- **git**: update merge_test parameters to use release branch instead of dev branch
- **git**: update bump version command to include files-only option and automate changelog commit
- **git**: rename parameter in flow_fix_start to clarify branch naming
- **git**: update branch deletion logic in flow_finish method
- **git**: fix wrong git option -X
- **git**: flow-release-start task wip
- **git**: flow-release-start task wip
- **devcontainer**: ensure SSH key is added to ssh-agent

### Refactor

- **invoke**: moved release task code to collector class
- **docker**: update import statement
- **invoke**: added collector class for git operations

## 0.0.1 (2025-09-04)
