#!/bin/bash

set -e
echo "🚀initializeCommand.sh: Start"

# Check if the script is running on GitHub Codespaces
if [[ -n "${CODESPACES}" || -n "${GITHUB_CODESPACE_TOKEN}" ]]; then
    printf "Running in GitHub Codespaces.\nNo need to export any keys."
    exit 0
elif [[ -n "${GITHUB_ACTIONS}" ]]; then
    printf "Running in GitHub Actions.\nNo need to export any keys."
    exit 0
else
    echo "Running on local host"
    echo "Check if gh is installed"
    if ! command -v gh &> /dev/null
    then
        echo "⚠️ gh could not be found"
    else
        echo "✅ gh is installed"
        gh --version
        echo "Check if gh is logged in"
        if ! gh auth status 2>&1 | grep -q "Logged in to github.com";
        then
            echo "⚠️ gh is not logged in, you have to provide the GitHub secrets"
        else
            echo "✅ gh is logged in"
            gh auth status
            echo "💡To write the secrets .devcontainer/.env, run:"
            echo 'gh auth token > .devcontainer/.github_token'
        fi
    fi

    if [ -z "$SSH_AUTH_SOCK" ]; then
        echo "SSH_AUTH_SOCK is not set"
        echo "⚠️ SSH authentication to github.com will not work"
        echo "https://code.visualstudio.com/remote/advancedcontainers/sharing-git-credentials#_using-ssh-keys"
    fi
fi


echo "🔚initalizeCommand.sh: Done"
