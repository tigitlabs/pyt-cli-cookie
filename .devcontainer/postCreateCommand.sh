#!/bin/bash

set -e
echo "🚀postCreateCommand.sh: Start"

echo "🔗 Installing pre-commit hooks"
poetry run pre-commit install

echo "🔚postCreateCommand.sh: Done"
