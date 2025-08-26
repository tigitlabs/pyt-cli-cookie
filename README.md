# Python Project Template

Template repository for `Python` projects.

## Invoke

All workflow steps can be run via 'invoke'.
To get an overview, run:
`inv -l`
To see the help for a specific task run:
`inv --help [task]` e.g. `inv --help python.release`

## Github Actions

- Any changes to `main` and `dev` are done via `PRs`.
- Code changes are added to the code base via `PRs` to `dev`.
- A `PR` title should start with one of those tags:
  - ✨ `feat`: A new feature
  - 🐛 `fix`: A bug fix
  - 📚 `docs`: Documentation only changes
  - ♻️ `refactor`: A code change that neither fixes a bug nor adds a feature

These tags are used to automatically update the `CHANGELOG.md` file upon release.

### Workflow

`PR` can be triggered via the `invoke` command.
`inv release.create-pr`
