SHELL := /bin/sh

BACKEND_DIR := backend
FRONTEND_DIR := frontend
UV := UV_CACHE_DIR=$(BACKEND_DIR)/.cache/uv uv --directory $(BACKEND_DIR)
BUN := bun run --cwd $(FRONTEND_DIR)

.DEFAULT_GOAL := help

.PHONY: help install install-backend install-frontend dev dev-backend dev-frontend \
	migrate migrations lint lint-backend lint-frontend format format-backend \
	format-frontend format-check format-check-backend format-check-frontend \
	typecheck typecheck-backend typecheck-frontend test test-backend test-frontend \
	check check-backend check-frontend pre-commit-install

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

lint: lint-backend lint-frontend ## Lint the entire project
lint-backend:
	$(UV) run ruff check .
	$(UV) run djlint pulse/templates --lint
lint-frontend:
	$(BUN) lint:check

format: format-backend format-frontend ## Format the entire project
format-backend:
	$(UV) run ruff format .
	$(UV) run djlint pulse/templates --reformat
format-frontend:
	$(BUN) format

format-check: format-check-backend format-check-frontend ## Check formatting without edits
format-check-backend:
	$(UV) run ruff format --check .
	$(UV) run djlint pulse/templates --check
format-check-frontend:
	$(BUN) format:check

typecheck: typecheck-backend typecheck-frontend ## Type-check the entire project
typecheck-backend:
	$(UV) run mypy .
typecheck-frontend:
	$(BUN) typecheck

test: test-backend test-frontend ## Run all tests
test-backend:
	$(UV) run pytest
test-frontend:
	$(BUN) test

check: check-backend check-frontend ## Run all non-mutating quality checks
check-backend: lint-backend format-check-backend typecheck-backend test-backend
check-frontend: lint-frontend format-check-frontend typecheck-frontend test-frontend

pre-commit-install: install-backend ## Install the repository Git hooks
	$(UV) run pre-commit install
