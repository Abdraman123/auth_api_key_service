.PHONY: help setup install run test clean migrate upgrade downgrade db-reset format lint

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Auth API - Available Commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

setup: ## Run initial setup (first time only)
	@echo "$(BLUE)Running setup script...$(NC)"
	@chmod +x setup.sh
	@./setup.sh

install: ## Install dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@uv pip install -e ".[dev]"

run: ## Start development server
	@echo "$(BLUE)Starting development server...$(NC)"
	@uvicorn app.main:app --reload

run-prod: ## Start production server
	@echo "$(BLUE)Starting production server...$(NC)"
	@uvicorn app.main:app --host 0.0.0.0 --port 8000

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	@pytest

test-cov: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	@pytest --cov=app --cov-report=html --cov-report=term

test-verbose: ## Run tests with verbose output
	@echo "$(BLUE)Running tests (verbose)...$(NC)"
	@pytest -v -s

migrate: ## Create new migration (usage: make migrate MSG="your message")
	@echo "$(BLUE)Creating new migration...$(NC)"
	@alembic revision --autogenerate -m "$(MSG)"

upgrade: ## Apply database migrations
	@echo "$(BLUE)Applying migrations...$(NC)"
	@alembic upgrade head

downgrade: ## Rollback last migration
	@echo "$(BLUE)Rolling back last migration...$(NC)"
	@alembic downgrade -1

db-reset: ## Reset database (careful!)
	@echo "$(BLUE)Resetting database...$(NC)"
	@alembic downgrade base
	@alembic upgrade head

db-create: ## Create database
	@echo "$(BLUE)Creating database...$(NC)"
	@createdb auth_api_db || echo "Database may already exist"

format: ## Format code with black
	@echo "$(BLUE)Formatting code...$(NC)"
	@black app/ tests/

lint: ## Lint code with ruff
	@echo "$(BLUE)Linting code...$(NC)"
	@ruff check app/ tests/

lint-fix: ## Fix linting issues
	@echo "$(BLUE)Fixing linting issues...$(NC)"
	@ruff check --fix app/ tests/

type-check: ## Type check with mypy
	@echo "$(BLUE)Type checking...$(NC)"
	@mypy app/

clean: ## Clean cache and temporary files
	@echo "$(BLUE)Cleaning cache files...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf htmlcov/ .coverage

shell: ## Open Python shell with app context
	@echo "$(BLUE)Opening Python shell...$(NC)"
	@python -i -c "from app.main import app; from app.db.session import SessionLocal; db = SessionLocal()"

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	@docker build -t auth-api .

docker-run: ## Run Docker container
	@echo "$(BLUE)Running Docker container...$(NC)"
	@docker run -p 8000:8000 auth-api

docker-compose: ## Run with docker-compose
	@echo "$(BLUE)Starting docker-compose...$(NC)"
	@docker-compose up -d

docker-down: ## Stop docker-compose
	@echo "$(BLUE)Stopping docker-compose...$(NC)"
	@docker-compose down

env: ## Create .env file from example
	@echo "$(BLUE)Creating .env file...$(NC)"
	@cp .env.example .env
	@echo "$(GREEN)✓ .env created. Please update with your values.$(NC)"

secret-key: ## Generate a new SECRET_KEY
	@echo "$(BLUE)Generating SECRET_KEY:$(NC)"
	@python3 -c "import secrets; print(secrets.token_urlsafe(32))"

dev: install upgrade run ## Setup and run development server

all: setup upgrade run ## Complete setup and run