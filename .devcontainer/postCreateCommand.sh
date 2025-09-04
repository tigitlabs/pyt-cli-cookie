#!/bin/bash

set -e
echo "🚀postCreateCommand.sh: Start"

echo "🔗 Installing pre-commit hooks"
poetry run pre-commit install

echo 'export PS1=$"${PS1}\n"' >> ~/.bashrc

echo "🔚postCreateCommand.sh: Done"
