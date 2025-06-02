FROM python:3.8

ENV PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.0.0

# System deps:
RUN pip install "poetry>=$POETRY_VERSION"

COPY poetry.lock pyproject.toml /tc-c2pa-py/

WORKDIR tc-c2pa-py

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi
