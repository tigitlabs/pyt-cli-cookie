#!/bin/bash

set -e
ACT_VERSION=v0.2.81
echo "🚀postCreateCommand.sh: Start"

if [[ -n "${CODESPACES}" || -n "${GITHUB_CODESPACE_TOKEN}" ]]; then
    printf "Running in GitHub Codespaces.\nNo need to export any keys."
    exit 0
elif [[ -n "${GITHUB_ACTIONS}" ]]; then
    printf "Running in GitHub Actions.\nNo need to export any keys."
    exit 0
else
    echo "Running on local host"
    echo "Authenticating with GitHub..."
    gh auth login --with-token < .devcontainer/.github_token

    echo "Check if gh is logged in"
    if ! gh auth status 2>&1 | grep -q "Logged in to github.com"; then
        echo "⚠️ gh is not logged in"
    else
        echo "✅ gh is logged in"
        gh auth status
    fi
fi

echo 'export PS1=$"${PS1}\n"' >> ~/.bashrc

echo "🔗 Installing nectos/act"
gh extension install https://github.com/nektos/gh-act --pin ${ACT_VERSION}

echo "🔗 Installing pre-commit hooks"
poetry run pre-commit install

echo "🔚postCreateCommand.sh: Done"
