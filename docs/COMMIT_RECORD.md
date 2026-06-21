# Commit Record — Restaurant Platform

> Detailed record of every commit: what changed, which files, and why.

---

## Phase 0 — Bootstrap

### `aaf65c8` — chore: initial project scaffolding

- **Date**: 2026-06-17
- **What**: Initial monorepo structure — backend (FastAPI), frontend (Angular), mobile (Flutter), infrastructure (Terraform/Docker), docs, scripts
- **Files**: Project root, docker-compose, Terraform modules, CI workflows, Dependabot config

### `d3f11d5` — docs: update spec to reflect actual implementation

- **Date**: 2026-06-17
- **Files**: docs/

### `bca8667` — feat(frontend): add shell layout with Material sidenav

- **Date**: 2026-06-17
- **Files**: frontend/ shell component, Angular Material setup

### `700f470` — feat(backend): backend bootstrap + shared kernel + scaffolding

- **Date**: 2026-06-17
- **What**: FastAPI app factory, shared kernel (Entity, VOs, events, exceptions, database, Redis, UoW, event bus, outbox), 11 module scaffolds, Alembic, Dockerfiles, Celery, structlog, OpenTelemetry
- **Files**: backend/src/shared/, backend/src/app/, backend/src/modules/*/\_\_init\_\_.py, backend/src/workers/

### `223724e` — refactor(backend): register top-level editable packages

- **Date**: 2026-06-17
- **Files**: pyproject.toml

### `9e7e72d` — refactor(docker): sync project packages in Dockerfiles

- **Date**: 2026-06-17
- **Files**: Dockerfiles

### `e61d8a0` — style: run ruff format on updated files

- **Date**: 2026-06-17
- **Files**: Various backend files (formatting only)

### `8e5535b` — chore: complete Sprint 0C — hooks, mobile state, docs, scripts

- **Date**: 2026-06-17
- **What**: Pre-commit hooks, git hooks, release workflow, Riverpod+GoRouter in 3 Flutter apps, development setup guide, coding standards, PowerShell scripts
- **Files**: .pre-commit-config.yaml, .githooks/, .github/workflows/, mobile/apps/\*, docs/guides/, scripts/

---

## Phase 1 — Foundation

### `6e3a536` — feat: implement Phase 1 modules (identity, users, restaurants)

- **Date**: 2026-06-17
- **What**: Full domain/application/infrastructure/API for Identity (auth, JWT, bcrypt), Users (profiles), Restaurants (CRUD + verification). Migrations 0001-0002.
- **Files**: backend/src/modules/identity/, backend/src/modules/users/, backend/src/modules/restaurants/, backend/migrations/versions/0001-0002

### `c355619` — test(backend): add unit tests for Sprint 1 command/query handlers

- **Date**: 2026-06-18
- **What**: 46 unit tests across Identity (22), Users (7), Restaurants (17)
- **Files**: backend/tests/unit/modules/identity/, users/, restaurants/

### `520eeff` — fix(backend): add missing domain events and migration columns

- **Date**: 2026-06-18
- **What**: Added ProfileCreated/ProfileUpdated events, fixed migration column types
- **Files**: backend/src/modules/users/domain/, backend/migrations/

---

## Phase 2 — Ordering

### `aa10742` — feat(menus): implement Menus module — Sprint 2

- **Date**: 2026-06-18
- **What**: Menu + MenuItem aggregates, Category entity, 13 commands + 6 queries, SQLAlchemy models, full CRUD API, migration 0003. 52 tests.
- **Files**: backend/src/modules/menus/ (all layers), backend/migrations/versions/0003

### `42f02b8` — feat(backend): implement Orders, Payments, Deliveries, Notifications

- **Date**: 2026-06-18
- **What**: 4 full modules — Orders (state machine, cart, checkout), Payments (gateway, refunds), Deliveries (PostGIS, partner matching), Notifications (email). Migrations 0004-0005. WebSocket tracking. Cross-module event wiring.
- **Files**: backend/src/modules/orders/, payments/, deliveries/, notifications/, backend/src/shared/api/websockets.py, backend/migrations/versions/0004-0005

### `d1e70f4` — feat(backend): clear backlog — notifications tests, SMS/push dispatchers, menu search, modifiers

- **Date**: 2026-06-18
- **What**: 11 notification tests, SMS/Push dispatcher placeholders, pg_trgm search (migration 0006), ModifierGroup/Modifier entities (migration 0007)
- **Files**: backend/src/modules/menus/ (modifiers), backend/src/modules/notifications/ (dispatchers), backend/migrations/versions/0006-0007, backend/tests/

### `01d60cf` — docs: update Phase 2 Menus section with completed backlog items

- **Date**: 2026-06-18
- **Files**: docs/TODO.md

---

## Phase 3 — Payments & Delivery

### `8455531` — feat(backend): add notification event handlers and async task dispatchers

- **Date**: 2026-06-18
- **What**: Celery tasks for async notification sending, event handlers for OrderPlaced/OrderConfirmed/DeliveryAssigned/DeliveryCompleted
- **Files**: backend/src/workers/tasks/, backend/src/modules/notifications/event_handlers.py

---

## Phase 4 — Mobile & Dashboard

### `a34a403` — feat(frontend): UI overhaul — elevated minimal design system and feature pages

- **Date**: 2026-06-18
- **What**: Angular admin dashboard with 11 feature pages (dashboard, users, restaurants, menus, orders, deliveries, payments, analytics, settings), NgRx Signal Stores, Angular Material M3, Tailwind CSS v4
- **Files**: frontend/ (78 files — shell, all feature libs, design system, styles)

### `23633d7` — feat(mobile): implement Flutter apps with auth, navigation, and core packages

- **Date**: 2026-06-18
- **What**: 3 Flutter apps (customer, restaurant, delivery) + 8 shared packages (networking, auth, design_system, core, realtime, maps, localization, storage). Full navigation, auth flows, state management.
- **Files**: mobile/ (31 files across apps and packages)

### `ca6b729` — docs: update TODO with Phase 4 completion status

- **Date**: 2026-06-18
- **Files**: docs/TODO.md

---

## Phase 5 — AI Features & Polish

### `c143f95` — feat(backend): implement Reviews and Promotions modules — Phase 5

- **Date**: 2026-06-18
- **What**: Reviews module (27 tests) — Review entity, ratings, sentiment, flagging, 48h edit window, 7 API routes, migration 0008. Promotions module (28 tests) — 4 discount types, coupon usage, validation, 5 API routes, migration 0009.
- **Files**: backend/src/modules/reviews/ (all layers), backend/src/modules/promotions/ (all layers), backend/migrations/versions/0008-0009, backend/tests/unit/modules/reviews/, promotions/

### `8937bc7` — feat(backend): implement Analytics module — Phase 5 complete (all 11 backend modules done)

- **Date**: 2026-06-19
- **What**: Analytics module (17 tests) — read-only cross-schema queries (orders, deliveries, restaurants, reviews), 9 frozen dataclasses, 3 query handlers (restaurant dashboard, platform dashboard, revenue breakdown), 3 materialized views, migration 0010.
- **Files**: backend/src/modules/analytics/ (all layers), backend/migrations/versions/0010, backend/tests/unit/modules/analytics/

### `a167a68` — fix(backend): refine module implementations and fix lint issues

- **Date**: 2026-06-19
- **What**: Bug fixes and improvements across deliveries, menus, orders, payments, notifications, restaurants modules. Fixed ruff lint violations (line length, formatting). Updated integration tests.
- **Files changed (31)**:
  - backend/src/modules/deliveries/ (api, commands, ports, domain, repositories — 9 files)
  - backend/src/modules/menus/ (routes, modifier entity, models, repositories — 5 files)
  - backend/src/modules/orders/ (ports, queries, domain, repositories — 6 files)
  - backend/src/modules/payments/domain/entities/payment.py
  - backend/src/modules/notifications/ (commands, repository — 2 files)
  - backend/src/modules/restaurants/infrastructure/repositories/restaurant_repository.py
  - backend/src/modules/promotions/api/routes.py
  - backend/src/modules/reviews/api/routes.py
  - backend/src/shared/api/websockets.py
  - backend/src/workers/tasks/ (\_\_init\_\_.py, notification_tasks.py)
  - backend/tests/ (menus, notifications, orders tests — 3 files)

### `7b75925` — feat(backend): add AI services — embeddings, sentiment, recommendations

- **Date**: 2026-06-19
- **What**: AI platform module — pgvector embedding generator, AI gateway client, sentiment classifier, AI API routes (/api/v1/ai), recommendations engine (/api/v1/recommendations), review event handlers (auto-sentiment on submission), Celery embedding tasks, vector migration 0011. 4 unit tests.
- **Files created (11)**:
  - ai/src/embeddings/generator.py — pgvector embedding generation
  - ai/src/gateway/client.py — AI provider gateway (OpenAI/Claude)
  - ai/src/models/sentiment_classifier.py — review sentiment analysis
  - backend/src/modules/analytics/api/ai_routes.py — AI search & sentiment API
  - backend/src/modules/analytics/api/recommendations_routes.py — placeholder
  - backend/src/app/recommendations_routes.py — smart recommendations API
  - backend/src/modules/reviews/event_handlers.py — ReviewSubmitted → auto-sentiment
  - backend/src/workers/tasks/embedding_tasks.py — async embedding generation
  - backend/tests/unit/test_ai_features.py — AI feature tests
  - backend/migrations/versions/0011_vector_and_menu_item_embeddings.py
  - backend/src/app/main.py — wired AI routes and review event handlers

### `e5085ba` — feat(frontend): add reviews and promotions management pages

- **Date**: 2026-06-19
- **What**: Angular dashboard Phase 5 pages — reviews management (moderation, flagging queue, reply), promotions management (CRUD, usage stats, deactivation). Each with NgRx Signal Store, service, model, and component.
- **Files created (8)**:
  - frontend/libs/reviews/src/lib/reviews-list.component.ts (486 lines)
  - frontend/libs/reviews/src/lib/reviews.model.ts
  - frontend/libs/reviews/src/lib/reviews.service.ts
  - frontend/libs/reviews/src/lib/reviews.store.ts
  - frontend/libs/promotions/src/lib/promotions-dashboard.component.ts (494 lines)
  - frontend/libs/promotions/src/lib/promotions.model.ts
  - frontend/libs/promotions/src/lib/promotions.service.ts
  - frontend/libs/promotions/src/lib/promotions.store.ts
- **Files modified (5)**: promotions.routes.ts, reviews.routes.ts, settings component/model/service

### `5dc7268` — feat(mobile): add Phase 5 features — AI search, reviews, analytics

- **Date**: 2026-06-19
- **What**: Customer app — AI-powered menu search screen, review submission after delivery, coupon/promotion support in cart, order tracking improvements. Restaurant app — enhanced dashboard with revenue/order analytics charts.
- **Files created (2)**:
  - mobile/apps/customer_app/lib/features/home/ai_search_screen.dart (263 lines)
  - mobile/apps/customer_app/lib/features/order/review_submission_screen.dart (148 lines)
- **Files modified (6)**: cart_screen.dart, home_screen.dart, order_tracking_screen.dart, router.dart, dashboard_screen.dart, gradle.properties

### `84fdd7a` — docs: update TODO with complete Phase 5 progress and commit log

- **Date**: 2026-06-19
- **Files**: docs/TODO.md
