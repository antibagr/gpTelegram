SOURCES = app tests

.DEFAULT_GOAL := help
py = python -m poetry run

DOCKER_COMPOSE_FILE = contrib/docker-compose.yml

export PROJECT_NAME=gptTelegram

help: ## Display this help screen
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help

install: ## Install project dependencies
	python -m poetry install --no-interaction --no-ansi
.PHONY: install

format: ## Format the source code
	$(py) ruff check --config pyproject.toml --fix $(SOURCES)
	$(py) ruff format --config pyproject.toml $(SOURCES)
.PHONY: format

lint: ## Lint the source code
	$(py) ruff check --config pyproject.toml  $(SOURCES)
	$(py) mypy $(SOURCES)
	$(py) bandit -r app
.PHONY: lint

test: ## Run tests
	$(py) pytest -s -vvv -o log_cli=true -o log_cli_level=DEBUG
.PHONY: test

compose-up: ## Run the development server with docker-compose
	COMPOSE_PROJECT_NAME=${PROJECT_NAME} docker-compose -f ${DOCKER_COMPOSE_FILE} up --build --no-deps --remove-orphans --force-recreate -d
.PHONY: compose-up

compose-down: ## Stop the development server with docker-compose
	COMPOSE_PROJECT_NAME=${PROJECT_NAME} docker-compose -f ${DOCKER_COMPOSE_FILE} down -v --remove-orphans
.PHONY: compose-down

migrate:
	$(py) prisma db push
.PHONY: migrate ## Upgrade the database to the latest revision

run: ## Run telegram bot
	$(py) python -m app.cmd dispatch
.PHONY: run

