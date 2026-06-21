# Project Bootstrap & Repository Setup Specification

## AI-Powered Multi-Vendor Restaurant Ordering Platform

| Field | Value |
|---|---|
| Status | Approved |
| Version | v1.1 |
| Date | June 2026 |
| Inputs | PRD v1.0, ADR v1.1, DDD v1.0, PostgreSQL Database Design v1.0, API Contract Specification v1.0, Backend Architecture v1.0, Frontend Architecture v1.0, AWS Infrastructure Architecture v1.0, AI Architecture Specification v1.0 |
| Repository Strategy | Git Monorepo |
| Repository Name | `restaurant-platform` |

---

# 1. Repository Initialization

## 1.1 Git Initialization Strategy

### Initialization Sequence

```text
1. Create GitHub repository: restaurant-platform (private)
2. Initialize with default branch: main
3. Clone locally
4. Create develop branch from main
5. Apply branch protection rules
6. Push initial commit (Section 10)
```

### Git Configuration

```text
Default Branch: main
Merge Strategy: Squash merge for feature branches into develop
                Merge commit for develop into main (release merges)
Signed Commits: Recommended, not enforced in Phase 1
LFS: Enabled for binary assets (images, design files)
```

### .gitignore Strategy

A root `.gitignore` covering all workspaces:

```text
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
.venv/
*.egg

# Node / Angular
node_modules/
dist/
.angular/

# Flutter
.dart_tool/
.packages
build/
.flutter-plugins
.flutter-plugins-dependencies

# Terraform
.terraform/
*.tfstate
*.tfstate.backup
*.tfplan

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.*
!.env.example

# Docker
docker-compose.override.yml
```

### .gitattributes

```text
*.png filter=lfs diff=lfs merge=lfs -text
*.jpg filter=lfs diff=lfs merge=lfs -text
*.jpeg filter=lfs diff=lfs merge=lfs -text
*.gif filter=lfs diff=lfs merge=lfs -text
*.ico filter=lfs diff=lfs merge=lfs -text
*.svg filter=lfs diff=lfs merge=lfs -text
*.pdf filter=lfs diff=lfs merge=lfs -text
```

---

## 1.2 Repository Settings

| Setting | Value |
|---|---|
| Visibility | Private |
| Wiki | Disabled (docs live in repo) |
| Issues | Enabled |
| Projects | Enabled |
| Discussions | Enabled |
| Packages | Enabled |
| Allow merge commits | Yes (develop → main only) |
| Allow squash merging | Yes (default for PRs) |
| Allow rebase merging | No |
| Auto-delete head branches | Yes |
| Require linear history | No |

---

## 1.3 Branch Protection Rules

### `main` Branch

| Rule | Value |
|---|---|
| Require pull request before merging | Yes |
| Required approvals | 2 |
| Dismiss stale reviews on new pushes | Yes |
| Require review from code owners | Yes |
| Require status checks to pass | Yes |
| Required checks | `backend-ci`, `frontend-ci`, `flutter-ci`, `security-scan` |
| Require branches to be up to date | Yes |
| Require conversation resolution | Yes |
| Restrict pushes | Only release managers |
| Allow force pushes | No |
| Allow deletions | No |

### `develop` Branch

| Rule | Value |
|---|---|
| Require pull request before merging | Yes |
| Required approvals | 1 |
| Dismiss stale reviews on new pushes | Yes |
| Require status checks to pass | Yes |
| Required checks | `backend-ci`, `frontend-ci`, `flutter-ci` |
| Require branches to be up to date | No |
| Allow force pushes | No |
| Allow deletions | No |

### Branch Naming Convention

```text
feature/<context>/<short-description>    — new functionality
fix/<context>/<short-description>        — bug fixes
chore/<context>/<short-description>      — tooling, config, infra
docs/<short-description>                 — documentation only
release/v<major>.<minor>.<patch>         — release candidates

Examples:
  feature/orders/place-order-flow
  fix/payments/capture-timeout
  chore/infra/terraform-vpc-setup
  docs/api-contract-update
  release/v0.1.0
```

---

## 1.4 Labels

### Priority Labels

| Label | Color | Description |
|---|---|---|
| `P0-critical` | `#b60205` | Production incident or blocker |
| `P1-high` | `#d93f0b` | Must be resolved this sprint |
| `P2-medium` | `#fbca04` | Should be resolved this sprint |
| `P3-low` | `#0e8a16` | Nice to have |

### Type Labels

| Label | Color | Description |
|---|---|---|
| `type:feature` | `#1d76db` | New functionality |
| `type:bug` | `#d73a4a` | Something broken |
| `type:chore` | `#e4e669` | Tooling, config, maintenance |
| `type:docs` | `#0075ca` | Documentation |
| `type:security` | `#b60205` | Security related |
| `type:performance` | `#5319e7` | Performance improvement |
| `type:refactor` | `#bfd4f2` | Code improvement, no behavior change |

### Domain Labels

| Label | Color | Description |
|---|---|---|
| `domain:identity` | `#c5def5` | Identity bounded context |
| `domain:users` | `#c5def5` | Users bounded context |
| `domain:restaurants` | `#c5def5` | Restaurants bounded context |
| `domain:menus` | `#c5def5` | Menus bounded context |
| `domain:orders` | `#c5def5` | Orders bounded context |
| `domain:payments` | `#c5def5` | Payments bounded context |
| `domain:deliveries` | `#c5def5` | Deliveries bounded context |
| `domain:notifications` | `#c5def5` | Notifications bounded context |
| `domain:reviews` | `#c5def5` | Reviews bounded context |
| `domain:promotions` | `#c5def5` | Promotions bounded context |
| `domain:analytics` | `#c5def5` | Analytics bounded context |
| `domain:ai` | `#c5def5` | AI Services bounded context |

### Platform Labels

| Label | Color | Description |
|---|---|---|
| `platform:backend` | `#d4c5f9` | Backend (FastAPI) |
| `platform:frontend` | `#d4c5f9` | Frontend (Angular) |
| `platform:mobile` | `#d4c5f9` | Mobile (Flutter) |
| `platform:infra` | `#d4c5f9` | Infrastructure (Terraform/AWS) |
| `platform:ai` | `#d4c5f9` | AI Platform |
| `platform:ci-cd` | `#d4c5f9` | CI/CD Pipelines |

### Status Labels

| Label | Color | Description |
|---|---|---|
| `status:blocked` | `#b60205` | Blocked by external dependency |
| `status:needs-review` | `#fbca04` | Awaiting review |
| `status:in-progress` | `#0e8a16` | Actively being worked on |
| `status:ready` | `#006b75` | Ready for implementation |

---

## 1.5 Milestones

| Milestone | Target | Description |
|---|---|---|
| `Sprint 0 — Bootstrap` | Week 1-2 | Repository setup, CI/CD, tooling, environments |
| `Sprint 1 — Foundation` | Week 3-4 | Identity, core domain models, database schemas |
| `Sprint 2 — Core Ordering` | Week 5-6 | Menus, Cart, Checkout, Orders |
| `Sprint 3 — Payments & Delivery` | Week 7-8 | Payment flow, delivery assignment |
| `Sprint 4 — Mobile & Dashboard` | Week 9-10 | Flutter apps, Angular admin |
| `Sprint 5 — AI & Polish` | Week 11-12 | AI features, testing, hardening |
| `MVP Release` | Week 13-14 | Production deployment |

---

# 2. Directory Creation Plan

## 2.1 Complete Directory Tree

```text
restaurant-platform/
│
├── .github/
│   ├── workflows/
│   │   ├── backend-ci.yml
│   │   ├── frontend-ci.yml
│   │   ├── flutter-ci.yml
│   │   ├── infrastructure-ci.yml
│   │   ├── security-scan.yml
│   │   ├── release.yml
│   │   └── dependency-review.yml
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   ├── feature_request.yml
│   │   └── config.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── CODEOWNERS
│   ├── dependabot.yml
│   └── labels.yml
│
├── docs/
│   ├── architecture/
│   │   ├── adr/
│   │   ├── specifications/
│   │   └── diagrams/
│   ├── api/
│   ├── guides/
│   │   ├── development-setup.md
│   │   ├── coding-standards.md
│   │   └── deployment.md
│   └── runbooks/
│
├── backend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   └── dependencies.py
│   │   │
│   │   ├── modules/
│   │   │   ├── identity/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── domain/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── entities/
│   │   │   │   │   ├── value_objects/
│   │   │   │   │   ├── events/
│   │   │   │   │   └── services/
│   │   │   │   ├── application/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── commands/
│   │   │   │   │   ├── queries/
│   │   │   │   │   ├── ports/
│   │   │   │   │   └── services/
│   │   │   │   ├── infrastructure/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── repositories/
│   │   │   │   │   ├── models/
│   │   │   │   │   └── adapters/
│   │   │   │   └── api/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── routes.py
│   │   │   │       ├── schemas/
│   │   │   │       └── dependencies.py
│   │   │   │
│   │   │   ├── users/
│   │   │   │   └── (same layered structure as identity)
│   │   │   ├── restaurants/
│   │   │   │   └── (same layered structure)
│   │   │   ├── menus/
│   │   │   │   └── (same layered structure)
│   │   │   ├── orders/
│   │   │   │   └── (same layered structure)
│   │   │   ├── payments/
│   │   │   │   └── (same layered structure)
│   │   │   ├── deliveries/
│   │   │   │   └── (same layered structure)
│   │   │   ├── notifications/
│   │   │   │   └── (same layered structure)
│   │   │   ├── reviews/
│   │   │   │   └── (same layered structure)
│   │   │   ├── promotions/
│   │   │   │   └── (same layered structure)
│   │   │   └── analytics/
│   │   │       └── (same layered structure)
│   │   │
│   │   ├── shared/
│   │   │   ├── __init__.py
│   │   │   ├── domain/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── events.py
│   │   │   │   ├── entity.py
│   │   │   │   ├── value_objects.py
│   │   │   │   └── exceptions.py
│   │   │   ├── infrastructure/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── database.py
│   │   │   │   ├── redis.py
│   │   │   │   ├── event_bus.py
│   │   │   │   ├── unit_of_work.py
│   │   │   │   └── outbox.py
│   │   │   └── api/
│   │   │       ├── __init__.py
│   │   │       ├── middleware/
│   │   │       ├── pagination.py
│   │   │       ├── errors.py
│   │   │       └── security.py
│   │   │
│   │   └── workers/
│   │       ├── __init__.py
│   │       ├── celery_app.py
│   │       ├── tasks/
│   │       └── schedules/
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── unit/
│   │   │   └── modules/
│   │   │       ├── identity/
│   │   │       ├── users/
│   │   │       ├── restaurants/
│   │   │       ├── menus/
│   │   │       ├── orders/
│   │   │       ├── payments/
│   │   │       ├── deliveries/
│   │   │       ├── notifications/
│   │   │       ├── reviews/
│   │   │       └── promotions/
│   │   ├── integration/
│   │   │   ├── conftest.py
│   │   │   └── modules/
│   │   ├── architecture/
│   │   │   └── test_import_boundaries.py
│   │   └── e2e/
│   │
│   ├── migrations/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       ├── identity/
│   │       ├── users/
│   │       ├── restaurants/
│   │       ├── menus/
│   │       ├── orders/
│   │       ├── payments/
│   │       ├── deliveries/
│   │       ├── notifications/
│   │       ├── reviews/
│   │       ├── promotions/
│   │       └── analytics/
│   │
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── alembic.ini
│   ├── Dockerfile
│   ├── Dockerfile.worker
│   ├── .python-version
│   └── .importlinter
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── app.ts
│   │   │   ├── app.html
│   │   │   ├── app.config.ts
│   │   │   └── app.routes.ts
│   │   ├── styles.scss          — Angular Material M3 theme + global a11y styles
│   │   ├── tailwind.css         — TailwindCSS v4 config
│   │   ├── index.html
│   │   └── main.ts
│   │
│   ├── libs/
│   │   ├── core/
│   │   │   └── src/
│   │   ├── shared/
│   │   │   └── src/
│   │   ├── design-system/
│   │   │   └── src/
│   │   ├── api-client/
│   │   │   └── src/
│   │   ├── auth/
│   │   │   └── src/
│   │   ├── dashboard/
│   │   │   └── src/
│   │   ├── users/
│   │   │   └── src/
│   │   ├── restaurants/
│   │   │   └── src/
│   │   ├── orders/
│   │   │   └── src/
│   │   ├── deliveries/
│   │   │   └── src/
│   │   ├── payments/
│   │   │   └── src/
│   │   ├── promotions/
│   │   │   └── src/
│   │   ├── reviews/
│   │   │   └── src/
│   │   ├── analytics/
│   │   │   └── src/
│   │   ├── settings/
│   │   │   └── src/
│   │   └── support/
│   │       └── src/
│   │
│   ├── package.json
│   ├── angular.json
│   ├── tsconfig.json
│   ├── eslint.config.mjs
│   ├── .prettierrc
│   ├── playwright.config.ts
│   ├── proxy.conf.json
│   ├── nginx.conf
│   └── Dockerfile
│
├── mobile/
│   ├── apps/
│   │   ├── customer_app/
│   │   │   ├── lib/
│   │   │   │   ├── app/
│   │   │   │   ├── core/
│   │   │   │   ├── features/
│   │   │   │   │   ├── authentication/
│   │   │   │   │   ├── home/
│   │   │   │   │   ├── restaurants/
│   │   │   │   │   ├── menus/
│   │   │   │   │   ├── cart/
│   │   │   │   │   ├── checkout/
│   │   │   │   │   ├── orders/
│   │   │   │   │   ├── tracking/
│   │   │   │   │   ├── reviews/
│   │   │   │   │   ├── profile/
│   │   │   │   │   └── promotions/
│   │   │   │   ├── navigation/
│   │   │   │   ├── shared/
│   │   │   │   └── main.dart
│   │   │   ├── test/
│   │   │   ├── pubspec.yaml
│   │   │   ├── analysis_options.yaml
│   │   │   └── README.md
│   │   │
│   │   ├── restaurant_app/
│   │   │   ├── lib/
│   │   │   │   ├── app/
│   │   │   │   ├── core/
│   │   │   │   ├── features/
│   │   │   │   │   ├── authentication/
│   │   │   │   │   ├── dashboard/
│   │   │   │   │   ├── orders/
│   │   │   │   │   ├── menu_management/
│   │   │   │   │   ├── restaurant_profile/
│   │   │   │   │   ├── staff/
│   │   │   │   │   ├── promotions/
│   │   │   │   │   ├── analytics/
│   │   │   │   │   └── settings/
│   │   │   │   ├── navigation/
│   │   │   │   ├── shared/
│   │   │   │   └── main.dart
│   │   │   ├── test/
│   │   │   ├── pubspec.yaml
│   │   │   └── analysis_options.yaml
│   │   │
│   │   └── delivery_app/
│   │       ├── lib/
│   │       │   ├── app/
│   │       │   ├── core/
│   │       │   ├── features/
│   │       │   │   ├── authentication/
│   │       │   │   ├── availability/
│   │       │   │   ├── assignments/
│   │       │   │   ├── navigation/
│   │       │   │   ├── deliveries/
│   │       │   │   ├── earnings/
│   │       │   │   ├── profile/
│   │       │   │   └── settings/
│   │       │   ├── navigation/
│   │       │   ├── shared/
│   │       │   └── main.dart
│   │       ├── test/
│   │       ├── pubspec.yaml
│   │       └── analysis_options.yaml
│   │
│   ├── packages/
│   │   ├── design_system/
│   │   │   ├── lib/
│   │   │   │   ├── src/
│   │   │   │   │   ├── tokens/
│   │   │   │   │   ├── theme/
│   │   │   │   │   ├── components/
│   │   │   │   │   └── foundations/
│   │   │   │   └── design_system.dart
│   │   │   ├── test/
│   │   │   └── pubspec.yaml
│   │   │
│   │   ├── core/
│   │   │   ├── lib/
│   │   │   │   └── src/
│   │   │   │       ├── config/
│   │   │   │       ├── errors/
│   │   │   │       ├── logging/
│   │   │   │       └── types/
│   │   │   └── pubspec.yaml
│   │   │
│   │   ├── networking/
│   │   │   ├── lib/
│   │   │   │   └── src/
│   │   │   │       ├── client/
│   │   │   │       ├── interceptors/
│   │   │   │       └── serialization/
│   │   │   └── pubspec.yaml
│   │   │
│   │   ├── authentication/
│   │   │   ├── lib/
│   │   │   │   └── src/
│   │   │   │       ├── jwt/
│   │   │   │       ├── session/
│   │   │   │       └── storage/
│   │   │   └── pubspec.yaml
│   │   │
│   │   ├── realtime/
│   │   │   ├── lib/
│   │   │   │   └── src/
│   │   │   └── pubspec.yaml
│   │   │
│   │   ├── analytics/
│   │   │   ├── lib/
│   │   │   └── pubspec.yaml
│   │   │
│   │   ├── localization/
│   │   │   ├── lib/
│   │   │   └── pubspec.yaml
│   │   │
│   │   ├── maps/
│   │   │   ├── lib/
│   │   │   └── pubspec.yaml
│   │   │
│   │   └── storage/
│   │       ├── lib/
│   │       └── pubspec.yaml
│   │
│   └── pubspec.yaml            — Dart native workspace root + Melos config
│
├── ai/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── gateway/
│   │   ├── prompts/
│   │   ├── embeddings/
│   │   ├── workflows/
│   │   ├── retrieval/
│   │   └── models/
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
│
├── infrastructure/
│   ├── terraform/
│   │   ├── environments/
│   │   │   ├── dev/
│   │   │   │   ├── main.tf
│   │   │   │   ├── variables.tf
│   │   │   │   ├── outputs.tf
│   │   │   │   ├── terraform.tfvars
│   │   │   │   └── backend.tf
│   │   │   ├── staging/
│   │   │   │   └── (same structure as dev)
│   │   │   └── production/
│   │   │       └── (same structure as dev)
│   │   │
│   │   └── modules/
│   │       ├── networking/
│   │       │   ├── main.tf
│   │       │   ├── variables.tf
│   │       │   └── outputs.tf
│   │       ├── compute/
│   │       ├── database/
│   │       ├── cache/
│   │       ├── storage/
│   │       ├── cdn/
│   │       ├── monitoring/
│   │       ├── security/
│   │       ├── ci-cd/
│   │       └── dns/
│   │
│   ├── docker/
│   │   ├── docker-compose.yml
│   │   ├── docker-compose.override.yml.example
│   │   ├── postgres/
│   │   │   └── init-scripts/
│   │   ├── redis/
│   │   └── localstack/
│   │
│   └── scripts/
│       ├── setup-local.sh
│       ├── seed-data.sh
│       └── run-migrations.sh
│
├── scripts/
│   ├── bootstrap.sh
│   ├── lint-all.sh
│   ├── test-all.sh
│   └── check-boundaries.sh
│
├── tools/
│   ├── generators/
│   ├── hooks/
│   │   ├── pre-commit
│   │   └── commit-msg
│   └── templates/
│
├── .editorconfig
├── .gitignore
├── .gitattributes
├── .pre-commit-config.yaml
├── CLAUDE.md
├── LICENSE
├── Makefile
└── README.md
```

---

## 2.2 Directory Purpose & Ownership

| Directory | Purpose | Owner |
|---|---|---|
| `.github/` | CI/CD workflows, issue templates, PR templates, CODEOWNERS, Dependabot config | DevOps Lead |
| `docs/` | All project documentation: architecture specs, API docs, dev guides, runbooks | Entire Team |
| `docs/architecture/` | Architecture Decision Records, specifications, system diagrams | Principal Architect |
| `docs/api/` | Generated OpenAPI documentation | Backend Lead |
| `docs/guides/` | Developer onboarding, coding standards, deployment guides | Backend Lead |
| `docs/runbooks/` | Operational runbooks for production | DevOps Lead |
| `backend/` | FastAPI modular monolith — all server-side business logic | Backend Lead |
| `backend/src/app/` | Application bootstrap: FastAPI app factory, config, root dependencies | Backend Lead |
| `backend/src/modules/` | Bounded context modules (identity, users, restaurants, menus, orders, payments, deliveries, notifications, reviews, promotions, analytics) | Backend Lead |
| `backend/src/modules/<context>/domain/` | Domain entities, value objects, events, domain services — zero framework deps | Backend Lead |
| `backend/src/modules/<context>/application/` | Use cases, commands, queries, ports (interfaces) | Backend Lead |
| `backend/src/modules/<context>/infrastructure/` | SQLAlchemy models, repository impls, adapters, external integrations | Backend Lead |
| `backend/src/modules/<context>/api/` | FastAPI routes, Pydantic schemas, route-level dependencies | Backend Lead |
| `backend/src/shared/` | Cross-cutting concerns: base classes, event bus, UoW, middleware, pagination | Backend Lead |
| `backend/src/workers/` | Celery app config, task definitions, scheduled jobs | Backend Lead |
| `backend/tests/` | All backend tests: unit, integration, architecture, e2e | Backend Lead |
| `backend/tests/architecture/` | Import boundary enforcement tests (import-linter) | Backend Lead |
| `backend/migrations/` | Alembic migrations, versioned per module | Backend Lead |
| `frontend/` | Angular v22 admin dashboard workspace | Frontend Lead |
| `frontend/apps/admin-dashboard/` | Admin Dashboard application shell | Frontend Lead |
| `frontend/libs/` | Feature libraries aligned to bounded contexts | Frontend Lead |
| `frontend/libs/core/` | Configuration, DI, environment, guards, interceptors | Frontend Lead |
| `frontend/libs/shared/` | Reusable components, pipes, directives, utilities | Frontend Lead |
| `frontend/libs/design-system/` | Design tokens, themes, typography, component wrappers | Frontend Lead |
| `frontend/libs/api-client/` | Generated/typed HTTP client for backend REST API | Frontend Lead |
| `mobile/` | Flutter workspace: all three mobile apps + shared packages | Mobile Lead |
| `mobile/apps/customer_app/` | Customer-facing Flutter application | Mobile Lead |
| `mobile/apps/restaurant_app/` | Restaurant operator Flutter application | Mobile Lead |
| `mobile/apps/delivery_app/` | Delivery partner Flutter application | Mobile Lead |
| `mobile/packages/` | Shared Flutter packages (design system, networking, auth, realtime, etc.) | Mobile Lead |
| `ai/` | AI platform module: gateway, prompts, embeddings, workflows, retrieval | AI/ML Lead (or Backend Lead in Phase 1) |
| `infrastructure/` | All infrastructure-as-code and local dev environment definitions | DevOps Lead |
| `infrastructure/terraform/` | Terraform modules and per-environment configurations | DevOps Lead |
| `infrastructure/docker/` | Docker Compose for local development, init scripts | DevOps Lead |
| `scripts/` | Developer convenience scripts (bootstrap, lint, test, boundary checks) | Entire Team |
| `tools/` | Code generators, git hooks, templates | Backend Lead |

---

## 2.3 CODEOWNERS

```text
# Default
*                                   @backend-lead

# Backend
/backend/                           @backend-lead
/backend/src/modules/identity/      @backend-lead
/backend/src/modules/payments/      @backend-lead
/backend/src/modules/orders/        @backend-lead

# Frontend
/frontend/                          @frontend-lead

# Mobile
/mobile/                            @mobile-lead

# Infrastructure
/infrastructure/                    @devops-lead
/.github/                           @devops-lead

# AI
/ai/                                @backend-lead

# Documentation
/docs/                              @backend-lead @frontend-lead @mobile-lead

# Security-sensitive
/backend/src/modules/identity/      @backend-lead @security-reviewer
/backend/src/modules/payments/      @backend-lead @security-reviewer
/backend/src/shared/api/security.py @backend-lead @security-reviewer
/infrastructure/terraform/modules/security/ @devops-lead @security-reviewer
```

---

# 3. Backend Bootstrap Plan

## 3.1 Python & uv Setup

### Python Version

```text
Python 3.13+
```

File: `backend/.python-version`

```text
3.13
```

### uv Initialization

```bash
cd backend
uv init --name restaurant-platform-backend
```

### pyproject.toml Structure

```toml
[project]
name = "restaurant-platform-backend"
version = "0.1.0"
description = "AI-Powered Multi-Vendor Restaurant Ordering Platform — Backend"
requires-python = ">=3.13"

dependencies = [
    # Web Framework
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "python-multipart>=0.0.9",

    # Database
    "sqlalchemy[asyncio]>=2.0",
    "asyncpg>=0.30",
    "alembic>=1.14",

    # Redis
    "redis[hiredis]>=5.0",

    # Background Processing
    "celery[redis]>=5.4",

    # Auth
    "pyjwt[crypto]>=2.9",
    "bcrypt>=4.2",

    # Validation
    "pydantic>=2.9",
    "pydantic-settings>=2.6",
    "email-validator>=2.2",

    # Observability
    "opentelemetry-api>=1.27",
    "opentelemetry-sdk>=1.27",
    "opentelemetry-instrumentation-fastapi>=0.48",
    "opentelemetry-instrumentation-sqlalchemy>=0.48",
    "opentelemetry-instrumentation-redis>=0.48",
    "opentelemetry-instrumentation-celery>=0.48",
    "structlog>=24.4",

    # AWS
    "boto3>=1.35",

    # Utilities
    "httpx2>=0.1",
    "orjson>=3.10",
]

[project.optional-dependencies]
dev = [
    # Testing
    "pytest>=8.3",
    "pytest-asyncio>=0.24",
    "pytest-cov>=5.0",
    "pytest-xdist>=3.5",
    "factory-boy>=3.3",
    "faker>=30.0",
    "httpx2>=0.1",

    # Code Quality
    "ruff>=0.7",
    "mypy>=1.13",
    "import-linter>=2.1",
    "pre-commit>=4.0",

    # Database Testing
    "testcontainers[postgres,redis]>=4.8",
]

[tool.ruff]
target-version = "py313"
line-length = 120
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E", "W", "F", "I", "N", "UP", "S", "B", "A", "C4",
    "DTZ", "T10", "ISC", "ICN", "PIE", "PT", "RSE", "RET",
    "SLF", "SIM", "TID", "TCH", "ARG", "PTH", "ERA", "PL",
    "TRY", "FLY", "PERF", "RUF",
]
ignore = ["S101", "TRY003"]

[tool.ruff.lint.isort]
known-first-party = ["app", "modules", "shared"]

[tool.mypy]
python_version = "3.13"
strict = true
plugins = ["pydantic.mypy", "sqlalchemy.ext.mypy.plugin"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "-v --tb=short --strict-markers"
markers = [
    "unit: Unit tests (no external dependencies)",
    "integration: Integration tests (require database/redis)",
    "e2e: End-to-end tests",
    "architecture: Architecture boundary tests",
]

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/migrations/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

### Dependency Installation

```bash
cd backend
uv sync --all-extras
```

---

## 3.2 FastAPI Initialization

### Application Factory Pattern

The FastAPI app SHALL be created via an application factory in `backend/src/app/main.py`.

Responsibilities:

```text
1. Load configuration from environment
2. Initialize database connection pool (async SQLAlchemy)
3. Initialize Redis connection pool
4. Register middleware (CORS, auth, rate limiting, request ID, tenant context)
5. Register module routers (/api/v1/<module>)
6. Register exception handlers
7. Register OpenTelemetry instrumentation
8. Register lifespan events (startup/shutdown)
```

### Module Registration Pattern

Each module exposes a single `router` from its `api/` package. The main app imports and mounts each:

```text
/api/v1/auth         → identity module
/api/v1/me           → users module
/api/v1/restaurants   → restaurants module
/api/v1/menus        → menus module (nested under restaurants per ACS 2.4)
/api/v1/checkout     → orders module (checkout flow)
/api/v1/orders       → orders module (post-creation management)
/api/v1/payments     → payments module
/api/v1/delivery-assignments → deliveries module
/api/v1/delivery-partners    → deliveries module
/api/v1/reviews      → reviews module
/api/v1/promotions   → promotions module
/api/v1/search       → menus module (search)
/api/v1/recommendations → AI module
/api/v1/admin/*      → admin routes across modules
```

---

## 3.3 Testing Setup

### Test Structure

```text
tests/
├── conftest.py                    — shared fixtures (db session, redis, test client)
├── unit/
│   └── modules/
│       └── <context>/
│           ├── domain/            — entity/VO/domain-service tests (no I/O)
│           └── application/       — use-case tests (mocked ports)
├── integration/
│   ├── conftest.py               — testcontainers fixtures
│   └── modules/
│       └── <context>/
│           ├── test_repositories.py
│           └── test_api.py
├── architecture/
│   └── test_import_boundaries.py — import-linter enforcement
└── e2e/
    └── test_order_flow.py        — full order lifecycle
```

### Test Commands

```bash
# All unit tests
uv run pytest tests/unit -m unit

# All integration tests (requires Docker)
uv run pytest tests/integration -m integration

# Architecture boundary tests
uv run pytest tests/architecture -m architecture

# Full suite with coverage
uv run pytest --cov=src --cov-report=html

# Parallel execution
uv run pytest -n auto
```

---

## 3.4 Alembic Setup

### Configuration

File: `backend/alembic.ini`

```ini
[alembic]
script_location = migrations
sqlalchemy.url = postgresql+asyncpg://%(DB_USER)s:%(DB_PASSWORD)s@%(DB_HOST)s:%(DB_PORT)s/%(DB_NAME)s
```

### Multi-Schema Migration Strategy

Per ADR 7.1 and Database Design Section 2, migrations are organized per module (schema):

```text
migrations/
├── env.py                          — multi-schema aware migration runner
├── script.py.mako                  — migration template
└── versions/
    ├── identity/                   — identity.* schema migrations
    ├── users/                      — users.* schema migrations
    ├── restaurants/                — restaurants.* schema migrations
    ├── menus/                      — menus.* schema migrations
    ├── orders/                     — orders.* schema migrations
    ├── payments/                   — payments.* schema migrations
    ├── deliveries/                 — deliveries.* schema migrations
    ├── notifications/              — notifications.* schema migrations
    ├── reviews/                    — reviews.* schema migrations
    ├── promotions/                 — promotions.* schema migrations
    └── analytics/                  — analytics.* schema migrations
```

### Migration Commands

```bash
# Generate migration for a specific module
uv run alembic -x module=identity revision --autogenerate -m "create accounts table"

# Run all pending migrations
uv run alembic upgrade head

# Run migrations for a specific module
uv run alembic -x module=orders upgrade head

# Rollback last migration
uv run alembic downgrade -1
```

---

## 3.5 Import Boundary Enforcement

File: `backend/.importlinter`

```ini
[importlinter]
root_packages =
    app
    modules
    shared

[importlinter:contract:module-isolation]
name = Modules must not import from each other directly
type = independence
modules =
    modules.identity
    modules.users
    modules.restaurants
    modules.menus
    modules.orders
    modules.payments
    modules.deliveries
    modules.notifications
    modules.reviews
    modules.promotions
    modules.analytics

[importlinter:contract:domain-layer-purity]
name = Domain layer must not import infrastructure
type = forbidden
source_modules =
    modules.identity.domain
    modules.users.domain
    modules.restaurants.domain
    modules.menus.domain
    modules.orders.domain
    modules.payments.domain
    modules.deliveries.domain
    modules.notifications.domain
    modules.reviews.domain
    modules.promotions.domain
forbidden_modules =
    sqlalchemy
    fastapi
    redis
    celery
    boto3
    httpx2
```

---

## 3.6 Local Development Setup

### Environment File

File: `backend/.env.example`

```env
# Application
APP_NAME=restaurant-platform
APP_ENV=local
APP_DEBUG=true
APP_HOST=0.0.0.0
APP_PORT=8000

# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=platform
DB_PASSWORD=platform_dev
DB_NAME=restaurant_platform

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# AWS (LocalStack for local dev)
AWS_ENDPOINT_URL=http://localhost:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_REGION=us-east-1

# S3
S3_BUCKET_ASSETS=platform-assets-local
S3_BUCKET_DOCUMENTS=platform-documents-local

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# OpenTelemetry
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_SERVICE_NAME=restaurant-platform-api
```

### Run Commands

```bash
# Start local development server
uv run uvicorn app.main:create_app --factory --reload --host 0.0.0.0 --port 8000

# Start Celery worker
uv run celery -A workers.celery_app worker --loglevel=info

# Start Celery Beat scheduler
uv run celery -A workers.celery_app beat --loglevel=info
```

---

# 4. Angular Bootstrap Plan

## 4.1 Workspace Creation

### Angular CLI Workspace

```bash
cd frontend
ng new admin-dashboard \
  --style=scss \
  --routing \
  --standalone
```

### Architecture

Plain Angular CLI workspace with path-mapped libraries (`@app/*` via tsconfig paths). Module boundary rules are enforced by `eslint-plugin-boundaries`. This avoids the overhead of Nx for a single-application workspace while preserving architectural isolation.

---

## 4.2 Architecture Alignment

### Library Structure

Libraries are created as plain directories under `libs/` and imported via tsconfig path mappings (`@app/*`). No ng-packagr or buildable libraries — path aliases resolve at build time.

```text
libs/
├── core/           — Configuration, DI, environment, guards, interceptors
├── shared/         — Reusable components, pipes, directives, utilities
├── design-system/  — Design tokens, themes, typography, component wrappers
├── api-client/     — Typed HTTP client for backend REST API
├── auth/           — Authentication feature (lazy-loaded)
├── dashboard/      — Dashboard feature (lazy-loaded)
├── users/          — Users management feature (lazy-loaded)
├── restaurants/    — Restaurants management feature (lazy-loaded)
├── orders/         — Orders management feature (lazy-loaded)
├── deliveries/     — Deliveries management feature (lazy-loaded)
├── payments/       — Payments management feature (lazy-loaded)
├── promotions/     — Promotions management feature (lazy-loaded)
├── reviews/        — Reviews management feature (lazy-loaded)
├── analytics/      — Analytics feature (lazy-loaded)
├── settings/       — Settings feature (lazy-loaded)
└── support/        — Support feature (lazy-loaded)
```

### Module Boundary Rules (eslint-plugin-boundaries)

File: `frontend/eslint.config.mjs`

```javascript
// Element types: app, core, shared, design-system, api-client, feature
// Dependency rules:
//   feature → can depend on: core, shared, design-system, api-client
//   shared → can depend on: core, design-system
//   core → nothing
//   design-system → can depend on: core
//   api-client → can depend on: core
```

---

## 4.3 Key Dependencies

```json
{
  "dependencies": {
    "@angular/core": "^22.0.0",
    "@angular/cdk": "^22.0.0",
    "@angular/material": "^22.0.0",
    "@ngrx/signals": "^21.1.1",
    "@angular/ssr": "^22.0.1",
    "express": "^5.1.0",
    "rxjs": "~7.8.0"
  },
  "devDependencies": {
    "@angular/build": "^22.0.1",
    "@angular/cli": "^22.0.1",
    "@playwright/test": "^1.52.0",
    "@tailwindcss/postcss": "^4.1.0",
    "angular-eslint": "^22.0.0",
    "eslint-plugin-boundaries": "^5.0.0",
    "tailwindcss": "^4.1.0",
    "typescript": "~6.0.2",
    "vitest": "^4.0.8"
  }
}
```

---

## 4.4 TailwindCSS v4 Setup

TailwindCSS v4 uses CSS-first configuration (no `tailwind.config.js`). The config lives in a plain CSS file.

File: `frontend/src/tailwind.css`

```css
@import "tailwindcss";

@theme {
  --font-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
}
```

The `@tailwindcss/postcss` plugin processes this at build time. The file is kept separate from `styles.scss` to avoid Sass `@import` conflicts.

---

## 4.5 Testing Setup

| Layer | Tool | Config File |
|---|---|---|
| Unit Tests | Vitest (native Angular 22 via `@angular/build:unit-test`) | `angular.json` |
| Component Tests | Angular Testing Library | (included in Vitest) |
| E2E Tests | Playwright | `playwright.config.ts` |
| Linting | ESLint + eslint-plugin-boundaries | `eslint.config.mjs` |
| Formatting | Prettier | `.prettierrc` |

### Test Commands

```bash
# Run all unit tests
npx ng test --watch=false

# Run tests with coverage
npm run test:ci

# Run e2e tests
npm run e2e

# Lint all (src + libs)
npx ng lint
```

---

# 5. Flutter Bootstrap Plan

## 5.1 Workspace Strategy

Use **Melos 7.x** with **Dart native workspaces** for multi-package Flutter monorepo management. Configuration lives in `mobile/pubspec.yaml` (not a separate `melos.yaml`).

File: `mobile/pubspec.yaml`

```yaml
name: restaurant_platform_mobile
publish_to: 'none'

environment:
  sdk: ^3.9.0

workspace:
  - apps/customer_app
  - apps/delivery_app
  - apps/restaurant_app
  - packages/analytics_pkg
  - packages/authentication
  - packages/core
  - packages/design_system
  - packages/localization
  - packages/maps
  - packages/networking
  - packages/realtime
  - packages/storage

dev_dependencies:
  melos: ^7.8.0

melos:
  name: restaurant_platform_mobile

  scripts:
    analyze:
      exec: dart analyze --fatal-infos
    test:
      exec: flutter test
    format:
      exec: dart format --set-exit-if-changed .
    generate:
      exec: dart run build_runner build --delete-conflicting-outputs
      packageFilters:
        dependsOn: build_runner
```

All child packages declare `resolution: workspace` in their pubspec.yaml.

---

## 5.2 Customer App Setup

```bash
cd mobile/apps
flutter create customer_app --org com.restaurantplatform --platforms android,ios
```

### Feature Map

```text
customer_app/lib/features/
├── authentication/     — Login, registration, OTP verification
├── home/              — Home screen, featured restaurants
├── restaurants/       — Restaurant discovery, restaurant detail
├── menus/             — Menu browsing, item detail
├── cart/              — Cart management
├── checkout/          — Checkout flow, payment selection
├── orders/            — Order history, order detail
├── tracking/          — Live order tracking, driver tracking
├── reviews/           — Review submission
├── profile/           — Profile management, addresses, preferences
└── promotions/        — Available coupons, active promotions
```

### Core Dependencies (`pubspec.yaml`)

```yaml
environment:
  sdk: ^3.9.0

resolution: workspace

dependencies:
  flutter:
    sdk: flutter
  flutter_riverpod: ^3.1.0
  go_router: ^17.0.0
  dio: ^5.9.0
  freezed_annotation: ^3.1.0
  json_annotation: ^4.12.0
  intl: ^0.20.2
  # Shared packages (path dependencies)
  design_system:
    path: ../../packages/design_system
  core:
    path: ../../packages/core
  networking:
    path: ../../packages/networking
  authentication:
    path: ../../packages/authentication
  realtime:
    path: ../../packages/realtime

dev_dependencies:
  flutter_test:
    sdk: flutter
  build_runner: ^2.4.0
  freezed: ^3.2.0
  json_serializable: ^6.14.0
  mocktail: ^1.0.4
  very_good_analysis: ^10.0.0
```

---

## 5.3 Restaurant App Setup

```bash
cd mobile/apps
flutter create restaurant_app --org com.restaurantplatform --platforms android,ios
```

### Feature Map

```text
restaurant_app/lib/features/
├── authentication/        — Login, restaurant onboarding application
├── dashboard/            — KPI overview, quick actions
├── orders/               — Incoming orders, order management, kitchen display
├── menu_management/      — CRUD menu categories, items, modifiers, availability
├── restaurant_profile/   — Business info, operating hours, delivery zones
├── staff/                — Staff management, role assignment
├── promotions/           — Promotion management
├── analytics/            — Sales insights, customer insights
└── settings/             — Notification preferences, app settings
```

---

## 5.4 Delivery App Setup

```bash
cd mobile/apps
flutter create delivery_app --org com.restaurantplatform --platforms android,ios
```

### Feature Map

```text
delivery_app/lib/features/
├── authentication/       — Login, partner onboarding application
├── availability/         — Online/offline toggle, availability management
├── assignments/          — Incoming assignments, accept/decline
├── navigation/           — Route guidance, pickup navigation, delivery navigation
├── deliveries/           — Active delivery, pickup confirmation, proof of delivery
├── earnings/             — Earnings overview, payout history
├── profile/              — Profile management, documents, vehicle info
└── settings/             — Notification preferences, app settings
```

---

## 5.5 Shared Packages Setup

Each package is created as a Flutter/Dart package:

```bash
cd mobile/packages
flutter create --template=package design_system
flutter create --template=package core
flutter create --template=package networking
flutter create --template=package authentication
flutter create --template=package realtime
flutter create --template=package analytics
flutter create --template=package localization
flutter create --template=package maps
flutter create --template=package storage
```

### Package Responsibilities

| Package | Contains |
|---|---|
| `design_system` | Design tokens, theme data, colors, typography, spacing, shared widgets (buttons, cards, inputs, dialogs) |
| `core` | Configuration, environment management, logging, error models, base types |
| `networking` | Dio HTTP client factory, interceptors (auth, retry, logging), response serialization |
| `authentication` | JWT token management, secure storage wrapper, session handling, refresh flow |
| `realtime` | WebSocket client, subscription management, event routing, reconnection with exponential backoff |
| `analytics` | Analytics event tracking, screen view tracking, standardized event schema |
| `localization` | Translation files, locale management, RTL support |
| `maps` | Maps provider abstraction, Google Maps / Mapbox adapter, geocoding |
| `storage` | Local storage abstraction (Hive/SQLite), offline queue, sync engine |

---

## 5.6 Analysis Options

File: `mobile/apps/customer_app/analysis_options.yaml` (shared across all apps/packages)

```yaml
include: package:flutter_lints/flutter.yaml

analyzer:
  strong-mode:
    implicit-casts: false
    implicit-dynamic: false
  errors:
    missing_return: error
    missing_required_param: error

linter:
  rules:
    - always_declare_return_types
    - annotate_overrides
    - avoid_empty_else
    - avoid_print
    - avoid_relative_lib_imports
    - avoid_returning_null_for_future
    - cancel_subscriptions
    - close_sinks
    - prefer_const_constructors
    - prefer_const_declarations
    - prefer_final_fields
    - prefer_final_locals
    - require_trailing_commas
    - sort_constructors_first
    - unawaited_futures
```

---

# 6. Infrastructure Bootstrap Plan

## 6.1 Terraform Structure

```text
infrastructure/terraform/
├── modules/
│   ├── networking/
│   │   ├── main.tf           — VPC, subnets, NAT, route tables, security groups
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── compute/
│   │   ├── main.tf           — ECS cluster, task definitions, services, ALB
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── database/
│   │   ├── main.tf           — RDS PostgreSQL, parameter groups, subnet groups
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── cache/
│   │   ├── main.tf           — ElastiCache Redis, subnet groups
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── storage/
│   │   ├── main.tf           — S3 buckets, lifecycle policies, CloudFront
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── cdn/
│   │   ├── main.tf           — CloudFront distributions
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── monitoring/
│   │   ├── main.tf           — CloudWatch, alarms, dashboards, log groups
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── security/
│   │   ├── main.tf           — WAF, Secrets Manager, KMS, IAM roles
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── ci-cd/
│   │   ├── main.tf           — ECR repositories, IAM for GitHub Actions OIDC
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── dns/
│       ├── main.tf           — Route 53 hosted zone, records
│       ├── variables.tf
│       └── outputs.tf
│
├── environments/
│   ├── dev/
│   │   ├── main.tf           — Module composition for dev
│   │   ├── variables.tf      — Dev-specific variable declarations
│   │   ├── terraform.tfvars  — Dev values (committed, non-sensitive)
│   │   ├── outputs.tf
│   │   └── backend.tf        — S3 remote state config for dev
│   ├── staging/
│   │   └── (same structure)
│   └── production/
│       └── (same structure)
│
└── .terraform-version
```

### Terraform Version

```text
Terraform >= 1.9
AWS Provider >= 5.70
```

### Remote State

```text
Backend: S3
Bucket: restaurant-platform-terraform-state-<account-id>
Key: <environment>/terraform.tfstate
DynamoDB Lock Table: terraform-state-lock
Encryption: AES-256 (SSE-S3)
```

---

## 6.2 AWS Account Preparation

### Account Structure (Recommended)

| Account | Purpose | AWS Account |
|---|---|---|
| Shared Services | Terraform state, ECR, monitoring, DNS | `shared-services` |
| Development | Dev environment | `dev` |
| Staging | Pre-production validation | `staging` |
| Production | Live customer traffic | `production` |

### Phase 1 Minimum

If multi-account is too heavy for initial setup, a single AWS account with environment isolation via:

```text
1. Separate VPCs per environment
2. IAM role separation per environment
3. Resource tagging: Environment=dev|staging|production
4. Separate S3 state buckets per environment
```

### Prerequisites

```text
1. AWS Organization created
2. IAM Identity Center configured
3. Billing alerts configured
4. CloudTrail enabled (all regions)
5. GuardDuty enabled
6. Default VPC deleted in all regions
7. Service Control Policies applied (deny unused regions)
```

---

## 6.3 Environment Strategy

| Environment | Purpose | Scale | Infra Characteristics |
|---|---|---|---|
| Local | Developer productivity | Single machine | Docker Compose: PostgreSQL, Valkey (Redis-compatible), LocalStack (S3/SQS/SNS) |
| Development | Feature validation | Minimal | Single AZ, smallest instances, single NAT, no HA |
| Staging | Production validation | Reduced | Production-like topology, smaller instances |
| Production | Live traffic | Full | Multi-AZ, auto-scaling, HA, monitoring, backups |

### Environment Parity

All environments SHALL use:

```text
Same Terraform modules (different variables)
Same Docker images (different config)
Same database schema (different data)
Same CI/CD pipeline (different deploy targets)
```

---

## 6.4 Secrets Strategy

### AWS Secrets Manager Layout

```text
/<environment>/database/credentials          — DB username/password
/<environment>/redis/auth-token              — Redis AUTH token
/<environment>/jwt/signing-key               — JWT secret key
/<environment>/payment-gateway/api-key       — Payment gateway credentials
/<environment>/sms/api-key                   — SMS provider credentials
/<environment>/email/smtp-credentials        — SES SMTP credentials
/<environment>/oauth/google-client-secret    — Google OAuth secret
/<environment>/maps/api-key                  — Maps provider API key
/<environment>/openai/api-key                — OpenAI API key
/<environment>/fcm/server-key               — Firebase Cloud Messaging key
```

### Secret Access Pattern

```text
1. ECS Task Role → Secrets Manager (IAM policy)
2. Secrets injected as environment variables at task start
3. No secrets in source code, Docker images, or CI/CD logs
4. Automatic rotation enabled for database credentials
5. Application reads secrets via Pydantic Settings from env vars
```

### Local Development Secrets

```text
1. Use .env file (git-ignored)
2. .env.example committed with placeholder values
3. No real credentials in .env.example
```

---

# 7. CI/CD Bootstrap Plan

## 7.1 Backend CI

File: `.github/workflows/backend-ci.yml`

### Triggers

```text
Push: develop, main, feature/**, fix/**
Pull Request: develop, main
Paths: backend/**, .github/workflows/backend-ci.yml
```

### Jobs

```text
Job: lint
  Steps:
    1. Checkout
    2. Setup Python 3.13
    3. Install uv
    4. uv sync --all-extras
    5. ruff check src/ tests/
    6. ruff format --check src/ tests/
    7. mypy src/

Job: test-unit
  Steps:
    1. Checkout
    2. Setup Python 3.13
    3. Install uv
    4. uv sync --all-extras
    5. pytest tests/unit -m unit --cov=src --cov-report=xml

Job: test-integration
  Needs: lint
  Services: postgres:17, redis:7
  Steps:
    1. Checkout
    2. Setup Python 3.13
    3. Install uv
    4. uv sync --all-extras
    5. alembic upgrade head
    6. pytest tests/integration -m integration

Job: test-architecture
  Steps:
    1. Checkout
    2. Setup Python 3.13
    3. Install uv
    4. uv sync --all-extras
    5. import-linter --config .importlinter

Job: build
  Needs: [test-unit, test-integration, test-architecture]
  Steps:
    1. Checkout
    2. Build Docker image
    3. Push to ECR (on develop/main only)
```

---

## 7.2 Frontend CI

File: `.github/workflows/frontend-ci.yml`

### Triggers

```text
Push: develop, main, feature/**, fix/**
Pull Request: develop, main
Paths: frontend/**, .github/workflows/frontend-ci.yml
```

### Jobs

```text
Job: lint
  Steps:
    1. Checkout
    2. Setup Node.js 22
    3. npm ci
    4. npx ng lint

Job: test
  Steps:
    1. Checkout
    2. Setup Node.js 22
    3. npm ci
    4. npm run test:ci

Job: build
  Needs: [lint, test]
  Steps:
    1. Checkout
    2. Setup Node.js 22
    3. npm ci
    4. npm run build:prod
    5. Upload build artifacts

Job: e2e
  Needs: build
  Steps:
    1. Checkout
    2. Setup Node.js 22
    3. npm ci
    4. npx playwright install --with-deps
    5. npm run e2e
```

---

## 7.3 Flutter CI

File: `.github/workflows/flutter-ci.yml`

### Triggers

```text
Push: develop, main, feature/**, fix/**
Pull Request: develop, main
Paths: mobile/**, .github/workflows/flutter-ci.yml
```

### Jobs

```text
Job: analyze
  Steps:
    1. Checkout
    2. Setup Flutter (stable)
    3. melos bootstrap
    4. melos run analyze

Job: format
  Steps:
    1. Checkout
    2. Setup Flutter (stable)
    3. melos bootstrap
    4. melos run format

Job: test
  Needs: [analyze, format]
  Steps:
    1. Checkout
    2. Setup Flutter (stable)
    3. melos bootstrap
    4. melos run test

Job: build-android
  Needs: test
  Steps:
    1. Checkout
    2. Setup Flutter (stable)
    3. Setup Java 17
    4. melos bootstrap
    5. cd apps/customer_app && flutter build apk --release
    6. cd apps/restaurant_app && flutter build apk --release
    7. cd apps/delivery_app && flutter build apk --release

Job: build-ios
  Needs: test
  Runs-on: macos-latest
  Steps:
    1. Checkout
    2. Setup Flutter (stable)
    3. melos bootstrap
    4. cd apps/customer_app && flutter build ios --release --no-codesign
    5. cd apps/restaurant_app && flutter build ios --release --no-codesign
    6. cd apps/delivery_app && flutter build ios --release --no-codesign
```

---

## 7.4 Infrastructure CI

File: `.github/workflows/infrastructure-ci.yml`

### Triggers

```text
Push: develop, main
Pull Request: develop, main
Paths: infrastructure/terraform/**, .github/workflows/infrastructure-ci.yml
```

### Jobs

```text
Job: validate
  Steps:
    1. Checkout
    2. Setup Terraform
    3. terraform fmt -check -recursive
    4. terraform init (per environment)
    5. terraform validate (per environment)

Job: plan
  Needs: validate
  Steps:
    1. Checkout
    2. Configure AWS credentials (OIDC)
    3. Setup Terraform
    4. terraform init
    5. terraform plan -out=tfplan
    6. Post plan output as PR comment

Job: apply (manual trigger on main only)
  Needs: plan
  Steps:
    1. Checkout
    2. Configure AWS credentials (OIDC)
    3. Setup Terraform
    4. terraform init
    5. terraform apply -auto-approve tfplan
```

---

## 7.5 Security Scan

File: `.github/workflows/security-scan.yml`

### Triggers

```text
Pull Request: develop, main
Schedule: Weekly (cron)
```

### Jobs

```text
Job: dependency-scan
  Steps:
    1. Checkout
    2. Run GitHub dependency review action
    3. Run pip-audit (backend)
    4. Run npm audit (frontend)
    5. Run flutter pub outdated (mobile)

Job: secret-scan
  Steps:
    1. Checkout
    2. Run gitleaks
    3. Run trufflehog

Job: sast
  Steps:
    1. Checkout
    2. Run bandit (Python SAST)
    3. Run semgrep (cross-language)

Job: container-scan
  Steps:
    1. Build Docker images
    2. Run Trivy container scan
```

---

# 8. Local Development Environment

## 8.1 Developer Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Git | >= 2.40 | Version control |
| Docker Desktop | >= 4.30 | Container runtime |
| Docker Compose | >= 2.28 | Local service orchestration |
| Python | 3.13+ | Backend runtime |
| uv | >= 0.5 | Python package management |
| Node.js | 22 LTS | Angular build tooling |
| npm | >= 10 | Node package management |
| Flutter | Stable (latest) | Mobile development |
| Dart | (bundled with Flutter) | Dart SDK |
| Android Studio | Latest | Android development + emulator |
| Xcode | Latest (macOS only) | iOS development + simulator |
| Terraform | >= 1.9 | Infrastructure management |
| AWS CLI | v2 | AWS interactions |
| Melos | Latest | Flutter monorepo tooling |
| pre-commit | >= 4.0 | Git hook management |

---

## 8.2 Installation Sequence

```text
Step 1: Clone Repository
  git clone git@github.com:<org>/restaurant-platform.git
  cd restaurant-platform

Step 2: Start Local Services
  cd infrastructure/docker
  docker compose up -d

Step 3: Setup Backend
  cd backend
  cp .env.example .env
  uv sync --all-extras
  uv run alembic upgrade head
  uv run python -m scripts.seed_data  (optional)
  uv run uvicorn app.main:create_app --factory --reload

Step 4: Setup Frontend
  cd frontend
  npm ci
  npm start

Step 5: Setup Mobile (any app)
  cd mobile
  dart pub get
  dart run melos bootstrap
  cd apps/customer_app
  flutter run

Step 6: Install Git Hooks
  cd <repo-root>
  pre-commit install
```

---

## 8.3 Local Services (Docker Compose)

File: `infrastructure/docker/docker-compose.yml`

### Services

| Service | Image | Port | Purpose |
|---|---|---|---|
| `postgres` | `postgis/postgis:17-3.5` | `5432` | PostgreSQL with PostGIS |
| `valkey` | `valkey/valkey:8-alpine` | `6379` | Valkey cache/pubsub (Redis-compatible, open-source) |
| `localstack` | `localstack/localstack:latest` | `4566` | AWS service emulation (SNS/SQS/SES) |
| `mailpit` | `axllent/mailpit:latest` | `1025`, `8025` | Email testing (SMTP + Web UI) |

### PostgreSQL Initialization

The `postgres` service SHALL mount `infrastructure/docker/postgres/init-scripts/` which:

```text
1. Creates the platform database
2. Creates database roles (app_tenant_scoped, app_admin)
3. Enables required extensions (pg_trgm, postgis, btree_gist)
4. Creates all module schemas (identity, users, restaurants, menus, orders, payments, deliveries, notifications, reviews, promotions, analytics)
```

### Docker Compose Override

Developers MAY create `docker-compose.override.yml` (git-ignored) for personal customizations:

```text
Port remapping
Volume mounts
Resource limits
Additional debug services (pgAdmin, RedisInsight)
```

---

## 8.4 Makefile

File: `Makefile` (root of repository)

```makefile
# ---- Local Infrastructure ----
.PHONY: infra-up infra-down infra-reset

infra-up:
 cd infrastructure/docker && docker compose up -d

infra-down:
 cd infrastructure/docker && docker compose down

infra-reset:
 cd infrastructure/docker && docker compose down -v && docker compose up -d

# ---- Backend ----
.PHONY: backend-install backend-dev backend-test backend-lint backend-migrate

backend-install:
 cd backend && uv sync --all-extras

backend-dev:
 cd backend && uv run uvicorn app.main:create_app --factory --reload --host 0.0.0.0 --port 8000

backend-test:
 cd backend && uv run pytest

backend-lint:
 cd backend && uv run ruff check src/ tests/ && uv run mypy src/

backend-migrate:
 cd backend && uv run alembic upgrade head

# ---- Frontend ----
.PHONY: frontend-install frontend-dev frontend-test frontend-lint frontend-build

frontend-install:
 cd frontend && npm ci

frontend-dev:
 cd frontend && npm start

frontend-test:
 cd frontend && npm test -- --watch=false

frontend-lint:
 cd frontend && npx ng lint

frontend-build:
 cd frontend && npm run build:prod

# ---- Mobile ----
.PHONY: mobile-install mobile-test mobile-analyze

mobile-install:
 cd mobile && dart pub get && dart run melos bootstrap

mobile-test:
 cd mobile && dart run melos run test

mobile-analyze:
 cd mobile && dart run melos run analyze

# ---- All ----
.PHONY: install test lint

install: backend-install frontend-install mobile-install

test: backend-test frontend-test mobile-test

lint: backend-lint frontend-lint mobile-analyze
```

---

# 9. Sprint 0 Plan

All tasks below MUST be completed before business feature development begins.

## 9.1 Repository Setup (Days 1-2)

| # | Task | Owner | Depends On |
|---|---|---|---|
| S0-001 | Create GitHub repository `restaurant-platform` | DevOps Lead | — |
| S0-002 | Configure repository settings (Section 1.2) | DevOps Lead | S0-001 |
| S0-003 | Apply branch protection rules (Section 1.3) | DevOps Lead | S0-001 |
| S0-004 | Create labels (Section 1.4) | DevOps Lead | S0-001 |
| S0-005 | Create milestones (Section 1.5) | DevOps Lead | S0-001 |
| S0-006 | Create CODEOWNERS file (Section 2.3) | DevOps Lead | S0-001 |
| S0-007 | Create issue templates and PR template | DevOps Lead | S0-001 |
| S0-008 | Create complete directory structure (Section 2.1) | Backend Lead | S0-001 |
| S0-009 | Create .gitignore, .gitattributes, .editorconfig | Backend Lead | S0-001 |
| S0-010 | Create root Makefile (Section 8.4) | Backend Lead | S0-008 |
| S0-011 | Create CLAUDE.md with project conventions | Backend Lead | S0-008 |
| S0-012 | Copy approved architecture documents to docs/ | Backend Lead | S0-008 |

---

## 9.2 Backend Bootstrap (Days 2-4)

| # | Task | Owner | Depends On |
|---|---|---|---|
| S0-020 | Initialize uv project with pyproject.toml (Section 3.1) | Backend Lead | S0-008 |
| S0-021 | Create FastAPI application factory (Section 3.2) | Backend Lead | S0-020 |
| S0-022 | Create shared kernel (base entity, value objects, events) | Backend Lead | S0-020 |
| S0-023 | Create database connection module (async SQLAlchemy) | Backend Lead | S0-021 |
| S0-024 | Create Redis connection module | Backend Lead | S0-021 |
| S0-025 | Create Alembic configuration (Section 3.4) | Backend Lead | S0-023 |
| S0-026 | Create initial schema creation migrations (all 11 schemas) | Backend Lead | S0-025 |
| S0-027 | Configure import-linter boundaries (Section 3.5) | Backend Lead | S0-020 |
| S0-028 | Create module scaffolding (empty modules with correct layers) | Backend Lead | S0-022 |
| S0-029 | Create health check endpoint (`GET /health`) | Backend Lead | S0-021 |
| S0-030 | Create test infrastructure (conftest, fixtures) (Section 3.3) | Backend Lead | S0-023 |
| S0-031 | Create Dockerfile and Dockerfile.worker | Backend Lead | S0-021 |
| S0-032 | Create .env.example (Section 3.6) | Backend Lead | S0-021 |
| S0-033 | Configure Celery app with Redis broker | Backend Lead | S0-024 |
| S0-034 | Configure OpenTelemetry instrumentation | Backend Lead | S0-021 |
| S0-035 | Configure structured logging (structlog) | Backend Lead | S0-021 |
| S0-036 | Create middleware: request ID, CORS, error handler | Backend Lead | S0-021 |

---

## 9.3 Frontend Bootstrap (Days 3-5)

| # | Task | Owner | Depends On |
|---|---|---|---|
| S0-040 | Create Angular CLI workspace (Section 4.1) | Frontend Lead | S0-008 |
| S0-041 | Create core, shared, design-system, api-client libs | Frontend Lead | S0-040 |
| S0-042 | Create feature libraries (one per bounded context) | Frontend Lead | S0-041 |
| S0-043 | Configure TailwindCSS v4 (Section 4.4) | Frontend Lead | S0-040 |
| S0-044 | Configure Angular Material M3 theming (WCAG AA) | Frontend Lead | S0-041 |
| S0-045 | Configure eslint-plugin-boundaries rules (Section 4.2) | Frontend Lead | S0-042 |
| S0-046 | Configure Vitest testing (Section 4.5) | Frontend Lead | S0-040 |
| S0-047 | Configure Playwright E2E | Frontend Lead | S0-040 |
| S0-048 | Configure ESLint + Prettier | Frontend Lead | S0-040 |
| S0-049 | Create Dockerfile for admin dashboard | Frontend Lead | S0-040 |
| S0-050 | Setup environment configuration (dev, staging, prod) | Frontend Lead | S0-040 |

---

## 9.4 Mobile Bootstrap (Days 3-5)

| # | Task | Owner | Depends On |
|---|---|---|---|
| S0-060 | Create customer_app Flutter project (Section 5.2) | Mobile Lead | S0-008 |
| S0-061 | Create restaurant_app Flutter project (Section 5.3) | Mobile Lead | S0-008 |
| S0-062 | Create delivery_app Flutter project (Section 5.4) | Mobile Lead | S0-008 |
| S0-063 | Create shared packages (Section 5.5) | Mobile Lead | S0-008 |
| S0-064 | Configure Melos workspace (Section 5.1) | Mobile Lead | S0-060 |
| S0-065 | Setup design_system package with base theme | Mobile Lead | S0-063 |
| S0-066 | Setup core package (config, logging, error models) | Mobile Lead | S0-063 |
| S0-067 | Setup networking package (Dio client, interceptors) | Mobile Lead | S0-063 |
| S0-068 | Setup authentication package (JWT, secure storage) | Mobile Lead | S0-063 |
| S0-069 | Configure analysis_options.yaml (Section 5.6) | Mobile Lead | S0-064 |
| S0-070 | Configure Riverpod in all apps | Mobile Lead | S0-060 |
| S0-071 | Configure GoRouter in all apps | Mobile Lead | S0-060 |

---

## 9.5 Infrastructure Bootstrap (Days 2-5)

| # | Task | Owner | Depends On |
|---|---|---|---|
| S0-080 | Create Terraform module structure (Section 6.1) | DevOps Lead | S0-008 |
| S0-081 | Create Docker Compose for local dev (Section 8.3) | DevOps Lead | S0-008 |
| S0-082 | Create PostgreSQL init scripts (schemas, roles, extensions) | DevOps Lead | S0-081 |
| S0-083 | Configure Terraform remote state (S3 + DynamoDB) | DevOps Lead | S0-080 |
| S0-084 | Create networking Terraform module (VPC, subnets) | DevOps Lead | S0-083 |
| S0-085 | Create ECR repository Terraform module | DevOps Lead | S0-083 |
| S0-086 | Create GitHub Actions OIDC IAM role for AWS | DevOps Lead | S0-083 |
| S0-087 | Create Secrets Manager entries for dev environment | DevOps Lead | S0-083 |
| S0-088 | Create dev environment Terraform configuration | DevOps Lead | S0-084 |

---

## 9.6 CI/CD Setup (Days 3-5)

| # | Task | Owner | Depends On |
|---|---|---|---|
| S0-100 | Create backend-ci.yml workflow (Section 7.1) | DevOps Lead | S0-020 |
| S0-101 | Create frontend-ci.yml workflow (Section 7.2) | DevOps Lead | S0-040 |
| S0-102 | Create flutter-ci.yml workflow (Section 7.3) | DevOps Lead | S0-060 |
| S0-103 | Create infrastructure-ci.yml workflow (Section 7.4) | DevOps Lead | S0-080 |
| S0-104 | Create security-scan.yml workflow (Section 7.5) | DevOps Lead | S0-020 |
| S0-105 | Create release.yml workflow (manual dispatch) | DevOps Lead | S0-100 |
| S0-106 | Create dependabot.yml configuration | DevOps Lead | S0-001 |
| S0-107 | Configure GitHub Actions secrets (AWS creds, etc.) | DevOps Lead | S0-086 |

---

## 9.7 Code Quality Tools (Days 2-3)

| # | Task | Owner | Depends On |
|---|---|---|---|
| S0-110 | Configure pre-commit hooks (Section tools/) | Backend Lead | S0-020 |
| S0-111 | Create .pre-commit-config.yaml | Backend Lead | S0-110 |
| S0-112 | Configure ruff (linting + formatting) | Backend Lead | S0-020 |
| S0-113 | Configure mypy (strict mode) | Backend Lead | S0-020 |
| S0-114 | Configure ESLint for Angular | Frontend Lead | S0-040 |
| S0-115 | Configure Prettier for Angular | Frontend Lead | S0-040 |
| S0-116 | Configure dart analyze for Flutter | Mobile Lead | S0-064 |
| S0-117 | Create .editorconfig | Backend Lead | S0-008 |

### Pre-commit Configuration

File: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
      - id: detect-private-key
      - id: check-added-large-files
        args: ['--maxkb=1000']

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.22.1
    hooks:
      - id: gitleaks
```

---

## 9.8 Monitoring Foundation (Days 4-5)

| # | Task | Owner | Depends On |
|---|---|---|---|
| S0-120 | Configure OpenTelemetry SDK in backend | Backend Lead | S0-034 |
| S0-121 | Configure structured logging format | Backend Lead | S0-035 |
| S0-122 | Create health check endpoints (liveness + readiness) | Backend Lead | S0-029 |
| S0-123 | Create CloudWatch log groups (Terraform) | DevOps Lead | S0-088 |
| S0-124 | Create basic CloudWatch dashboard (Terraform) | DevOps Lead | S0-123 |
| S0-125 | Configure CloudWatch alarms (P1: platform down, DB down) | DevOps Lead | S0-123 |

---

## 9.9 Secrets Management (Days 2-3)

| # | Task | Owner | Depends On |
|---|---|---|---|
| S0-130 | Create Secrets Manager entries (Section 6.4) | DevOps Lead | S0-087 |
| S0-131 | Create IAM policy for ECS task secret access | DevOps Lead | S0-086 |
| S0-132 | Configure Pydantic Settings to read from env vars | Backend Lead | S0-021 |
| S0-133 | Document secret rotation procedure | DevOps Lead | S0-130 |

---

# 10. First Commit Strategy

## 10.1 Commit Sequence

Commits are ordered to build on each other and keep the repository in a passing-CI state at every step.

| Commit # | Branch | Description | Contains |
|---|---|---|---|
| 1 | `main` | Initial repository setup | README.md, LICENSE, .gitignore, .gitattributes, .editorconfig |
| 2 | `develop` | Create develop branch | Branch creation from main |
| 3 | `chore/infra/docker-compose` | Local development environment | Docker Compose, init scripts, Makefile |
| 4 | `chore/backend/bootstrap` | Backend project skeleton | pyproject.toml, app factory, shared kernel, module scaffolds, Alembic config, Dockerfiles, .importlinter |
| 5 | `chore/backend/initial-migrations` | Database schema creation | Alembic migrations for all 11 schemas with extensions |
| 6 | `chore/backend/ci-pipeline` | Backend CI workflow | backend-ci.yml, security-scan.yml |
| 7 | `chore/frontend/bootstrap` | Angular workspace skeleton | Nx workspace, core/shared/design-system libs, feature libs, Tailwind, Dockerfile |
| 8 | `chore/frontend/ci-pipeline` | Frontend CI workflow | frontend-ci.yml |
| 9 | `chore/mobile/bootstrap` | Flutter workspace skeleton | Melos, all 3 apps, all shared packages |
| 10 | `chore/mobile/ci-pipeline` | Flutter CI workflow | flutter-ci.yml |
| 11 | `chore/infra/terraform-foundation` | Terraform modules + dev environment | All Terraform modules, dev config, infrastructure-ci.yml |
| 12 | `chore/docs/architecture` | Architecture documentation | All approved architecture specs in docs/ |
| 13 | `chore/tools/pre-commit` | Code quality tooling | .pre-commit-config.yaml, commit-msg hook |

Each commit is a PR → `develop`, squash-merged. After all Sprint 0 work is merged to `develop`, a release PR merges `develop` → `main` with tag `v0.0.1`.

---

## 10.2 Repository Milestones & Tags

| Tag | Description | Criteria |
|---|---|---|
| `v0.0.1` | Sprint 0 Complete — Repository bootstrapped | All Sprint 0 tasks complete, all CI pipelines green |
| `v0.1.0` | Sprint 1 Complete — Foundation | Identity module, core domain models, database schemas populated |
| `v0.2.0` | Sprint 2 Complete — Core Ordering | Menu browsing, cart, checkout, order placement working |
| `v0.3.0` | Sprint 3 Complete — Payments & Delivery | Payment capture, delivery assignment working |
| `v0.4.0` | Sprint 4 Complete — Mobile & Dashboard | Flutter apps functional, Angular dashboard functional |
| `v0.5.0` | Sprint 5 Complete — AI & Polish | AI features, comprehensive testing, hardening |
| `v1.0.0` | MVP Release | Production deployment |

---

## 10.3 Tagging Strategy

```text
Format: v<MAJOR>.<MINOR>.<PATCH>

MAJOR: Breaking changes or major release milestones
MINOR: Sprint completion / feature batch
PATCH: Bug fixes, hotfixes

Pre-release: v1.0.0-rc.1, v1.0.0-rc.2
```

Tags are created on the `main` branch only, after a release merge from `develop`.

---

# 11. Definition of Ready (for Sprint 1)

Sprint 1 SHALL NOT begin until ALL of the following conditions are met:

## 11.1 Repository & Tooling

- [ ] GitHub repository created with all settings applied
- [ ] Branch protection rules active on `main` and `develop`
- [ ] CODEOWNERS file in place
- [ ] Labels and milestones created
- [ ] .gitignore, .gitattributes, .editorconfig committed

## 11.2 Backend

- [ ] Backend project initializes and starts (`uvicorn` runs without errors)
- [ ] Health check endpoint returns 200
- [ ] All 11 PostgreSQL schemas created via Alembic migrations
- [ ] PostgreSQL extensions enabled (pg_trgm, postgis, btree_gist)
- [ ] Database roles created (app_tenant_scoped, app_admin)
- [ ] Import-linter passes with all module boundaries defined
- [ ] Shared kernel (base entity, value objects, event bus) exists
- [ ] Test infrastructure works (unit + integration test fixtures)
- [ ] Structured logging configured
- [ ] OpenTelemetry instrumentation configured
- [ ] Celery worker starts and connects to Redis

## 11.3 Frontend

- [ ] Angular CLI workspace builds successfully
- [ ] All feature libraries created and boundary rules enforced (eslint-plugin-boundaries)
- [ ] TailwindCSS v4 configured and working
- [ ] Angular Material M3 theming applied (WCAG AA compliant)
- [ ] Vitest tests run (at least one passing placeholder test)
- [ ] Playwright E2E infrastructure configured

## 11.4 Mobile

- [ ] All three Flutter apps build successfully (Android + iOS)
- [ ] Melos bootstrap runs without errors
- [ ] All shared packages resolve
- [ ] Riverpod + GoRouter configured in all apps
- [ ] Analyzer passes on all packages
- [ ] At least one passing widget test per app

## 11.5 Infrastructure

- [ ] Docker Compose starts all local services
- [ ] PostgreSQL accessible on localhost:5432
- [ ] Redis accessible on localhost:6379
- [ ] LocalStack S3 accessible on localhost:4566
- [ ] Terraform modules validate successfully
- [ ] Dev environment Terraform plan runs without errors

## 11.6 CI/CD

- [ ] backend-ci.yml runs and passes
- [ ] frontend-ci.yml runs and passes
- [ ] flutter-ci.yml runs and passes
- [ ] infrastructure-ci.yml runs and passes
- [ ] security-scan.yml runs and passes
- [ ] All CI secrets configured in GitHub Actions

## 11.7 Documentation

- [ ] All approved architecture specifications committed to docs/
- [ ] Development setup guide written and validated by a second developer
- [ ] Coding standards documented
- [ ] CLAUDE.md created with project conventions

---

# 12. Definition of Done (for MVP Implementation)

MVP implementation SHALL NOT be considered complete until ALL of the following conditions are met:

## 12.1 Functional Completeness

- [ ] All Phase 1 bounded contexts implemented (Identity, Users, Restaurants, Menus, Orders, Payments, Deliveries, Notifications, Reviews, Promotions)
- [ ] All Phase 1 API endpoints implemented per API Contract Specification
- [ ] All state machines implemented per DDD Specification Section 11
- [ ] All aggregate invariants enforced per DDD Specification Section 10
- [ ] Customer mobile app: full order lifecycle (browse → checkout → track → review)
- [ ] Restaurant mobile app: order management, menu management
- [ ] Delivery mobile app: assignment acceptance, navigation, proof of delivery
- [ ] Admin dashboard: user management, restaurant management, order management, analytics
- [ ] AI Phase 1 capabilities operational (semantic search, support assistant, recommendations)

## 12.2 Quality

- [ ] Backend unit test coverage >= 80% on business logic
- [ ] Backend integration tests pass for all critical workflows
- [ ] Architecture boundary tests pass (import-linter)
- [ ] Frontend unit test coverage >= 80% on state management
- [ ] Mobile widget test coverage >= 80% on critical flows
- [ ] E2E tests pass for critical user journeys (Section 9.6 of Frontend Spec)
- [ ] No P0 or P1 bugs open
- [ ] Security scan passes with no critical/high findings

## 12.3 Performance

- [ ] API latency P95 < 500ms under load test (Section 10 of AWS Infrastructure Spec)
- [ ] Load tested at 100 concurrent order writes/sec
- [ ] Database query performance validated (no N+1, slow queries < 100ms)
- [ ] WebSocket fan-out tested with 1000 concurrent connections
- [ ] Redis cache hit rate > 80% on hot paths

## 12.4 Security

- [ ] JWT authentication implemented and tested
- [ ] RBAC implemented for all roles per ACS Section 5
- [ ] PostgreSQL Row-Level Security policies active on all tenant-scoped tables
- [ ] Input validation on all endpoints (Pydantic)
- [ ] Rate limiting active on auth and public endpoints
- [ ] No secrets in source code (gitleaks passes)
- [ ] Payment tokenization verified (no raw card data stored)
- [ ] CORS restricted to known origins
- [ ] TLS configured on all external endpoints

## 12.5 Infrastructure

- [ ] Production environment provisioned via Terraform
- [ ] Multi-AZ deployment active
- [ ] Database backups configured (daily, 35-day retention)
- [ ] PITR enabled for PostgreSQL
- [ ] WAF enabled on ALB
- [ ] CloudTrail enabled
- [ ] GuardDuty enabled
- [ ] All secrets in AWS Secrets Manager
- [ ] Auto-scaling configured for ECS services

## 12.6 Observability

- [ ] Structured logging active across all services
- [ ] Distributed tracing active (OpenTelemetry)
- [ ] Platform dashboard operational (availability, latency, errors)
- [ ] Database dashboard operational (connections, slow queries, replication)
- [ ] P1 alerts configured and tested (platform down, database down, payment failures)
- [ ] P2 alerts configured (high error rate, queue backlog, Redis failure)

## 12.7 Operations

- [ ] CI/CD pipeline fully operational (commit → deploy)
- [ ] Deployment strategy validated (rolling deployment)
- [ ] Rollback procedure documented and tested
- [ ] Disaster recovery procedure documented
- [ ] Backup restore tested at least once
- [ ] Runbooks written for common operational scenarios

## 12.8 Documentation

- [ ] API documentation generated and accessible
- [ ] Development setup guide validated
- [ ] Deployment guide written
- [ ] Operational runbooks written
- [ ] Architecture documentation up to date

---

# Appendix A — Technology Version Matrix

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.13+ | Backend runtime |
| FastAPI | >= 0.115 | Web framework |
| SQLAlchemy | >= 2.0 | ORM |
| Alembic | >= 1.14 | Database migrations |
| PostgreSQL | 17 | Primary database |
| Valkey | 8 | Cache, pubsub, sessions (Redis-compatible, open-source) |
| Celery | >= 5.4 | Background processing |
| uv | >= 0.5 | Python package manager |
| Node.js | 22 LTS | Angular build tooling |
| Angular | v22 | Admin dashboard (CLI workspace) |
| Angular Material | v22 | UI component library (M3 theme) |
| TailwindCSS | v4 | Utility-first CSS (CSS-first config) |
| TypeScript | ~6.0 | Type checking (with `ignoreDeprecations: "6.0"`) |
| NgRx Signal Store | >= 21.1 | Angular state management |
| Vitest | >= 4.0 | Angular unit testing (native via `@angular/build:unit-test`) |
| eslint-plugin-boundaries | >= 5.0 | Angular module boundary enforcement |
| Flutter | Stable (Dart SDK ^3.9.0) | Mobile framework |
| Dart | >= 3.9.0 | Mobile language |
| flutter_riverpod | >= 3.1.0 | Flutter state management |
| go_router | >= 17.0.0 | Flutter navigation |
| Melos | >= 7.8 | Flutter workspace tooling (via Dart native workspace) |
| very_good_analysis | >= 10.0.0 | Flutter lint rules |
| Terraform | >= 1.9 | Infrastructure as code |
| AWS Provider (TF) | >= 5.70 | AWS Terraform provider |
| Docker | >= 27 | Containerization |
| Docker Compose | >= 2.28 | Local orchestration |
| GitHub Actions | N/A | CI/CD |
| OpenTelemetry | >= 1.27 | Observability |
| ruff | >= 0.7 | Python linting + formatting |
| mypy | >= 1.13 | Python type checking |
| OpenAI | API v1 | LLM provider |
| LangGraph | Latest | Agent orchestration |
| pgvector | Latest | Vector search (Phase 1+) |

---

# Appendix B — CLAUDE.md Template

File: `CLAUDE.md` (repository root)

```markdown
# CLAUDE.md — Restaurant Platform

## Project Overview
AI-Powered Multi-Vendor Restaurant Ordering Platform. Modular monolith architecture.

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
- `make backend-dev` — Start FastAPI dev server (port 8000)
- `make frontend-dev` — Start Angular dev server
- `make backend-test` — Run backend tests
- `make frontend-test` — Run frontend tests
- `make mobile-test` — Run Flutter tests

## Architecture Rules
- Each bounded context is an independent module under backend/src/modules/
- Modules MUST NOT import from each other directly (enforced by import-linter)
- Cross-module communication uses domain events only
- Domain layer has ZERO framework dependencies
- Database uses schema-per-module (identity.*, orders.*, etc.)
- Cross-schema references are by UUID only, no foreign keys
- All state changes go through explicit Unit of Work
- Multi-tenancy via Row-Level Security with restaurant_id as tenant key

## Coding Conventions
- Python: ruff for linting/formatting, mypy strict mode, 120 char line length
- Angular: ESLint + Prettier, eslint-plugin-boundaries for module rules, Angular Signals + NgRx Signal Store
- Flutter: dart analyze with strict mode, Riverpod for state, GoRouter for navigation
- Commits: conventional commits (feat:, fix:, chore:, docs:)
- PRs: squash merge to develop, merge commit to main
```

---

*End of Project Bootstrap & Repository Setup Specification v1.0. This document SHALL serve as the authoritative guide for creating the restaurant-platform repository from scratch.*
