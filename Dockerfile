# syntax=docker/dockerfile:1
# Keep this syntax directive! It's used to enable Docker BuildKit

################################
# PYTHON-BASE
# Sets up all our shared environment variables
################################
FROM python:3.11-bookworm as python-base

ENV PYTHONUNBUFFERED=1 \
    # pip
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # Poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.7.1 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    # never create virtual environment automaticly, only use env prepared by us
    POETRY_VIRTUALENVS_CREATE=false \
    \
    # this is where our requirements + virtual environment will live
    VIRTUAL_ENV="/venv"\
    DISPLAY=:0

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VIRTUAL_ENV/bin:$PATH"

# prepare virtual env
RUN python -m venv $VIRTUAL_ENV

WORKDIR /app
ENV PYTHONPATH="/app:$PYTHONPATH"

################################
# BUILDER-BASE
# Used to build deps + create our virtual environment
################################
FROM python-base as builder-base
RUN apt-get update && \
    apt-get install -y \
    apt-transport-https \
    gnupg \
    ca-certificates \
    build-essential \
    git \
    nano \
    curl

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
# The --mount will mount the buildx cache directory to where
# Poetry and Pip store their cache so that they can re-use it
RUN --mount=type=cache,target=/root/.cache \
    curl -sSL https://install.python-poetry.org | python -

# Copy application code

WORKDIR /app
COPY backend/pyproject.toml backend/poetry.lock ./
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --only main
COPY ./backend/aiconsole /app/aiconsole
COPY ./backend/aiconsole_toolkit /app/aiconsole_toolkit

################################
# DEVELOPMENT
# Image used during development / testing
################################
FROM builder-base as development

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --with dev,test

EXPOSE 8000
CMD ["bash"]

################################
# PRODUCTION
# Final image used for runtime
################################
FROM python-base as production

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y --no-install-recommends\
    ca-certificates && \
    apt-get clean

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $VIRTUAL_ENV $VIRTUAL_ENV

WORKDIR /app
COPY backend/pyproject.toml backend/poetry.lock ./
COPY ./backend/aiconsole /app/aiconsole
COPY ./backend/aiconsole_toolkit /app/aiconsole_toolkit

EXPOSE 8000
CMD ["python", "-m", "aiconsole.init"]