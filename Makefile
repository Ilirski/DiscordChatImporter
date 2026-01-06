.PHONY: help sync install update run test lint format typecheck check clean build

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

sync: ## Install/upgrade dependencies and sync lockfile
	uv sync --all-extras

install: sync ## Alias for sync

update: ## Update all dependencies to latest compatible versions
	uv lock --upgrade-all
	uv sync

run: ## Run the bot
	uv run python main.py

test: ## Run tests with coverage
	uv run pytest -v

test-quick: ## Run tests without coverage (faster)
	uv run pytest -v --no-cov

lint: ## Run linter to check code quality
	uv run ruff check .

format: ## Format code with ruff
	uv run ruff format .

format-check: ## Check if code is formatted
	uv run ruff format --check .

typecheck: ## Run type checker
	uv run basedpyright

check: lint typecheck test ## Run all checks (lint, typecheck, test)

clean: ## Clean build artifacts
	rm -rf .venv
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .pyright/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

build: ## Build the package
	uv build

fix: ## Auto-fix linting issues
	uv run ruff check --fix .

# Spell check
spell-check: ## Run spell checker
	uv run codespell

# Development helper commands
dev-deps: ## Install development dependencies
	uv sync --group dev

freeze: ## Show locked dependencies
	uv pip freeze
