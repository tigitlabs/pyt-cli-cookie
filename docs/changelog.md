## 0.0.2 (2025-08-27)

### Feat

- **python**: add task to run all Python tests
- **git**: add flow_release_start task to initiate a new release flow
- **git**: add flow-fix-finish task to complete fix branches
- **invoke**: added flow-fix-start command
- **invoke**: added git-flow-start-feature task
- **git**: enhance version type validation based on bump provider

### Fix

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

## 0.0.1 (2025-08-26)

### Feat

- **docker**: dynamic container name added to docker.py

### Fix

- **docker**: add git-flow installation to Dockerfile
- **commitizen**: fix version provider
- **commitizen**: fix output path
