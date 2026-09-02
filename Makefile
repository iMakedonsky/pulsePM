SHELL := /bin/sh

BACKEND_DIR := backend
FRONTEND_DIR := frontend
UV := cd $(BACKEND_DIR) && UV_CACHE_DIR=.cache/uv uv
BUN := bun run --cwd $(FRONTEND_DIR)

.DEFAULT_GOAL := help

.PHONY: help install install-backend install-frontend dev dev-backend dev-frontend \
	migrate migrations format format-backend format-frontend \
	format-check-backend format-check-frontend lint lint-backend lint-frontend \
	typecheck typecheck-backend typecheck-frontend fix fix-backend fix-frontend \
	test test-backend test-frontend pre-commit-install

help: ## Show available commands
	@awk 'BEGIN {FS = ":.*## "; printf "Usage: make <target>\n\n"} /^[a-zA-Z_-]+:.*## / {printf "  %-22s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: install-backend install-frontend ## Install all dependencies
install-backend: ## Create/sync the backend uv environment
	$(UV) sync --all-groups
install-frontend: ## Install frontend dependencies from the lockfile
	bun install --cwd $(FRONTEND_DIR) --frozen-lockfile

dev: ## Run backend and frontend together (Ctrl-C stops both)
	@$(MAKE) dev-backend & backend_pid=$$!; \
		$(MAKE) dev-frontend & frontend_pid=$$!; \
		trap 'kill $$backend_pid $$frontend_pid 2>/dev/null || true' INT TERM EXIT; \
		wait
dev-backend: ## Run Django on http://localhost:8000
	$(UV) run python manage.py runserver
dev-frontend: ## Run Vite on http://localhost:3000
	$(BUN) dev

migrate: ## Apply backend database migrations
	$(UV) run python manage.py migrate
migrations: ## Create backend database migrations
	$(UV) run python manage.py makemigrations

format: format-backend format-frontend ## Format backend and frontend files
format-backend:
	$(UV) run ruff format .
	$(UV) run djlint . --reformat --exclude .venv,.cache
format-frontend:
	$(BUN) format

lint: lint-backend lint-frontend ## Lint backend and frontend files
lint-backend:
	$(UV) run ruff check .
	$(UV) run djlint . --lint --exclude .venv,.cache
lint-frontend:
	$(BUN) lint:check

typecheck: typecheck-backend typecheck-frontend ## Type-check backend and frontend code
typecheck-backend:
	$(UV) run mypy .
typecheck-frontend:
	$(BUN) typecheck

fix: fix-backend fix-frontend ## Format, autofix lint, and type-check both projects
fix-backend:
	$(UV) run ruff format .
	$(UV) run ruff check --fix .
	$(UV) run djlint . --reformat --lint --exclude .venv,.cache
	$(UV) run mypy .
fix-frontend:
	$(BUN) fix
	$(BUN) typecheck

test: test-backend test-frontend ## Run all tests
test-backend:
	$(UV) run pytest
test-frontend:
	$(BUN) test

pre-commit-install: install-backend ## Install the repository Git hooks
	$(UV) run pre-commit install
