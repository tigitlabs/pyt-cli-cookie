# Python Project Template

Template repository for Python projects.  
When used with the devcontainer there are no steps required to setup the environment.  
If used locally run: `source activate.sh`

Changelog can be found [/docs/changelog.md](/docs/changelog.md)

## Invoke

All workflow steps can be run via 'invoke'.  
To get an overview, run:
`inv -l`
To see the help for a specific task run:
`inv --help [task]` e.g. `inv --help python.release`

## Setup

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
