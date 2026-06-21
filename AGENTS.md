# AGENTS.md — Restaurant Platform

## Project Overview
AI-Powered Multi-Vendor Restaurant Ordering Platform. Modular monolith architecture with 12 bounded contexts.

## Repository Structure
- `backend/` — FastAPI modular monolith (Python 3.13+, uv)
- `frontend/` — Angular v22 admin dashboard (Angular CLI workspace)
- `mobile/` — Flutter apps (customer, restaurant, delivery) with Melos
- `ai/` — AI platform module
- `infrastructure/` — Terraform + Docker Compose
- `docs/` — Architecture specifications and guides
- `scripts/` — Developer convenience scripts

## Key Commands
- `make infra-up` — Start local PostgreSQL, Valkey, LocalStack, Mailpit
- `make infra-down` — Stop local services
- `make infra-reset` — Reset local services (destroy volumes)
- `make backend-install` — Install backend dependencies
- `make backend-dev` — Start FastAPI dev server (port 8000)
- `make backend-test` — Run backend tests
- `make backend-lint` — Run ruff + mypy
- `make backend-migrate` — Run Alembic migrations
- `make frontend-install` — Install frontend dependencies
- `make frontend-dev` — Start Angular dev server
- `make frontend-test` — Run frontend tests
- `make mobile-install` — Bootstrap Flutter workspace via Melos
- `make mobile-test` — Run Flutter tests

## Architecture Rules
- Each bounded context is an independent module under `backend/src/modules/`
- Modules MUST NOT import from each other directly (enforced by import-linter)
- Cross-module communication uses domain events only (transactional outbox pattern)
- Domain layer has ZERO framework dependencies (no SQLAlchemy, FastAPI, Redis, etc.)
- Clean Architecture layers: Domain → Application → Infrastructure → API
- Database uses schema-per-module (identity.*, orders.*, payments.*, etc.)
- Cross-schema references are by UUID only — no foreign keys across schemas
- All state changes go through explicit Unit of Work
- Multi-tenancy via Row-Level Security with restaurant_id as tenant key

## Bounded Contexts
Identity, Users, Restaurants, Menus, Orders, Payments, Deliveries, Notifications, Reviews, Promotions, Analytics, AI Services

## Coding Conventions
- Python: ruff for linting/formatting, mypy strict mode, 120 char line length
- Angular: ESLint + Prettier, eslint-plugin-boundaries for module rules, Angular Signals + NgRx Signal Store
- Flutter: dart analyze with strict mode, Riverpod for state, GoRouter for navigation
- Commits: conventional commits (feat:, fix:, chore:, docs:)
- PRs: squash merge to develop, merge commit to main

## Testing
- Backend: pytest, testcontainers for integration, import-linter for architecture
- Frontend: Vitest (native Angular 22 support), Playwright for E2E
- Mobile: Flutter test, mocktail for mocking

## API
- Single unified REST API: `/api/v1/`
- WebSockets for live tracking only
- JWT auth (15min access + 7day refresh tokens)
- RBAC with tenant scoping
