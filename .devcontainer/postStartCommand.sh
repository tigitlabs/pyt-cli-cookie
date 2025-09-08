#!/bin/bash

set -e
echo "🚀postStartCommand.sh: Start"


# Check if the script is running on GitHub Codespaces
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
    echo " Test SSH AgentForwarding for github.com"
    ssh -T git@github.com
fi

echo "🔚postStartCommand.sh: Done"
