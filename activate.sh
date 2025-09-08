#!/usr/bin/env bash
# Activate the development environment

# Activate the Poetry environment
if command -v poetry >/dev/null 2>&1; then
    echo "Activating Poetry environment"
    eval "$(poetry env activate)"
else
    echo "Poetry is not installed or not on PATH"
fi

# Enable Invoke tab completion
if command -v inv >/dev/null 2>&1; then
    if [[ -n $BASH_VERSION ]]; then
        # bash
        echo "Enabling Invoke tab completion for bash"
        eval "$(inv --print-completion-script bash)"
    elif [[ -n $ZSH_VERSION ]]; then
        # zsh
        echo "Enabling Invoke tab completion for zsh"
        eval "$(inv --print-completion-script zsh)"
    fi
else
    echo "Invoke (inv) is not installed or not on PATH"
fi

# Enable Commitizen tab completion
if ! command -v cz >/dev/null 2>&1; then
    echo "❌ Commitizen (cz) is not installed or not on PATH"
elif ! command -v register-python-argcomplete >/dev/null 2>&1; then
    echo "❌ register-python-argcomplete is not installed or not on PATH"
else
    echo "Enabling Commitizen tab completion"
    eval "$(register-python-argcomplete cz)"
fi

echo "Environment setup complete!"
