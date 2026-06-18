# Phase-Wise Development Prompts

## AI-Powered Multi-Vendor Restaurant Ordering Platform

> Each prompt below is self-contained and designed to be given to an AI coding assistant (like Claude Code) at the start of each phase. Copy the relevant phase prompt when you're ready to begin that sprint.

---

## Phase 0A — Backend Bootstrap (Sprint 0, Days 2-4)

### Prompt

```
You are working on the "restaurant-platform" monorepo — an AI-Powered Multi-Vendor Restaurant Ordering Platform. The repository already has the frontend (Angular 22), mobile (Flutter/Melos), CI/CD workflows, Docker Compose, and directory scaffolding in place. Read CLAUDE.md for full project conventions.

Your task: **Complete the backend bootstrap** — all foundational infrastructure code so the FastAPI backend can start, connect to PostgreSQL and Valkey, run migrations, and pass CI. Do NOT write business/feature logic — only the engineering foundation.

### What to build

1. **Python project setup** (`backend/`)
   - `pyproject.toml` with all dependencies (see spec Section 3.1): FastAPI >=0.115, SQLAlchemy[asyncio] >=2.0, asyncpg >=0.30, Alembic >=1.14, redis[hiredis] >=5.0, celery[redis] >=5.4, pyjwt[crypto] >=2.9, bcrypt >=4.2, pydantic >=2.9, pydantic-settings >=2.6, structlog >=24.4, opentelemetry-* >=1.27, boto3 >=1.35, httpx2 >=0.1, orjson >=3.10
   - Dev dependencies: pytest >=8.3, pytest-asyncio >=0.24, pytest-cov >=5.0, pytest-xdist, factory-boy, faker, ruff >=0.7, mypy >=1.13, import-linter >=2.1, testcontainers[postgres,redis] >=4.8
   - `.python-version` → 3.13
   - Use `uv` as package manager

2. **FastAPI application factory** (`backend/src/app/`)
   - `main.py` — app factory pattern (`create_app()`) that:
     - Loads config from environment via Pydantic Settings
     - Initializes async SQLAlchemy engine + session factory
     - Initializes Redis/Valkey connection pool
     - Registers CORS, request-ID, and error-handler middleware
     - Mounts module routers under `/api/v1/<module>`
     - Registers lifespan events (startup/shutdown for DB and Redis pools)
     - Returns the FastAPI instance
   - `config.py` — Pydantic Settings class reading from env vars (all settings from .env.example)
   - `dependencies.py` — FastAPI dependency providers (get_db_session, get_redis, get_current_user placeholder)

3. **Shared kernel** (`backend/src/shared/`)
   - `domain/entity.py` — Base Entity class with id (UUID), created_at, updated_at
   - `domain/value_objects.py` — Base ValueObject (frozen dataclass)
   - `domain/events.py` — Base DomainEvent class with event_id, occurred_at, aggregate_id
   - `domain/exceptions.py` — DomainException, NotFoundException, AuthorizationException, ValidationException
   - `infrastructure/database.py` — async SQLAlchemy engine factory, async session factory, Base model class
   - `infrastructure/redis.py` — async Redis/Valkey connection pool factory
   - `infrastructure/unit_of_work.py` — Abstract UnitOfWork + SQLAlchemy implementation
   - `infrastructure/event_bus.py` — In-process event bus (publish/subscribe) 
   - `infrastructure/outbox.py` — Transactional outbox pattern base (OutboxMessage model)
   - `api/errors.py` — Exception-to-HTTP-response handlers
   - `api/pagination.py` — Cursor-based and offset pagination schemas
   - `api/middleware/request_id.py` — X-Request-ID middleware
   - `api/middleware/cors.py` — CORS configuration
   - `api/security.py` — JWT token decode/verify utility (placeholder, no business logic)

4. **Module scaffolding** (`backend/src/modules/<context>/`)
   - Create all 11 modules: identity, users, restaurants, menus, orders, payments, deliveries, notifications, reviews, promotions, analytics
   - Each module gets: `__init__.py`, `domain/` (with __init__, entities/, value_objects/, events/, services/), `application/` (with __init__, commands/, queries/, ports/, services/), `infrastructure/` (with __init__, repositories/, models/, adapters/), `api/` (with __init__, routes.py, schemas/, dependencies.py)
   - Every `api/routes.py` should export an `APIRouter` with the module's prefix
   - All directories must have `__init__.py` files

5. **Database setup**
   - `alembic.ini` — Alembic configuration pointing to `migrations/`
   - `migrations/env.py` — Multi-schema aware migration runner
   - `migrations/script.py.mako` — Migration template
   - Create initial migration that creates all 11 schemas: identity, users, restaurants, menus, orders, payments, deliveries, notifications, reviews, promotions, analytics
   - Enable extensions: pg_trgm, postgis (via PostGIS image), btree_gist

6. **Import boundary enforcement** (`backend/.importlinter`)
   - Module isolation contract: all 11 modules must be independent
   - Domain purity contract: domain layers cannot import sqlalchemy, fastapi, redis, celery, boto3, httpx2

7. **Health check endpoint**
   - `GET /health` — returns {status: "healthy", database: "connected", redis: "connected"} with actual connectivity checks

8. **Test infrastructure** (`backend/tests/`)
   - `conftest.py` — shared fixtures: async test client, test database session, test Redis
   - `unit/` and `integration/` and `architecture/` and `e2e/` directories with __init__.py
   - One sample unit test that passes
   - Architecture test that runs import-linter

9. **Dockerfiles**
   - `backend/Dockerfile` — multi-stage build: uv install → copy src → uvicorn CMD
   - `backend/Dockerfile.worker` — same base, Celery worker CMD

10. **Environment**
    - `backend/.env.example` — all config vars with placeholder values (see spec Section 3.6)

11. **Celery setup** (`backend/src/workers/`)
    - `celery_app.py` — Celery app factory with Redis broker
    - `tasks/__init__.py` — empty task registry
    - `schedules/__init__.py` — empty beat schedule

12. **Structured logging**
    - Configure structlog with JSON output, request-ID correlation, log level from config

13. **OpenTelemetry instrumentation**
    - Configure OTLP exporter, instrument FastAPI, SQLAlchemy, Redis, Celery

### Constraints
- Python 3.13+, use modern syntax (match statements, type unions with |, etc.)
- Domain layer must have ZERO framework imports — pure Python only
- All async code uses native async/await (no sync wrappers)
- ruff line-length: 120
- mypy strict mode
- Every file must pass `ruff check` and `ruff format`
- All __init__.py files should exist but can be empty or have minimal re-exports
- Do NOT write any business logic, entities, or API schemas — only the skeleton/infrastructure
- The app must start with `uv run uvicorn app.main:create_app --factory --reload`

### Verification
- `uv sync --all-extras` succeeds
- `uv run uvicorn app.main:create_app --factory` starts without errors
- `GET /health` returns 200
- `uv run pytest` passes (at least 1 test)
- `uv run ruff check src/ tests/` passes
- `uv run mypy src/` passes (or has only expected stubs issues)
- `uv run lint-imports` passes
- `docker build -f Dockerfile .` succeeds
```

---

## Phase 0B — Infrastructure Bootstrap (Sprint 0, Days 2-5)

### Prompt

```
You are working on the "restaurant-platform" monorepo. Read CLAUDE.md for conventions. The Docker Compose file exists at `infrastructure/docker/docker-compose.yml` but needs PostgreSQL init scripts and refinement. Terraform structure needs to be built.

Your task: **Complete the infrastructure bootstrap** — local dev environment and Terraform foundation. No AWS resources will be provisioned yet, but modules must validate.

### What to build

1. **PostgreSQL init scripts** (`infrastructure/docker/postgres/init-scripts/`)
   - `01-create-extensions.sql` — Enable: pg_trgm, postgis, btree_gist, pgcrypto, uuid-ossp
   - `02-create-schemas.sql` — Create schemas: identity, users, restaurants, menus, orders, payments, deliveries, notifications, reviews, promotions, analytics
   - `03-create-roles.sql` — Create roles:
     - `app_tenant_scoped` — can SELECT/INSERT/UPDATE/DELETE on tenant-scoped tables (used by app at runtime)
     - `app_admin` — superuser-level for migrations and admin operations
   - `04-configure-rls.sql` — Template for enabling Row-Level Security (helper function to create tenant policies)

2. **Docker Compose refinement** (`infrastructure/docker/docker-compose.yml`)
   - `postgres`: image `postgis/postgis:17-3.5`, port 5432, mount init-scripts, health check, volume for data persistence
   - `valkey`: image `valkey/valkey:8-alpine`, port 6379, health check, custom config for maxmemory + eviction policy
   - `localstack`: image `localstack/localstack:latest`, port 4566, services: s3,sqs,sns,ses
   - `mailpit`: image `axllent/mailpit:latest`, ports 1025 (SMTP) + 8025 (Web UI)
   - `docker-compose.override.yml.example` — sample with pgAdmin and RedisInsight for debugging
   - Named volumes for postgres data and valkey data
   - Shared network `platform-network`

3. **Terraform modules** (`infrastructure/terraform/modules/`)
   Each module gets `main.tf`, `variables.tf`, `outputs.tf`:
   - `networking/` — VPC (3 AZs), public/private subnets, NAT gateway, route tables, security groups (ALB, ECS, RDS, Redis)
   - `compute/` — ECS Fargate cluster, task definitions (API, worker, beat), ALB with target groups, auto-scaling policies
   - `database/` — RDS PostgreSQL 17 (Multi-AZ option), parameter group, subnet group, security group rules
   - `cache/` — ElastiCache Valkey/Redis 8, subnet group, parameter group
   - `storage/` — S3 buckets (assets, documents, backups), lifecycle policies, bucket policies
   - `cdn/` — CloudFront distribution for static assets + S3 origin
   - `monitoring/` — CloudWatch log groups (per service), dashboards, alarms (P1: platform down, DB down; P2: high error rate, queue backlog)
   - `security/` — WAF web ACL, Secrets Manager entries, KMS key, IAM roles (ECS task role, execution role)
   - `ci-cd/` — ECR repositories (api, worker, frontend), GitHub Actions OIDC provider + IAM role
   - `dns/` — Route 53 hosted zone, A/AAAA alias records for ALB and CloudFront

4. **Environment configurations** (`infrastructure/terraform/environments/`)
   - `dev/` — main.tf (compose all modules with dev sizing), variables.tf, terraform.tfvars (smallest instances, single AZ, no HA), outputs.tf, backend.tf (S3 remote state)
   - `staging/` — same structure, production-like topology but smaller instances
   - `production/` — same structure, full Multi-AZ, auto-scaling, HA
   - `.terraform-version` → 1.9.x

5. **Infrastructure convenience scripts** (`infrastructure/scripts/`)
   - `setup-local.sh` — Checks prerequisites, starts Docker Compose, waits for health checks, runs backend migrations
   - `seed-data.sh` — Placeholder for inserting seed/demo data
   - `run-migrations.sh` — Runs Alembic migrations against local DB

6. **CI workflow** (`.github/workflows/infrastructure-ci.yml`)
   - Triggers on push/PR to infrastructure/terraform/**
   - Jobs: terraform fmt -check, terraform init + validate for each environment
   - No apply step (manual only)

7. **Security scan workflow** (`.github/workflows/security-scan.yml`)
   - dependency-scan: pip-audit, npm audit, flutter pub outdated
   - secret-scan: gitleaks
   - sast: bandit (Python), semgrep
   - container-scan: Trivy

8. **Dependabot** (`.github/dependabot.yml`)
   - Ecosystems: pip (backend/), npm (frontend/), pub (mobile/), terraform (infrastructure/terraform/), github-actions (.github/workflows/)
   - Weekly schedule, max 10 open PRs per ecosystem

### Constraints
- Terraform >= 1.9, AWS Provider >= 5.70
- All Terraform resources must be tagged: Project, Environment, ManagedBy=terraform
- Use `terraform fmt` canonical style
- PostgreSQL init scripts must be idempotent (use IF NOT EXISTS)
- Docker Compose must work on macOS, Linux, and Windows (Docker Desktop)
- Shell scripts must have proper error handling (set -euo pipefail)

### Verification
- `docker compose up -d` starts all 4 services, all pass health checks
- `psql` can connect, all 11 schemas exist, extensions are enabled
- `redis-cli ping` returns PONG from Valkey
- `terraform init && terraform validate` passes for all 3 environments
- `terraform fmt -check -recursive` passes
- CI workflows have valid YAML syntax
```

---

## Phase 0C — Code Quality & Remaining Sprint 0 (Sprint 0, Days 3-5)

### Prompt

```
You are working on the "restaurant-platform" monorepo. Read CLAUDE.md. The backend, frontend, mobile, and infrastructure scaffolding are complete. Your task: **Finish remaining Sprint 0 items** — pre-commit hooks, release workflow, mobile state management setup, and the development setup guide.

### What to build

1. **Pre-commit hooks** (`.pre-commit-config.yaml`)
   - pre-commit-hooks v5: trailing-whitespace, end-of-file-fixer, check-yaml, check-json, check-merge-conflict, detect-private-key, check-added-large-files (1MB max)
   - ruff-pre-commit v0.8+: ruff (--fix), ruff-format
   - gitleaks v8.22+

2. **Git hooks** (`tools/hooks/`)
   - `commit-msg` — Validate conventional commit format (feat|fix|chore|docs|refactor|test|perf|ci|build|style)(optional scope): message
   - `pre-commit` — Run ruff check on staged Python files (fast, local only)

3. **Release workflow** (`.github/workflows/release.yml`)
   - Manual dispatch with version input (e.g., v0.1.0)
   - Steps: validate version format, create git tag, build all Docker images, push to ECR, create GitHub Release with auto-generated notes

4. **Mobile state management** (Flutter)
   - Configure Riverpod in all 3 apps:
     - Wrap app widget with `ProviderScope` in each `main.dart`
     - Add `flutter_riverpod: ^3.1.0` to each app's pubspec.yaml dependencies (if not already present)
   - Configure GoRouter in all 3 apps:
     - Create `lib/navigation/router.dart` in each app with a basic GoRouter setup
     - Define initial routes: splash → auth → home (placeholder screens)
     - Add `go_router: ^17.0.0` to each app's pubspec.yaml
   - Ensure `flutter analyze` passes on all apps after changes

5. **Development setup guide** (`docs/guides/development-setup.md`)
   - Prerequisites with exact versions
   - Step-by-step setup for each platform (Backend, Frontend, Mobile)
   - Windows-specific notes (no `make` by default — use PowerShell equivalents or install make via chocolatey/scoop)
   - Common troubleshooting section
   - IDE setup recommendations (VS Code extensions, IntelliJ plugins)

6. **Coding standards guide** (`docs/guides/coding-standards.md`)
   - Python conventions (ruff rules, mypy strict, import ordering, naming)
   - Angular conventions (OnPush, Signals, standalone components, lazy routes)
   - Flutter conventions (Riverpod patterns, GoRouter patterns, freezed models)
   - Git conventions (branch naming, commit format, PR process)
   - Architecture rules summary (module isolation, domain purity, event-driven communication)

7. **PowerShell convenience scripts** (`scripts/`)
   - `bootstrap.ps1` — Windows equivalent of the Makefile: install all deps, start infra, run migrations
   - `lint-all.ps1` — Run all linters (ruff, eslint, dart analyze)
   - `test-all.ps1` — Run all test suites

### Constraints
- Pre-commit hooks must be fast (< 5 seconds for typical commits)
- Mobile changes must not break existing `dart analyze` or `flutter test`
- GoRouter configuration should use typed routes where possible
- Documentation must be accurate to the actual project state (not aspirational)

### Verification
- `pre-commit run --all-files` passes
- Commit message hook rejects "bad message" and accepts "feat(orders): add checkout flow"
- `flutter analyze` passes in all 3 mobile apps
- Each mobile app builds: `flutter build apk --debug`
- Documentation is complete and internally consistent
```

---

## Phase 1 — Foundation: Identity & Core Domain (Sprint 1, Weeks 3-4)

### Prompt

```
You are working on the "restaurant-platform" monorepo. Read CLAUDE.md for architecture rules. Sprint 0 is complete — the backend starts, connects to PostgreSQL/Valkey, passes CI, and all module scaffolding exists. 

Your task: **Implement the Identity module and core domain foundations** for Sprint 1. This is the first real business logic sprint.

### What to build

#### 1. Identity Module (`backend/src/modules/identity/`)

**Domain layer** (`domain/`):
- `entities/account.py` — Account aggregate root:
  - Fields: id (UUID), email, password_hash, phone_number, is_verified, is_active, verification_token, roles (list), created_at, updated_at
  - Methods: verify_email(), deactivate(), add_role(), remove_role(), change_password()
  - Invariants: email must be unique (enforced at DB level), password must meet complexity rules
- `value_objects/email.py` — Email value object with validation
- `value_objects/password.py` — Password value object (min 8 chars, complexity rules, never stores plaintext)
- `value_objects/phone_number.py` — Phone number with E.164 validation
- `value_objects/role.py` — Enum: SUPER_ADMIN, RESTAURANT_OWNER, RESTAURANT_STAFF, CUSTOMER, DELIVERY_PARTNER
- `events/account_events.py` — AccountCreated, AccountVerified, AccountDeactivated, PasswordChanged, RoleAssigned
- `services/password_service.py` — Domain service for password hashing/verification (port only — interface)

**Application layer** (`application/`):
- `commands/register_account.py` — RegisterAccountCommand + handler: validate input, check email uniqueness, hash password, create Account, publish AccountCreated event
- `commands/verify_email.py` — VerifyEmailCommand + handler
- `commands/login.py` — LoginCommand + handler: validate credentials, return JWT tokens
- `commands/refresh_token.py` — RefreshTokenCommand + handler
- `commands/change_password.py` — ChangePasswordCommand + handler
- `commands/forgot_password.py` — ForgotPasswordCommand + handler (send reset email)
- `commands/reset_password.py` — ResetPasswordCommand + handler
- `queries/get_account.py` — GetAccountQuery + handler
- `ports/account_repository.py` — Abstract AccountRepository interface
- `ports/password_hasher.py` — Abstract PasswordHasher interface
- `ports/token_service.py` — Abstract TokenService interface (JWT generation)
- `ports/email_sender.py` — Abstract EmailSender interface
- `services/auth_service.py` — Orchestrates login flow, token generation, token refresh

**Infrastructure layer** (`infrastructure/`):
- `models/account_model.py` — SQLAlchemy model mapped to `identity.accounts` table
- `repositories/account_repository.py` — SQLAlchemy implementation of AccountRepository
- `adapters/bcrypt_password_hasher.py` — bcrypt implementation of PasswordHasher
- `adapters/jwt_token_service.py` — PyJWT implementation of TokenService (access + refresh tokens)
- `adapters/smtp_email_sender.py` — Email sender (SMTP for dev, SES for prod)

**API layer** (`api/`):
- `routes.py` — FastAPI router:
  - `POST /api/v1/auth/register` — Register new account
  - `POST /api/v1/auth/verify-email` — Verify email with token
  - `POST /api/v1/auth/login` — Login, returns access + refresh tokens
  - `POST /api/v1/auth/refresh` — Refresh access token
  - `POST /api/v1/auth/forgot-password` — Request password reset
  - `POST /api/v1/auth/reset-password` — Reset password with token
  - `POST /api/v1/auth/logout` — Invalidate refresh token
- `schemas/` — Pydantic v2 request/response schemas for all endpoints
- `dependencies.py` — Wire up dependencies (repos, services) via FastAPI DI

**Database migration**:
- Create `identity.accounts` table with all columns, indexes on email (unique), phone_number
- Create `identity.refresh_tokens` table (token_hash, account_id, expires_at, is_revoked)

#### 2. Users Module — Basic Profile (`backend/src/modules/users/`)

**Domain**:
- `entities/user_profile.py` — UserProfile: id, account_id (UUID ref to identity), first_name, last_name, display_name, avatar_url, preferred_language, created_at, updated_at

**Application**:
- `commands/create_profile.py` — CreateProfileCommand (triggered by AccountCreated event)
- `queries/get_profile.py` — GetProfileQuery
- `ports/user_repository.py` — Abstract repo

**Infrastructure**:
- SQLAlchemy model for `users.profiles`
- Repository implementation

**API**:
- `GET /api/v1/me` — Get current user profile
- `PATCH /api/v1/me` — Update profile

**Migration**: `users.profiles` table

#### 3. Restaurants Module — Basic Structure (`backend/src/modules/restaurants/`)

**Domain**:
- `entities/restaurant.py` — Restaurant aggregate: id, owner_id, name, description, cuisine_types, address (VO), phone, email, operating_hours (VO), is_active, is_verified, rating_avg, total_reviews, created_at
- `value_objects/address.py` — Address with street, city, state, zip, country, lat/lng
- `value_objects/operating_hours.py` — Weekly schedule with open/close times per day
- `events/restaurant_events.py` — RestaurantRegistered, RestaurantVerified, RestaurantDeactivated

**Application**:
- `commands/register_restaurant.py` — Register new restaurant
- `commands/update_restaurant.py` — Update restaurant details
- `commands/verify_restaurant.py` — Admin verifies restaurant
- `queries/get_restaurant.py`, `queries/list_restaurants.py`
- `ports/restaurant_repository.py`

**Infrastructure**: SQLAlchemy model, repository, migration for `restaurants.restaurants`

**API**:
- `POST /api/v1/restaurants` — Register restaurant
- `GET /api/v1/restaurants` — List restaurants (paginated, filterable)
- `GET /api/v1/restaurants/{id}` — Get restaurant detail
- `PATCH /api/v1/restaurants/{id}` — Update restaurant
- `POST /api/v1/admin/restaurants/{id}/verify` — Admin verify

#### 4. Auth Middleware & RBAC (`backend/src/shared/api/`)
- `security.py` — Full JWT auth middleware:
  - Decode and validate access tokens
  - Extract current user (account_id, roles) into request state
  - `get_current_user` dependency
  - `require_roles(*roles)` dependency factory
  - `require_restaurant_access(restaurant_id)` — tenant scoping check
- Integrate with all module API routes

#### 5. Event Infrastructure
- Wire up the in-process event bus so AccountCreated triggers CreateProfileCommand in Users module
- Events cross module boundaries via the event bus, NOT direct imports

#### 6. Tests
- Unit tests for all domain entities and value objects (100% coverage on domain layer)
- Unit tests for command handlers (mocked ports)
- Integration tests for repositories (using testcontainers)
- Integration tests for API endpoints (register → verify → login → access protected route)
- Architecture test: import-linter still passes

### Constraints
- Domain layer: ZERO framework imports. Pure Python only.
- Modules MUST NOT import from each other. The Users module listens to AccountCreated via event bus, it does NOT import from identity.
- All passwords stored as bcrypt hashes, never plaintext
- JWT: RS256 or HS256 (configurable), 15min access tokens, 7-day refresh tokens
- All API responses follow consistent envelope: {data: ..., meta: ...} or {error: {code, message, details}}
- Use async/await everywhere — no sync database calls
- SQL migrations must be reversible (include downgrade)
- Row-Level Security: set up RLS on restaurants table with restaurant_id policy

### Verification
- `uv run pytest tests/unit -m unit` — all pass, >80% domain coverage
- `uv run pytest tests/integration -m integration` — all pass
- `uv run pytest tests/architecture -m architecture` — import boundaries hold
- Full auth flow works: register → verify email → login → get profile → create restaurant
- `uv run ruff check src/` and `uv run mypy src/` pass
- `uv run lint-imports` passes (no cross-module imports)
```

---

## Phase 2 — Core Ordering: Menus, Cart, Checkout (Sprint 2, Weeks 5-6)

### Prompt

```
You are working on the "restaurant-platform" monorepo. Read CLAUDE.md. Sprint 1 is complete — Identity (auth, JWT, RBAC), Users (profiles), and Restaurants modules are working. The event bus, auth middleware, and multi-tenant RLS are in place.

Your task: **Implement the Menus and Orders modules** — the core ordering flow from menu browsing to order placement.

### What to build

#### 1. Menus Module (`backend/src/modules/menus/`)

**Domain**:
- `entities/menu.py` — Menu aggregate: id, restaurant_id, name, description, is_active, display_order, categories (list)
- `entities/category.py` — MenuCategory: id, menu_id, name, description, display_order, items (list)
- `entities/menu_item.py` — MenuItem: id, category_id, name, description, price (Money VO), image_url, is_available, preparation_time_minutes, dietary_tags (list), modifiers (list)
- `entities/modifier_group.py` — ModifierGroup: id, menu_item_id, name, min_selections, max_selections, modifiers
- `entities/modifier.py` — Modifier: id, name, price_adjustment (Money VO)
- `value_objects/money.py` — Money VO (amount as Decimal, currency as str) with arithmetic operations
- `value_objects/dietary_tag.py` — Enum: VEGETARIAN, VEGAN, GLUTEN_FREE, HALAL, NUT_FREE, DAIRY_FREE, SPICY
- `events/menu_events.py` — MenuCreated, MenuItemAdded, MenuItemUpdated, MenuItemPriceChanged, ItemMarkedUnavailable

**Application**:
- Commands: CreateMenu, AddCategory, AddMenuItem, UpdateMenuItem, UpdateItemAvailability, AddModifierGroup, ReorderCategories
- Queries: GetMenu, ListMenusByRestaurant, SearchMenuItems (text search using pg_trgm)
- Ports: MenuRepository, MenuSearchService

**Infrastructure**:
- SQLAlchemy models mapped to `menus.*` tables
- Repository with eager loading for menu → categories → items → modifiers
- Full-text search implementation using PostgreSQL pg_trgm + GIN index
- Migration: menus.menus, menus.categories, menus.menu_items, menus.modifier_groups, menus.modifiers — with proper indexes and constraints

**API**:
- `POST /api/v1/restaurants/{restaurant_id}/menus` — Create menu (restaurant owner only)
- `GET /api/v1/restaurants/{restaurant_id}/menus` — List menus
- `GET /api/v1/menus/{menu_id}` — Full menu with all items
- `POST /api/v1/menus/{menu_id}/categories` — Add category
- `POST /api/v1/categories/{category_id}/items` — Add menu item
- `PATCH /api/v1/menu-items/{item_id}` — Update item
- `PATCH /api/v1/menu-items/{item_id}/availability` — Toggle availability
- `GET /api/v1/search?q=...&restaurant_id=...` — Search menu items

#### 2. Orders Module (`backend/src/modules/orders/`)

**Domain**:
- `entities/cart.py` — Cart aggregate: id, customer_id, restaurant_id, items (list of CartItem), notes, created_at, updated_at
  - CartItem: menu_item_id, menu_item_name, quantity, unit_price (Money), selected_modifiers, subtotal
  - Methods: add_item(), remove_item(), update_quantity(), clear(), calculate_total()
  - Invariants: all items must be from the same restaurant, quantity > 0, cart cannot be empty at checkout
- `entities/order.py` — Order aggregate root (the most important entity):
  - Fields: id, order_number (human-readable), customer_id, restaurant_id, items (list of OrderItem), subtotal, tax, delivery_fee, tip, total, status, delivery_address, special_instructions, estimated_delivery_time, placed_at, confirmed_at, preparing_at, ready_at, picked_up_at, delivered_at, cancelled_at, cancellation_reason
  - OrderItem: menu_item_id, name, quantity, unit_price, modifiers, subtotal
  - **State machine** for status:
    ```
    PENDING → CONFIRMED → PREPARING → READY_FOR_PICKUP → PICKED_UP → DELIVERED
    PENDING → CANCELLED (by customer, within time window)
    CONFIRMED → CANCELLED (by restaurant, with reason)
    Any state → FAILED (system failure)
    ```
  - Methods: confirm(), start_preparing(), mark_ready(), mark_picked_up(), mark_delivered(), cancel(reason)
  - Each transition publishes a domain event
- `value_objects/order_status.py` — Status enum with allowed transitions
- `value_objects/order_number.py` — Human-readable order number generator (e.g., ORD-20260617-A1B2C3)
- `events/order_events.py` — OrderPlaced, OrderConfirmed, OrderPreparing, OrderReady, OrderPickedUp, OrderDelivered, OrderCancelled

**Application**:
- Commands:
  - `AddToCart` — Add item to cart (validate item exists, belongs to correct restaurant)
  - `UpdateCartItem` — Update quantity or modifiers
  - `RemoveFromCart` — Remove item
  - `PlaceOrder` — Convert cart to order: snapshot prices, calculate totals, create Order in PENDING, publish OrderPlaced
  - `ConfirmOrder` — Restaurant confirms (must be within SLA)
  - `UpdateOrderStatus` — Restaurant updates through preparation states
  - `CancelOrder` — Cancel with rules (customer: only if PENDING, restaurant: with reason)
- Queries:
  - `GetCart` — Current cart for customer + restaurant
  - `GetOrder` — Order by ID
  - `ListCustomerOrders` — Paginated order history for customer
  - `ListRestaurantOrders` — Paginated orders for restaurant (with status filter)
- Ports: CartRepository, OrderRepository, OrderNumberGenerator

**Infrastructure**:
- SQLAlchemy models for orders.carts, orders.cart_items, orders.orders, orders.order_items
- Repositories with proper transaction handling
- Order number generator (date-based + random suffix)
- Migration with indexes on customer_id, restaurant_id, status, placed_at
- Redis/Valkey cache for active carts (TTL: 24 hours)

**API**:
- Cart:
  - `POST /api/v1/checkout/cart/items` — Add item to cart
  - `PATCH /api/v1/checkout/cart/items/{item_id}` — Update cart item
  - `DELETE /api/v1/checkout/cart/items/{item_id}` — Remove from cart
  - `GET /api/v1/checkout/cart` — Get current cart
  - `DELETE /api/v1/checkout/cart` — Clear cart
- Checkout:
  - `POST /api/v1/checkout/place-order` — Place order (cart → order)
- Orders:
  - `GET /api/v1/orders` — List my orders (customer) or restaurant orders (restaurant owner)
  - `GET /api/v1/orders/{order_id}` — Order detail
  - `POST /api/v1/orders/{order_id}/confirm` — Restaurant confirms
  - `POST /api/v1/orders/{order_id}/status` — Update status
  - `POST /api/v1/orders/{order_id}/cancel` — Cancel order

#### 3. Frontend — Menu & Order Management (Angular admin dashboard)

Update the Angular dashboard to show real data:
- **Restaurants page**: List restaurants from API, detail view
- **Menus page**: CRUD for menus, categories, items within a restaurant
- **Orders page**: Live order list with status filtering, order detail view, status update actions
- Use NgRx Signal Store for state management in each feature
- Use the api-client lib for typed HTTP calls
- Responsive tables with Angular Material

#### 4. Cross-Module Events
- OrderPlaced event should be published (will be consumed by Payments and Notifications in future sprints)
- MenuItemPriceChanged should NOT affect existing orders (orders snapshot prices at placement time)

#### 5. Tests
- Unit tests: Cart invariants, Order state machine transitions (every valid and invalid transition), Money arithmetic
- Integration: Full flow — create menu → add items → add to cart → place order → confirm → update status
- API tests: All endpoints with auth, RBAC (customer vs restaurant owner vs admin)
- Performance: Verify menu search uses pg_trgm index (EXPLAIN ANALYZE)

### Constraints
- Order prices are snapshotted at placement — never recalculated from current menu prices
- Cart is per-customer-per-restaurant (adding items from a different restaurant prompts to clear cart)
- Order state machine must be strict — invalid transitions raise DomainException
- Money calculations use Decimal (never float) to avoid precision issues
- All monetary amounts stored as integers (cents) in the database
- Menu search must support partial matching and be accent-insensitive
- RLS on all tables: restaurant_id scoping

### Verification
- Full ordering flow works end-to-end via API
- Order state machine rejects invalid transitions
- Cart enforces single-restaurant constraint
- Menu search returns relevant results with partial queries
- All tests pass, import boundaries maintained
- Angular dashboard shows restaurants, menus, and orders from the API
```

---

## Phase 3 — Payments & Delivery (Sprint 3, Weeks 7-8)

### Prompt

```
You are working on the "restaurant-platform" monorepo. Read CLAUDE.md. Sprint 2 is complete — Menus (CRUD, search) and Orders (cart, checkout, state machine) are working. OrderPlaced events are being published.

Your task: **Implement the Payments and Deliveries modules** — handling payment capture and delivery assignment/tracking.

### What to build

#### 1. Payments Module (`backend/src/modules/payments/`)

**Domain**:
- `entities/payment.py` — Payment aggregate:
  - Fields: id, order_id, customer_id, restaurant_id, amount (Money), currency, status, payment_method_type, payment_method_id, gateway_transaction_id, gateway_response, failure_reason, captured_at, refunded_at
  - **State machine**:
    ```
    PENDING → AUTHORIZED → CAPTURED → (partial) REFUNDED
    PENDING → FAILED
    AUTHORIZED → VOIDED
    CAPTURED → REFUNDED
    ```
  - Methods: authorize(), capture(), void(), refund(amount), fail(reason)
- `entities/payment_method.py` — PaymentMethod: id, customer_id, type (CARD, WALLET, COD), last_four, brand, is_default, token (gateway token, never raw card data)
- `value_objects/payment_status.py` — Status enum with transitions
- `events/payment_events.py` — PaymentAuthorized, PaymentCaptured, PaymentFailed, PaymentRefunded

**Application**:
- Commands:
  - `InitiatePayment` — Triggered by OrderPlaced event. Creates Payment in PENDING, calls gateway to authorize
  - `CapturePayment` — Triggered by OrderConfirmed event. Captures authorized payment
  - `RefundPayment` — Admin/system initiated refund (full or partial)
  - `VoidPayment` — Void if order cancelled before capture
  - `AddPaymentMethod` — Save tokenized payment method
  - `RemovePaymentMethod` — Remove saved method
- Queries: GetPayment, ListPaymentsByOrder, ListCustomerPaymentMethods
- Ports: PaymentGatewayPort (abstract), PaymentRepository, PaymentMethodRepository

**Infrastructure**:
- `adapters/stripe_gateway.py` — Stripe payment gateway adapter (use Stripe SDK)
  - For dev: use Stripe test mode keys
  - Implements: authorize, capture, void, refund
  - Stores gateway_transaction_id, never raw card data
- `adapters/mock_gateway.py` — Mock gateway for testing (always succeeds, configurable failures)
- SQLAlchemy models for payments.payments, payments.payment_methods
- Migration with indexes on order_id, customer_id, status

**API**:
- `POST /api/v1/payments/methods` — Add payment method (tokenized)
- `GET /api/v1/payments/methods` — List my payment methods
- `DELETE /api/v1/payments/methods/{id}` — Remove payment method
- `GET /api/v1/payments/orders/{order_id}` — Get payment for order
- `POST /api/v1/admin/payments/{id}/refund` — Admin refund

#### 2. Deliveries Module (`backend/src/modules/deliveries/`)

**Domain**:
- `entities/delivery.py` — Delivery aggregate:
  - Fields: id, order_id, restaurant_id, partner_id, pickup_address, delivery_address, status, estimated_pickup_time, actual_pickup_time, estimated_delivery_time, actual_delivery_time, distance_km, current_location (lat/lng), proof_of_delivery_url
  - **State machine**:
    ```
    PENDING_ASSIGNMENT → ASSIGNED → PARTNER_EN_ROUTE_TO_PICKUP → AT_PICKUP → 
    EN_ROUTE_TO_DELIVERY → AT_DELIVERY → DELIVERED
    PENDING_ASSIGNMENT → NO_PARTNER_AVAILABLE
    ASSIGNED → REASSIGNED (partner declines/cancels)
    ```
  - Methods: assign(partner_id), accept(), arrive_at_pickup(), pickup(), arrive_at_delivery(), deliver(proof_url), reassign(), update_location(lat, lng)
- `entities/delivery_partner.py` — DeliveryPartner: id, account_id, name, phone, vehicle_type, is_online, is_available, current_location, rating_avg, total_deliveries
- `value_objects/location.py` — GeoLocation VO (latitude, longitude) with distance calculation (Haversine)
- `value_objects/vehicle_type.py` — Enum: BICYCLE, MOTORCYCLE, CAR
- `events/delivery_events.py` — DeliveryCreated, PartnerAssigned, PickupCompleted, DeliveryCompleted, LocationUpdated

**Application**:
- Commands:
  - `CreateDelivery` — Triggered by OrderConfirmed event. Creates delivery in PENDING_ASSIGNMENT
  - `AssignPartner` — Assignment algorithm: find nearest available partner within radius
  - `AcceptAssignment` — Partner accepts
  - `UpdateDeliveryStatus` — Partner updates through delivery states
  - `UpdatePartnerLocation` — Real-time location update (high frequency, stored in Redis)
  - `TogglePartnerAvailability` — Go online/offline
- Queries: GetDelivery, GetDeliveryByOrder, ListPartnerDeliveries, ListActiveDeliveries, GetPartnerLocation
- Ports: DeliveryRepository, PartnerRepository, LocationCache (Redis), GeoService

**Infrastructure**:
- SQLAlchemy models for deliveries.deliveries, deliveries.delivery_partners
- PostGIS queries for nearest-partner search (ST_DWithin, ST_Distance)
- Redis for real-time partner locations (GEOADD/GEOSEARCH)
- Migration with PostGIS geometry columns for location data

**API**:
- `POST /api/v1/delivery-assignments/{delivery_id}/assign` — Trigger assignment
- `POST /api/v1/delivery-assignments/{delivery_id}/accept` — Partner accepts
- `POST /api/v1/delivery-assignments/{delivery_id}/status` — Update status
- `POST /api/v1/delivery-partners/location` — Update partner location
- `POST /api/v1/delivery-partners/availability` — Toggle online/offline
- `GET /api/v1/delivery-partners/me/deliveries` — Partner's delivery history
- `GET /api/v1/orders/{order_id}/tracking` — Get delivery tracking info

#### 3. WebSocket — Live Tracking (`backend/src/shared/api/`)

- WebSocket endpoint: `ws://localhost:8000/ws/orders/{order_id}/tracking`
- Sends real-time updates:
  - Order status changes
  - Delivery partner location updates (throttled to every 5 seconds)
  - Estimated time updates
- Auth: JWT token passed as query parameter for WebSocket handshake
- Use Redis Pub/Sub for broadcasting across server instances

#### 4. Notifications Module — Basic Setup (`backend/src/modules/notifications/`)

**Domain**:
- `entities/notification.py` — Notification: id, recipient_id, type, channel (EMAIL, SMS, PUSH, IN_APP), title, body, data (JSON), status (PENDING, SENT, FAILED), sent_at
- Events consumed: OrderPlaced → notify customer (confirmation), OrderConfirmed → notify customer, PartnerAssigned → notify partner + customer, DeliveryCompleted → notify customer

**Application**:
- `commands/send_notification.py` — SendNotificationCommand + handler
- `ports/notification_dispatcher.py` — Abstract dispatcher interface
- `ports/notification_repository.py` — Abstract repository interface

**Infrastructure**:
- Email via Mailpit (local) / SES (prod)
- SMS placeholder (log only in dev)
- Push notification placeholder (FCM integration ready)
- Celery tasks for async notification sending
- SQLAlchemy models for `notifications.notifications` table
- Repository implementation

**API**:
- `GET /api/v1/notifications` — List user notifications
- `PATCH /api/v1/notifications/{id}/read` — Mark as read

**Migration**: `notifications.notifications` table with indexes on recipient_id, status

**Unit tests**: Domain entity + SendNotification handler

#### 5. Cross-Module Event Wiring
- OrderPlaced → Payments.InitiatePayment, Notifications.SendOrderConfirmation
- OrderConfirmed → Payments.CapturePayment, Deliveries.CreateDelivery, Notifications.SendOrderConfirmed
- OrderCancelled → Payments.VoidPayment (if not captured) or Payments.RefundPayment
- PartnerAssigned → Notifications.SendPartnerAssigned (to customer + partner)
- DeliveryCompleted → trigger order completion flow

#### 6. Tests
- Payment state machine: every transition, including failures and edge cases
- Delivery assignment: nearest partner selection with PostGIS
- WebSocket: connection, auth, message delivery
- Integration: full order lifecycle — place → pay → confirm → assign delivery → deliver
- Event flow: verify all cross-module events fire correctly

### Constraints
- NEVER store raw card numbers — only tokenized references
- Payment amounts must match order totals exactly (no modification after placement)
- WebSocket connections must be authenticated
- Partner location updates should be efficient (Redis GEOADD, not database writes)
- Delivery assignment should have a timeout — if no partner accepts within 5 minutes, retry with wider radius
- All monetary operations must use Decimal, stored as cents in DB

### Verification
- Full lifecycle: place order → payment authorized → order confirmed → payment captured → delivery assigned → partner accepts → delivers
- Payment refund works for cancelled orders
- WebSocket delivers real-time tracking updates
- Nearest-partner search returns correct results
- All events propagate correctly across modules
- Tests pass, import boundaries maintained
```

---

## Phase 4 — Mobile Apps & Admin Dashboard (Sprint 4, Weeks 9-10)

### Prompt

```
You are working on the "restaurant-platform" monorepo. Read CLAUDE.md. Sprints 1-3 are complete — all backend modules (Identity, Users, Restaurants, Menus, Orders, Payments, Deliveries, Notifications) are working with full API, events, and tests.

Your task: **Build the Flutter mobile apps and enhance the Angular admin dashboard** to create fully functional user interfaces for all user roles.

### What to build

#### 1. Shared Flutter Packages (`mobile/packages/`)

**networking/**:
- Dio HTTP client factory with base URL configuration
- Auth interceptor: attach JWT access token, auto-refresh on 401, queue requests during refresh
- Retry interceptor: exponential backoff for 5xx errors
- Logging interceptor: structured request/response logging
- Response serialization: generic ApiResponse<T> wrapper with fromJson

**authentication/**:
- JWT token management: store access + refresh tokens in flutter_secure_storage
- Session state: Riverpod provider for auth state (authenticated, unauthenticated, loading)
- Login/register/logout flows with token persistence
- Auto-login on app start if valid refresh token exists

**design_system/**:
- Color tokens: primary (orange), secondary, surface, error colors matching Material 3
- Typography: Inter font, text styles (displayLarge → bodySmall)
- Spacing tokens: 4, 8, 12, 16, 24, 32, 48
- Common widgets: AppButton (filled, outlined, text variants), AppTextField, AppCard, LoadingOverlay, ErrorView, EmptyState
- Theme: ThemeData for light + dark mode

**core/**:
- Environment config: dev/staging/prod base URLs, feature flags
- Error models: AppException hierarchy (NetworkException, AuthException, ValidationException)
- Logger: structured logging with different levels
- Common types: Paginated<T>, Result<T> (Success/Failure), LatLng

**realtime/**:
- WebSocket client: connect to ws://host/ws/orders/{id}/tracking
- Auto-reconnect with exponential backoff
- Event parsing: OrderStatusUpdate, LocationUpdate
- Riverpod provider for tracking state

**maps/**:
- Google Maps widget wrapper with marker management
- Route polyline rendering for delivery tracking
- Location permission handling
- Platform-specific API key configuration

**localization/**:
- ARB-based i18n setup with flutter_localizations
- English (default) + extensible locale registry
- Localized string accessors for all user-facing text

**storage/**:
- Local storage abstraction (SharedPreferences for non-sensitive, flutter_secure_storage for tokens)
- Cache manager for offline-first read operations
- Image cache configuration

**analytics_pkg/**:
- Event tracking abstraction (Firebase Analytics ready)
- Screen view tracking, custom event logging
- User property management

#### 2. Customer App (`mobile/apps/customer_app/`)

**Features to implement:**

- **Authentication**: Login, register, forgot password screens. Biometric auth option.
- **Home**: Restaurant discovery grid/list, search bar, filter by cuisine, sort by rating/distance. Pull-to-refresh.
- **Restaurant Detail**: Restaurant info, operating hours, menu tabs by category, item cards with images.
- **Menu Item Detail**: Item description, price, modifier selection (size, toppings, etc.), quantity picker, add to cart.
- **Cart**: Cart summary, edit quantities, remove items, delivery address input, special instructions, order total breakdown (subtotal, tax, delivery fee, tip). Place order button.
- **Checkout**: Payment method selection (saved cards), add new card (Stripe widget), order review, confirm & pay.
- **Order Tracking**: Real-time order status with progress indicator, map with delivery partner location (Google Maps), estimated delivery time, partner info (name, phone).
- **Order History**: Past orders list, reorder button, order detail view.
- **Profile**: Edit profile, manage addresses, manage payment methods, notification preferences.

**Navigation**: GoRouter with shell route (bottom nav: Home, Orders, Profile). Auth guard redirects to login if unauthenticated.

**State Management**: Riverpod providers for each feature:
- `authProvider` — Auth state (AsyncNotifier)
- `restaurantsProvider` — Restaurant list with search/filter
- `menuProvider(restaurantId)` — Menu data (family)
- `cartProvider` — Cart state (Notifier)
- `ordersProvider` — Order history
- `trackingProvider(orderId)` — WebSocket tracking

#### 3. Restaurant App (`mobile/apps/restaurant_app/`)

**Features:**

- **Authentication**: Login for restaurant owners/staff.
- **Dashboard**: Today's stats (orders count, revenue, avg prep time), pending orders count badge.
- **Order Management**: 
  - Incoming orders tab (PENDING) with accept/reject actions
  - Active orders tab (CONFIRMED, PREPARING, READY) with status update buttons
  - Order detail: items, customer info, delivery info, payment status
  - Audio notification for new orders
- **Menu Management**: List menus, toggle item availability, edit prices/descriptions, add new items (with image upload via S3).
- **Restaurant Profile**: Edit business info, operating hours, delivery zones.
- **Analytics**: Basic charts — orders per day, revenue per day, popular items (last 7/30 days).

**Navigation**: GoRouter with shell route (bottom nav: Dashboard, Orders, Menu, Profile).

#### 4. Delivery App (`mobile/apps/delivery_app/`)

**Features:**

- **Authentication**: Login for delivery partners.
- **Home/Availability**: Online/offline toggle, current status, earnings summary for today.
- **Assignment**: 
  - Incoming assignment card with restaurant/delivery details, distance, estimated earnings
  - Accept/decline with countdown timer (30 seconds to respond)
- **Active Delivery**:
  - Step-by-step: navigate to restaurant → confirm pickup → navigate to customer → confirm delivery
  - Google Maps integration with turn-by-turn directions (launch native Maps app)
  - Proof of delivery: photo capture
  - Contact customer/restaurant buttons (phone)
- **Delivery History**: Past deliveries list with earnings.
- **Earnings**: Daily/weekly/monthly earnings breakdown, payout history.
- **Profile**: Edit profile, vehicle info, documents.

**Background**: Location updates sent every 10 seconds when on active delivery (use geolocator package).

#### 5. Angular Admin Dashboard Enhancement (`frontend/`)

Replace placeholder components with real functionality:

- **Dashboard**: KPI cards (total orders today, revenue, active users, active restaurants), charts (orders over time, revenue over time)
- **Users Management**: Users table with search, filter by role, user detail view, activate/deactivate user, assign roles
- **Restaurants Management**: Restaurant table with search, approval queue (pending verification), restaurant detail, approve/reject restaurants
- **Orders Management**: Orders table with status filter, date range picker, order detail modal, manual status update for support
- **Deliveries**: Active deliveries map view, delivery partner list with status, assignment override
- **Payments**: Transaction log table with filters, refund action
- **Analytics**: Revenue charts, order volume charts, popular restaurants, average delivery time (use Angular Material chart components or ngx-charts)
- **Notifications**: Notification log table, template management (future)
- **Settings**: Platform configuration (commission rates, delivery radius, etc.)

Each feature page should use:
- NgRx Signal Store for local state
- `@app/api-client` for HTTP calls
- Angular Material tables, forms, dialogs, snackbars
- Responsive layout (Material sidenav already in place)

#### 6. Tests
- Flutter: Widget tests for critical flows (login, restaurant list, cart, checkout)
- Angular: Vitest unit tests for Signal Stores, Playwright E2E for admin login → view orders → refund
- At least one integration test per mobile app: launch → login → primary action

### Constraints
- All mobile apps must work offline-first for read operations (cache restaurant/menu data)
- Images loaded via cached_network_image with placeholder
- Sensitive data (tokens, card info) in flutter_secure_storage only
- All API calls must handle loading, error, and empty states in the UI
- Angular: lazy-loaded routes, OnPush change detection, standalone components
- Mobile: Riverpod for all state, GoRouter for all navigation, freezed for models
- No hardcoded strings — prepare for localization (use constants/enums)

### Verification
- Customer app: browse restaurants → view menu → add to cart → checkout → track delivery
- Restaurant app: receive order notification → accept → update status through preparation
- Delivery app: go online → receive assignment → accept → pickup → deliver
- Admin dashboard: view all orders, manage restaurants, process refund
- All 3 mobile apps build for Android: `flutter build apk --debug`
- Angular build passes: `npm run build`
- Tests pass in all projects
```

---

## Phase 5 — AI Features & Polish (Sprint 5, Weeks 11-12)

### Prompt

```
You are working on the "restaurant-platform" monorepo. Read CLAUDE.md. Sprints 1-4 are complete — all backend modules, 3 mobile apps, and admin dashboard are functional. 

Your task: **Implement AI features, the Reviews/Promotions modules, comprehensive testing, and production hardening.**

### What to build

#### 1. Reviews Module (`backend/src/modules/reviews/`)

**Domain**:
- `entities/review.py` — Review: id, order_id, customer_id, restaurant_id, rating (1-5), comment, sentiment (AI-analyzed), is_flagged, reply (by restaurant), images, created_at
- `entities/review_summary.py` — RestaurantReviewSummary: restaurant_id, avg_rating, total_reviews, rating_distribution (1-5 counts), common_positive_themes, common_negative_themes
- Business rules: one review per order, only after delivery completed, editable within 48 hours
- Events: ReviewSubmitted, ReviewFlagged, ReviewReplied

**Application & API**:
- `POST /api/v1/orders/{order_id}/reviews` — Submit review
- `GET /api/v1/restaurants/{id}/reviews` — List reviews (paginated, sortable)
- `POST /api/v1/reviews/{id}/reply` — Restaurant owner reply
- `GET /api/v1/restaurants/{id}/reviews/summary` — Aggregated summary

#### 2. Promotions Module (`backend/src/modules/promotions/`)

**Domain**:
- `entities/promotion.py` — Promotion: id, restaurant_id (null for platform-wide), code, type (PERCENTAGE, FIXED_AMOUNT, FREE_DELIVERY, BUY_X_GET_Y), value, min_order_amount, max_discount, start_date, end_date, usage_limit, used_count, applicable_items, is_active
- `entities/coupon_usage.py` — CouponUsage: id, promotion_id, customer_id, order_id, discount_amount, used_at
- Business rules: validate expiry, usage limits, min order amount, one coupon per order
- Events: PromotionCreated, CouponApplied, PromotionExpired

**Application & API**:
- `POST /api/v1/promotions` — Create promotion (restaurant or admin)
- `GET /api/v1/promotions/available` — List available promotions for customer
- `POST /api/v1/checkout/apply-coupon` — Validate and apply coupon to cart
- `DELETE /api/v1/checkout/remove-coupon` — Remove applied coupon
- Integrate coupon validation into the order placement flow

#### 3. Analytics Module (`backend/src/modules/analytics/`)

**Domain**:
- Read-only module — consumes events from all other modules to build analytics views
- Materialized views / aggregation tables:
  - Daily order counts and revenue per restaurant
  - Popular menu items per restaurant
  - Average delivery time per area
  - Customer retention metrics
  - Peak ordering hours

**API**:
- `GET /api/v1/analytics/restaurant/{id}/dashboard` — Restaurant analytics
- `GET /api/v1/admin/analytics/platform` — Platform-wide analytics
- `GET /api/v1/admin/analytics/revenue` — Revenue reports with date range

#### 4. AI Services Module (`ai/`)

**4a. Semantic Menu Search**:
- Use pgvector extension for vector similarity search
- Embed menu item descriptions + names using OpenAI text-embedding-3-small
- Store embeddings in menus.menu_item_embeddings table
- API: `GET /api/v1/search/semantic?q=something+spicy+and+vegetarian`
- Falls back to pg_trgm text search if embedding service unavailable

**4b. AI-Powered Customer Support Assistant**:
- `POST /api/v1/ai/support/chat` — Conversational support
- Uses OpenAI GPT-4o or Claude via LangGraph workflow
- Context: order history, restaurant info, FAQs
- Can handle: order status inquiries, refund requests (creates ticket), restaurant recommendations
- Guardrails: cannot modify orders or payments directly, escalates to human for complex issues
- Rate limited: 20 messages per user per hour

**4c. Smart Recommendations**:
- `GET /api/v1/recommendations/restaurants` — Personalized restaurant recommendations
- Based on: order history, cuisine preferences, location, time of day, ratings
- `GET /api/v1/recommendations/menu-items?restaurant_id={id}` — "You might also like" on menu
- Hybrid: collaborative filtering (users who ordered X also ordered Y) + content-based (cuisine, dietary preferences)
- Cold start: popularity-based fallback for new users

**4d. Review Sentiment Analysis**:
- Analyze review text on submission
- Extract: overall sentiment (positive/neutral/negative), key themes
- Store in review entity
- Aggregate into restaurant review summary

#### 5. Production Hardening

**Rate Limiting**:
- Apply rate limits to all public endpoints (configurable per-route)
- Auth endpoints: 5 req/min per IP
- API endpoints: 100 req/min per authenticated user
- Use Redis sliding window counter

**Caching Strategy**:
- Restaurant list: cache 5 minutes
- Menu data: cache 10 minutes (invalidate on update)
- Search results: cache 2 minutes
- Use Redis with proper cache invalidation

**Error Handling Audit**:
- Ensure all endpoints return consistent error format
- Ensure no stack traces leak in production
- Ensure all domain exceptions map to appropriate HTTP status codes

**Security Hardening**:
- Ensure RLS policies are active on all tenant-scoped tables
- Add SQL injection protection audit (parameterized queries only)
- Add request payload size limits
- Add Helmet-equivalent security headers

#### 6. Comprehensive Testing

**Backend**:
- Unit test coverage >=80% on all domain layers
- Integration tests for every API endpoint
- Full E2E test: customer registers → browses → orders → pays → tracks → reviews
- Load test: 100 concurrent order placements using locust or k6
- Architecture tests: all import boundaries verified

**Frontend**:
- Vitest coverage >=80% on Signal Stores
- Playwright E2E: admin login → manage restaurants → view orders → process refund → view analytics

**Mobile**:
- Widget tests for all critical screens
- Integration test: login → browse → order flow (mocked API)
- Golden tests for key UI components

#### 7. Mobile App Updates
- Add review submission to customer app (after delivery)
- Add coupon/promotion application to cart/checkout
- Add AI search to customer app home screen
- Add analytics charts to restaurant app dashboard
- Add review management (reply) to restaurant app

#### 8. Angular Dashboard Updates
- **Reviews Management**: Review moderation queue, flagged reviews, view/respond to reviews, sentiment overview
- **Promotions Management**: CRUD promotions, usage statistics, activate/deactivate, coupon code generation
- **Notifications Management**: Notification log viewer, delivery/read status tracking

### Constraints
- AI features must gracefully degrade (if OpenAI is down, use fallback)
- Vector embeddings must be generated asynchronously (Celery task)
- Support chat must have conversation history (stored in DB)
- Rate limits must be per-user, not per-IP (for authenticated routes)
- Analytics must use read replicas / materialized views (never slow down writes)
- All new modules must pass import-linter
- Load test must complete without errors at target throughput

### Verification
- Semantic search returns relevant results for natural language queries
- AI support assistant can answer order status questions accurately
- Recommendations change based on user behavior
- Review sentiment analysis produces reasonable results
- All rate limits are enforced
- Caching reduces database load (verify with query monitoring)
- Load test: 100 concurrent orders/sec with P95 < 500ms
- Total test coverage: backend >=80%, frontend >=80%, mobile critical flows covered
- `uv run lint-imports` passes with all 12 modules
- All CI pipelines pass
```

---

## Phase 6 — MVP Release & Production Deployment (Sprint 6, Weeks 13-14)

### Prompt

```
You are working on the "restaurant-platform" monorepo. Read CLAUDE.md. All features are implemented and tested. All CI pipelines are green. 

Your task: **Prepare for production deployment** — infrastructure provisioning, deployment pipelines, monitoring, documentation, and the release process.

### What to build

#### 1. Terraform — Production Environment

Apply the Terraform modules to provision production AWS infrastructure:

- **Networking**: VPC with 3 AZs, public + private subnets, NAT gateway, VPC flow logs
- **Compute**: ECS Fargate cluster with services:
  - `api` — 2-4 tasks, 512 CPU / 1024 MB, ALB health check on /health
  - `worker` — 1-2 tasks for Celery workers
  - `beat` — 1 task for Celery Beat scheduler
  - Auto-scaling: CPU >70% scale up, <30% scale down
- **Database**: RDS PostgreSQL 17, db.r6g.large, Multi-AZ, 100GB gp3, automated backups (35 days), PITR enabled, encrypted at rest
- **Cache**: ElastiCache Valkey 8, cache.r6g.large, 2 nodes (primary + replica), encryption in transit + at rest
- **Storage**: S3 buckets — assets (CloudFront), documents (private), backups (lifecycle to Glacier)
- **CDN**: CloudFront distribution for frontend static assets + S3 asset images
- **Security**: WAF on ALB (rate limiting, SQL injection protection, XSS protection), KMS key for encryption, Secrets Manager for all credentials
- **Monitoring**: CloudWatch log groups, dashboards, alarms
- **DNS**: Route 53 hosted zone, A records for API + frontend, ACM certificate for TLS

#### 2. CI/CD — Production Deployment Pipeline

**Release workflow** (`.github/workflows/release.yml`):
1. Trigger: manual dispatch with version tag (e.g., v1.0.0)
2. Run all CI checks (backend, frontend, mobile)
3. Build Docker images with version tag
4. Push to ECR
5. Deploy backend to ECS (rolling update strategy)
6. Deploy frontend to S3 + CloudFront invalidation
7. Run post-deployment health checks
8. Create GitHub Release with auto-generated notes
9. Notify team (Slack webhook)

**Rollback procedure**:
- One-click rollback: redeploy previous ECS task definition revision
- Database: Alembic downgrade script for each migration
- Document in runbook

#### 3. Monitoring & Alerting

**CloudWatch Dashboards**:
- Platform Overview: request rate, error rate, latency P50/P95/P99, active connections
- Database: connection count, CPU, storage, replication lag, slow queries
- Cache: hit rate, evictions, connections, memory usage
- Delivery: active deliveries, avg delivery time, partner availability

**Alarms** (SNS → email/Slack):
- P1 (page immediately): API 5xx >5% for 5 minutes, database unreachable, ECS task count = 0
- P2 (alert within 1 hour): API latency P95 >1s, Celery queue depth >100, cache hit rate <50%, disk usage >80%
- P3 (daily digest): 4xx rate increase >20%, unused resources, certificate expiry <30 days

**Structured Logging**:
- JSON format with: timestamp, level, request_id, user_id, restaurant_id, service, message, extra
- Ship to CloudWatch Logs via awslogs driver
- Log retention: 30 days hot, 90 days archived

**Distributed Tracing**:
- OpenTelemetry traces exported to AWS X-Ray (or Jaeger for dev)
- Trace context propagation across HTTP calls, Celery tasks, Redis operations
- Sample rate: 10% in production, 100% in dev

#### 4. Operational Runbooks (`docs/runbooks/`)

- `incident-response.md` — Severity classification, escalation matrix, communication template
- `deployment.md` — Step-by-step deployment procedure, rollback steps, smoke test checklist
- `database-operations.md` — Migration procedure, backup/restore, failover, scaling
- `scaling.md` — How to scale ECS tasks, RDS, ElastiCache; when to scale; cost implications
- `common-issues.md` — Known issues and fixes: connection pool exhaustion, cache invalidation, payment gateway timeouts

#### 5. Documentation Finalization (`docs/`)

- `guides/deployment.md` — Full deployment guide with architecture diagram
- `api/` — Generate OpenAPI docs from FastAPI (auto-generated, ensure it's served at /docs)
- `architecture/adr/` — ADRs for key decisions made during development
- Update `guides/development-setup.md` with any changes since Sprint 0
- Update root `README.md` with project overview, setup instructions, architecture summary, contributing guidelines

#### 6. Security Checklist

Verify and document:
- [ ] All secrets in AWS Secrets Manager (none in code, env files, or Docker images)
- [ ] JWT signing key rotatable
- [ ] CORS restricted to production domains only
- [ ] Rate limiting active on all public endpoints
- [ ] WAF rules active (SQL injection, XSS, rate limiting)
- [ ] RLS policies verified on all tenant-scoped tables
- [ ] TLS on all external endpoints (ACM certificate)
- [ ] No debug mode in production config
- [ ] Gitleaks passes on entire repository
- [ ] Dependency audit: no critical vulnerabilities
- [ ] Password reset tokens expire (1 hour)
- [ ] Account lockout after 5 failed login attempts
- [ ] API payloads validated (Pydantic strict mode)

#### 7. Mobile Release Preparation

- Android: generate signed APK/AAB for all 3 apps
- iOS: archive builds (requires macOS + Xcode, may need to document manual steps)
- App store metadata: descriptions, screenshots (placeholder), privacy policy URL
- Version: 1.0.0 for all apps
- Configure Firebase for push notifications (FCM)

#### 8. Final Integration Testing

Run comprehensive end-to-end test on staging environment:
1. Customer: register → browse → search (AI) → add to cart → apply coupon → checkout → pay → track delivery → receive → review
2. Restaurant: login → view dashboard → receive order → accept → prepare → mark ready → view analytics
3. Delivery: login → go online → receive assignment → accept → pickup → deliver → view earnings
4. Admin: login → view dashboard → manage restaurants → view orders → process refund → view analytics
5. Load test: 100 concurrent users performing the customer flow simultaneously

### Constraints
- Zero-downtime deployment (rolling updates)
- All infrastructure changes through Terraform (no manual AWS console changes)
- Secrets must never appear in logs, error messages, or API responses
- Database migrations must be backwards-compatible (old code must work with new schema during rolling deploy)
- CloudFront cache invalidation must be triggered on frontend deploy
- Minimum 99.9% uptime target

### Verification
- All Terraform applies successfully for production environment
- Health check returns 200 on production URL
- Full E2E test passes on production
- All monitoring dashboards show data
- P1 alarm test: intentionally trigger and verify notification arrives
- Load test passes: 100 concurrent orders/sec, P95 <500ms, 0 errors
- Mobile apps install and function on real devices
- Tag v1.0.0 created on main branch
- GitHub Release published with artifacts and notes
```

---

## Quick Reference — Phase Dependencies

```
Phase 0A (Backend Bootstrap) ──┐
Phase 0B (Infrastructure)  ────┤
Phase 0C (Quality/Mobile)  ────┴──→ Phase 1 (Foundation) ──→ Phase 2 (Ordering)
                                                                    │
                                                                    ▼
                                                          Phase 3 (Payments/Delivery)
                                                                    │
                                                                    ▼
                                                          Phase 4 (Mobile/Dashboard)
                                                                    │
                                                                    ▼
                                                          Phase 5 (AI/Polish)
                                                                    │
                                                                    ▼
                                                          Phase 6 (MVP Release)
```

## Estimated Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| 0A + 0B + 0C (parallel) | 1-2 weeks | Week 2 |
| Phase 1 — Foundation | 2 weeks | Week 4 |
| Phase 2 — Ordering | 2 weeks | Week 6 |
| Phase 3 — Payments/Delivery | 2 weeks | Week 8 |
| Phase 4 — Mobile/Dashboard | 2 weeks | Week 10 |
| Phase 5 — AI/Polish | 2 weeks | Week 12 |
| Phase 6 — MVP Release | 1-2 weeks | Week 14 |
