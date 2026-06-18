# Project Status — Restaurant Platform

> Last updated: 2026-06-18
> Phase structure matches [phase-wise-development-prompts.md](guides/phase-wise-development-prompts.md)

## Phase 0 — Bootstrap (Sprint 0) ✅

### Sprint 0A: Backend Bootstrap ✅

| Area | Status | Notes |
|------|--------|-------|
| Python project setup (uv, pyproject.toml, Python 3.13) | ✅ Done | |
| FastAPI application factory (main.py, config.py) | ✅ Done | |
| Shared kernel (entity, VOs, events, UoW, event bus, outbox) | ✅ Done | |
| Module scaffolding (11 bounded contexts) | ✅ Done | |
| Database setup (Alembic, multi-schema, extensions) | ✅ Done | |
| Import boundary enforcement (.importlinter) | ✅ Done | |
| Health check endpoint | ✅ Done | |
| Test infrastructure | ✅ Done | |
| Dockerfiles (api + worker) | ✅ Done | |
| Celery + structured logging + OpenTelemetry | ✅ Done | |

### Sprint 0B: Infrastructure Bootstrap ✅

| Area | Status | Notes |
|------|--------|-------|
| Docker Compose (Postgres, Valkey, LocalStack, Mailpit) | ✅ Done | Pinned versions |
| PostgreSQL init scripts (extensions, schemas, roles, RLS) | ✅ Done | |
| Terraform modules (10 modules) | ✅ Done | Security hardened |
| Environment configs (dev, staging, production) | ✅ Done | |
| CI workflows + Dependabot | ✅ Done | |

### Sprint 0C: Code Quality & Remaining ✅

| Area | Status | Notes |
|------|--------|-------|
| Pre-commit hooks + git hooks | ✅ Done | |
| Release workflow | ✅ Done | |
| Mobile state management (Riverpod + GoRouter) | ✅ Done | |
| Frontend Angular shell + sidenav | ✅ Done | |
| Development setup + coding standards guides | ✅ Done | |
| PowerShell convenience scripts | ✅ Done | |

---

## Phase 1 — Foundation: Identity & Core Domain (Sprint 1) ✅

### Identity Module ✅ · 22 tests
- [x] Domain: Account entity, Email/Password/Phone/Role VOs, 5 events
- [x] Application: Register, Login, VerifyEmail, ChangePassword, ForgotPassword, ResetPassword, RefreshToken, GetAccount
- [x] Infrastructure: SQLAlchemy repo, JWT token service, bcrypt hasher
- [x] API: 8 auth routes under /api/v1/auth
- [x] Migration: identity.accounts, identity.refresh_tokens

### Users Module ✅ · 7 tests
- [x] Domain: UserProfile aggregate root, events
- [x] Application: CreateProfile, UpdateProfile, GetProfile
- [x] Event handler: AccountCreated → auto-create profile
- [x] API: Profile routes (GET/PATCH /api/v1/me)

### Restaurants Module ✅ · 17 tests
- [x] Domain: Restaurant entity, Address VO, OperatingHours VO, 4 events
- [x] Application: Register, Update, Verify, Get, List (pagination + search)
- [x] Infrastructure: SQLAlchemy repo, LIKE injection protection
- [x] API: 5 routes under /api/v1/restaurants + ownership checker

### Cross-Cutting ✅
- [x] Auth middleware + RBAC (shared/api/security.py)
- [x] Event bus subscribe_by_name (no cross-module imports)
- [x] Architecture tests (import-linter)
- [x] Integration test: full auth flow

---

## Phase 2 — Core Ordering: Menus, Cart, Checkout (Sprint 2) 🟡

### Menus Module (Backend) ✅ · 52 tests
- [x] Domain: Menu + MenuItem + ModifierGroup + Modifier aggregates, Category entity, Money VO, 7 events
- [x] Application: 13 commands + 6 queries (incl. search + modifiers)
- [x] Infrastructure: 5 models (menus.*), repos with filtering, pg_trgm search
- [x] API: Full CRUD under /api/v1/menus, search (GET /search), modifier endpoints
- [x] Migration: 0003_menus_module + 0006_menu_search_index + 0007_modifier_groups with RLS

### Orders Module (Backend) ✅ · 31 tests
- [x] Domain: Order aggregate (OrderNumber, financial breakdown, state machine), Cart aggregate, 8 events
- [x] Application: 8 commands + 4 queries, MenuService anti-corruption layer
- [x] Infrastructure: 4 models (orders.*), Redis write-through cache (24h TTL)
- [x] API: Dual routers — /api/v1/checkout + /api/v1/orders
- [x] Migration: 0004_orders_module with RLS

### Angular Frontend 🔲
- [ ] Restaurants page, Menus page, Orders page
- [ ] NgRx Signal Store + api-client lib
- [ ] Responsive tables with Angular Material

---

## Phase 3 — Payments & Delivery (Sprint 3) 🟡

### Payments Module (Backend) ✅ · 4 tests
- [x] Domain: Payment + PaymentMethod entities, PaymentStatus, 6 events
- [x] Application: 6 commands + 2 queries, PaymentGateway port
- [x] Infrastructure: MockGateway + StripeGateway, SQLAlchemy repos (payments.*)
- [x] Event handlers: OrderPlaced → initiate payment, PaymentCompleted → confirm order

### Deliveries Module (Backend) ✅ · 4 tests
- [x] Domain: Delivery + DeliveryPartner entities, GeoLocation VOs, 8 events
- [x] Application: 8 commands + 3 queries, LocationCache port
- [x] Infrastructure: PostGIS spatial queries, Redis location cache
- [x] API: Dual routers — /api/v1/delivery-assignments + /api/v1/partners
- [x] Migration: 0005_payments_deliveries with PostGIS + RLS

### WebSocket — Live Tracking ✅
- [x] /ws/orders/{id}/tracking with JWT auth, Redis pub/sub, location throttling

### Notifications Module ✅ · 9 tests
- [x] Domain + Application + Infrastructure + API + event handlers
- [x] Unit tests: 5 domain + 4 handler (9 total)
- [x] SMS/push dispatcher placeholders (CompositeNotificationDispatcher)
- [ ] Celery async sending (currently synchronous)

---

## Phase 4 — Mobile Apps & Admin Dashboard (Sprint 4) 🔲

### Shared Flutter Packages 🔲
- [ ] networking, authentication, design_system, core, realtime, maps, localization, storage

### Customer App 🔲
- [ ] Auth, home/discovery, restaurant detail, menu/cart, checkout, order tracking, history, profile

### Restaurant App 🔲
- [ ] Auth, dashboard, order management, menu management, profile, analytics

### Delivery App 🔲
- [ ] Auth, availability toggle, assignment, active delivery, history, earnings, profile

### Angular Admin Dashboard 🔲
- [ ] Dashboard, Users, Restaurants, Orders, Deliveries, Payments, Analytics, Settings pages

---

## Phase 5 — AI Features & Polish (Sprint 5) 🔲

### Reviews Module 🔲
- [ ] Domain, application, infrastructure, API, migration, tests

### Promotions Module 🔲
- [ ] Domain, application, infrastructure, API, migration, tests

### Analytics Module 🔲
- [ ] Read-only module with materialized views, API

### AI Services 🔲
- [ ] Semantic menu search (pgvector), AI support assistant, smart recommendations, review sentiment analysis

### Production Hardening 🔲
- [ ] Rate limiting, caching, error handling audit, security hardening

### Comprehensive Testing 🔲
- [ ] Backend >=80% coverage, frontend E2E, mobile widget tests, load testing

---

## Phase 6 — MVP Release & Production Deployment (Sprint 6) 🔲

- [ ] Terraform production environment (VPC, ECS, RDS, ElastiCache, S3, CloudFront, WAF, Route 53)
- [ ] CI/CD production pipeline (release workflow, rollback procedure)
- [ ] Monitoring & alerting (CloudWatch dashboards, P1/P2/P3 alarms, distributed tracing)
- [ ] Operational runbooks (incident response, deployment, database ops, scaling, common issues)
- [ ] Documentation finalization (deployment guide, OpenAPI, ADRs, README)
- [ ] Security checklist (13 items)
- [ ] Mobile release preparation (signed builds, app store metadata, FCM)
- [ ] Final integration testing (all 4 user roles + load test)

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Complete |
| 🟡 | Backend done, frontend/mobile pending |
| 🔲 | Not started |
