# Windows does not support BuildKit yet, so we need to use the old syntax
# Reference: https://github.com/moby/buildkit/issues/616
FROM python:3.12.0-bookworm

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY ./scripts/entrypoint.sh ./entrypoint.sh
RUN sed -i 's/\r$//g' ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-interaction --no-ansi --no-root --only main && rm -rf $POETRY_CACHE_DIR

COPY app /app/app/

ENTRYPOINT ["./entrypoint.sh"]
