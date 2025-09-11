# Python Project Template

Template repository for Python projects.  
When used with the devcontainer there are no steps required to setup the environment.  
If used locally run: `source activate.sh`

Changelog can be found [/docs/changelog.md](/docs/changelog.md)

## Tools

### Invoke

All workflow steps can be run via 'invoke'.  
Most of the tasks are simply wrappers around the CLI tools used.

To get an overview, run:  
`inv -l`  
To see the help for a specific task run:  
`inv --help [task]` e.g. `inv --help python.ci`

#### Docker Tasks

The devcontainer has the the `docker-in-docker` feature installed and the Docker `invoke` tasks can
be run in the `devcontainer`.

However, `devcontainer` related tasks should be run on your host with the
 [devcontainer-cli][devcontainer-cli-link] already installed.

### Commitizen & Changelog

Changelogs are created automatically via [Commitizen][commitizen-link].  
In order to make sure the parsing of the changes works use the `cz c` command to commit.

### Git Flow

There are two possible workflows.

- `Pull Request` workflow
- `Local CI` workflow

    The actual build is still done via GitHub Actions.

Both share the `start` commands:

```bash
  git.flow-feature-start              Start a new feature branch.
  git.flow-fix-start                  Start a new fix branch.
  git.flow-release-start              Start a new release branch.
```

When the work is done the `finish` commands can be used for the `Local CI` workflow.
Or the `pr` commands for the `Pull Request` workflow.

## Setup

To use the template without cloning the repository you can run:  
⚠️ This will overwrite existing files! ⚠️

```bash
VERSION="0.0.5"; \
URL="https://github.com/tigitlabs/pyt-cli-cookie/archive/refs/tags/v${VERSION}.zip"; \
curl -L -o pyt-cli-cookie.zip ${URL} && \
unzip -o pyt-cli-cookie.zip && \
cd pyt-cli-cookie-${VERSION} && \
rsync -av . ../ && \
cd .. && \
rm -rf pyt-cli-cookie.zip pyt-cli-cookie-${VERSION}
```

---

[commitizen-link]: https://commitizen-tools.github.io/commitizen/
[devcontainer-cli-link]: https://code.visualstudio.com/docs/devcontainers/devcontainer-cli
