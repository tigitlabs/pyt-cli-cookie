#!/bin/bash

set -e
echo "🚀postStartCommand.sh: Start"

if [[ -n "${CODESPACES}" || -n "${GITHUB_CODESPACE_TOKEN}" ]]; then
    printf "Running in GitHub Codespaces.\nNo need to export any keys."
    exit 0
elif [[ -n "${GITHUB_ACTIONS}" ]]; then
    printf "Running in GitHub Actions.\nNo need to export any keys."
    exit 0
else
    echo "Running on local host"

fi

echo "🔚postStartCommand.sh: Done"
