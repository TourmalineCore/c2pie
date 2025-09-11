FROM python:3.12-slim

ENV PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.0.0

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential
    
RUN pip install "poetry>=$POETRY_VERSION"

ENV RUSTUP_HOME=/home/vscode/.rustup \
    CARGO_HOME=/home/vscode/.cargo \
    PATH=/home/vscode/.cargo/bin:/home/vscode/.local/bin:$PATH
RUN curl -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable && \
    cargo install c2patool --locked

COPY . /c2pie/

WORKDIR c2pie

RUN poetry config virtualenvs.create false \
  && poetry lock && poetry install --no-interaction --no-ansi