.DEFAULT_GOAL := help

# ---- Local Infrastructure ----
.PHONY: infra-up infra-down infra-reset infra-logs

infra-up: ## Start local services (PostgreSQL, Valkey, LocalStack, Mailpit)
	cd infrastructure/docker && docker compose up -d

infra-down: ## Stop local services
	cd infrastructure/docker && docker compose down

infra-reset: ## Reset local services (destroy volumes and recreate)
	cd infrastructure/docker && docker compose down -v && docker compose up -d

infra-logs: ## Tail local service logs
	cd infrastructure/docker && docker compose logs -f

# ---- Backend ----
.PHONY: backend-install backend-dev backend-test backend-test-unit backend-test-integration backend-lint backend-migrate backend-migrate-create

backend-install: ## Install backend dependencies
	cd backend && uv sync --all-extras

backend-dev: ## Start FastAPI dev server with hot reload
	cd backend && uv run uvicorn app.main:create_app --factory --reload --host 0.0.0.0 --port 8000

backend-test: ## Run all backend tests
	cd backend && uv run pytest

backend-test-unit: ## Run backend unit tests only
	cd backend && uv run pytest tests/unit -m unit

backend-test-integration: ## Run backend integration tests (requires Docker)
	cd backend && uv run pytest tests/integration -m integration

backend-lint: ## Run backend linting (ruff + mypy)
	cd backend && uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/ && uv run mypy src/

backend-format: ## Auto-format backend code
	cd backend && uv run ruff format src/ tests/ && uv run ruff check --fix src/ tests/

backend-migrate: ## Run all pending Alembic migrations
	cd backend && uv run alembic upgrade head

backend-migrate-create: ## Create a new migration (usage: make backend-migrate-create msg="description")
	cd backend && uv run alembic revision --autogenerate -m "$(msg)"

backend-boundaries: ## Check import boundary rules
	cd backend && uv run lint-imports

# ---- Frontend ----
.PHONY: frontend-install frontend-dev frontend-test frontend-lint frontend-build

frontend-install: ## Install frontend dependencies
	cd frontend && npm ci

frontend-dev: ## Start Angular dev server
	cd frontend && npm start

frontend-test: ## Run all frontend tests
	cd frontend && npm test -- --watch=false

frontend-lint: ## Lint all frontend libraries
	cd frontend && npx ng lint

frontend-build: ## Build frontend for production
	cd frontend && npm run build:prod

# ---- Mobile ----
.PHONY: mobile-install mobile-test mobile-analyze mobile-format

mobile-install: ## Bootstrap Flutter workspace via Melos
	cd mobile && dart pub get && dart run melos bootstrap

mobile-test: ## Run all Flutter tests
	cd mobile && dart run melos run test

mobile-analyze: ## Run dart analyze on all packages
	cd mobile && dart run melos run analyze

mobile-format: ## Check formatting on all packages
	cd mobile && dart run melos run format

# ---- All ----
.PHONY: install test lint

install: backend-install frontend-install mobile-install ## Install all dependencies

test: backend-test frontend-test mobile-test ## Run all tests

lint: backend-lint frontend-lint mobile-analyze ## Lint everything

# ---- Help ----
.PHONY: help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'
