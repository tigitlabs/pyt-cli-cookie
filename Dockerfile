FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

LABEL dev.containers.project=template

ENV PROJECT_NAME=pyt-cli-cookie \
    POETRY_VERSION=2.1.3 \
    VIRTUAL_ENV_DISABLE_PROMPT=1 \
    CODENAME=jammy

# hadolint ignore=DL3008,DL3009
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    bash-completion \
    software-properties-common \
    ca-certificates \
    tmux \
    vim \
    curl \
    git \
    git-flow \
    python3-pip \
    python-is-python3 \
    pipx \
    # Clean up
    && apt-get autoremove -y && apt-get clean -y

USER vscode

# Install Poetry
# https://stackoverflow.com/questions/53835198/integrating-python-poetry-with-docker
RUN pipx ensurepath && pipx install poetry==${POETRY_VERSION}
# Add poetry to PATH
ENV PATH="${PATH}:/home/vscode/.local/bin"
# Install python dependencies
WORKDIR /workspaces/${PROJECT_NAME}
COPY pyproject.toml ./
COPY poetry.lock ./
RUN poetry install --no-interaction --no-ansi --no-root && \
    poetry self add poetry-plugin-up

# Set up pre-commit
COPY .pre-commit-config.yaml ./
# git init is needed to install pre-commit hooks
RUN git init . && poetry run pre-commit install-hooks && rm -rf .git

# Setup invoke tab completion
RUN poetry run invoke --print-completion-script bash > ~/.invoke-completion.sh && \
    echo "source ~/.invoke-completion.sh" >> ~/.bashrc

# Set up commitizen tab completion
RUN poetry run register-python-argcomplete cz > ~/.commitizen-completion.sh && \
    echo "source ~/.commitizen-completion.sh" >> ~/.bashrc
