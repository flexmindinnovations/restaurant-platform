# Codebase Index & Architecture Guide

Welcome to the **Restaurant Platform** codebase. This unified index serves as a fast-reference guide and architectural catalog to help you understand the codebase quickly, navigate between directories, and write code consistent with project standards.

---

## 🗺️ High-Level Directory Overview

The repository is organized as a multi-workspace platform:

```text
restaurant-platform/
├── docs/                 # Architectural specifications, status sheets, and style guides
│   ├── architecture/     # Specifications, ADRs (Architecture Decision Records) & Diagrams
│   ├── guides/           # Coding standards, Development setup, and Frontend UI guide
│   └── PROJECT_STATUS.md # Current sprint-by-sprint completion status
├── backend/              # Python FastAPI modular monolith (12 bounded contexts)
│   ├── src/modules/      # Independent module directories (Domain → App → Infra → API)
│   └── pyproject.toml    # strict typing (mypy) & linting/formatting (ruff) rules
├── frontend/             # Angular v22 Admin Dashboard (Angular CLI Workspace)
│   ├── src/app/          # Main application core, shell, and route definitions
│   └── libs/             # 16 path-mapped libraries representing pages & features
├── mobile/               # Flutter Monorepo managed with Melos (3 Apps + 9 Packages)
│   ├── apps/             # Customer App, Delivery App, and Restaurant App
│   └── packages/         # Shared packages (Design System, Networking, Authentication, etc.)
└── infrastructure/       # Terraform modules and local Docker Compose environments
```

---

## 💻 Frontend: Admin Dashboard (Angular v22)

The frontend is a modern Angular v22 single-page application built as an **Angular CLI workspace with path-mapped libraries** to maximize separation of concerns and build modularity.

### 📁 Directory Layout

* **Application Shell (`src/app/`)**: Holds main entrypoint, global Tailwind `styles.scss` and `tailwind.css`, configuration, and the layout `Shell` containing sidenav/navigation.
* **Shared Libraries (`libs/`)**: Features and core functionalities are located under `libs/` and imported into the shell using path-mapped aliases (`@app/*`).

### 🧩 Mapping of Libraries (`libs/`)

All libraries live under `/libs/` and expose their public API via `index.ts`. They are grouped by purpose:

| Path-Map Alias | Subfolder Path | Purpose / Scope |
| :--- | :--- | :--- |
| **`@app/core`** | `libs/core` | Zero-dependency core constants, interfaces, and core utility classes. |
| **`@app/design-system`** | `libs/design-system`| Modular UI design tokens (typography, colors, spacing) and glassmorphic card elements. |
| **`@app/api-client`** | `libs/api-client` | HTTP services, interceptors, and TypeScript models for interacting with the backend API. |
| **`@app/shared`** | `libs/shared` | Core UI pieces like status badges, theme-toggle, and theme providers. |
| **`@app/auth`** | `libs/auth` | Authentication guards, login/registration routes, and state. |
| **`@app/dashboard`** | `libs/dashboard` | Main admin summary dashboard page components & state. |
| **`@app/users`** | `libs/users` | Customer & system user administration list. |
| **`@app/restaurants`** | `libs/restaurants` | Restaurant listings, details, and interactive menu-item-dialog management. |
| **`@app/orders`** | `libs/orders` | Ordering dashboard lists and order detailed review components. |
| **`@app/deliveries`** | `libs/deliveries` | Active deliveries list & delivery mapping visualizer components. |
| **`@app/payments`** | `libs/payments` | Payment lists, service tracking, and state managers. |
| **`@app/promotions`** | `libs/promotions` | Promotion and discount code dashboard controls. |
| **`@app/reviews`** | `libs/reviews` | Multi-vendor customer feedback tables. |
| **`@app/analytics`** | `libs/analytics` | Materialized analytics tables and visual metrics dashboards. |
| **`@app/settings`** | `libs/settings` | System-wide configuration dashboard pages. |
| **`@app/support`** | `libs/support` | Active support queue and ticketing views. |

### ⛔ Dependency Boundaries (Enforced by `eslint-plugin-boundaries`)

To maintain high code quality and avoid spaghetti imports, strict dependency rules are enforced:

1. **`core`** cannot import from any other library.
2. **`design-system`** can only depend on `core`.
3. **`api-client`** can only depend on `core`.
4. **`shared`** can depend on `core` and `design-system`.
5. **Feature Libraries** (dashboard, users, orders, etc.) can depend on `core`, `shared`, `design-system`, and `api-client`.
6. **Feature Libraries MUST NOT import from each other.** (e.g. `orders` cannot import directly from `restaurants`).

### ⚡ Key Tech Conventions

* **Change Detection**: Strict `OnPush` change detection everywhere for optimal performance.
* **State Management**: Native `Angular Signals` combined with `@ngrx/signals` (**NgRx Signal Store**) for localized, reactive reactive state management.
* **Styling**: Powered by Angular Material M3 + **TailwindCSS v4** utilities.
* **Testing**: Native modern testing with **Vitest** for quick execution plus **Playwright** for complete End-to-End browser specs.

---

## 📱 Mobile: Flutter Workspace (Dart 3.9+)

The mobile platform uses a high-performance **Flutter multi-app workspace structured as a Melos monorepo**. This approach separates core feature applications from isolated shared Dart/Flutter packages.

### 📁 Directory Layout

* **`apps/`**: Complete, self-contained mobile applications representing different personas in the platform.
* **`packages/`**: Domain-agnostic packages representing underlying business kernels, UI widgets, and hardware interfaces.

### 📦 Personas / Applications (`apps/`)

1. **Customer App (`apps/customer_app`)**: User-facing application supporting restaurant search, semantic AI menu discovery, cart management, stripe checkout, live driver/order tracking, and order history.
2. **Delivery App (`apps/delivery_app`)**: App for delivery couriers to toggle availability, accept route proposals, display postgis delivery assignments, navigate map waypoints, and view earnings.
3. **Restaurant App (`apps/restaurant_app`)**: Portal for restaurant owners to track orders in real-time, modify menu items, oversee delivery handoffs, and view sales metrics.

### 🧩 Shared Packages (`packages/`)

All applications pull shared logic from modular packages:

| Package | Path | Responsibility |
| :--- | :--- | :--- |
| **`core`** | `packages/core` | Core models, constant definitions, generic utilities, and business rule boundaries. |
| **`design_system`**| `packages/design_system` | Common material-based design primitives, typography, custom icons, and visual elements. |
| **`networking`** | `packages/networking` | Base HTTP service configurations built on `Dio` (includes custom interceptors, auth inject, and error handling). |
| **`authentication`**| `packages/authentication` | Shared OAuth/JWT local session persistence, token automatic refreshes, and auth state. |
| **`maps`** | `packages/maps` | Google Maps integrations, delivery track helpers, and geo-coordinate calculations. |
| **`realtime`** | `packages/realtime` | WebSocket clients for low-latency live order progress & driver location updates. |
| **`storage`** | `packages/storage` | Key-value secure data caches and disk databases (e.g. Hive / SecureStorage). |
| **`localization`** | `packages/localization` | Platform internationalization, translated string resource files, and locale switchers. |
| **`analytics_pkg`**| `packages/analytics_pkg` | Centralized tracking events hook, routing logs, and debug trackers. |

### ⚡ Key Tech Conventions

* **State Management**: **Riverpod** (`flutter_riverpod`) with generated code support (`build_runner` + `riverpod_generator`) for safe dependency injection and caching.
* **Navigation**: **GoRouter** (`go_router`) for declarative, deep-link-friendly URL routing.
* **Data Models**: **Freezed** (`freezed`) + `json_serializable` for compile-safe immutable entities and serialization schemas.
* **Testing**: Unit & Widget testing via native Flutter Test runner with `mocktail` for mocks.

---

## ⚙️ Backend: Modular Monolith (FastAPI)

While frontend and mobile are front-and-center, understanding the FastAPI monolith architecture under `/backend` is key for modeling communication.

* **12 Bounded Contexts**: `Identity`, `Users`, `Restaurants`, `Menus`, `Orders`, `Payments`, `Deliveries`, `Notifications`, `Reviews`, `Promotions`, `Analytics`, `AI Services`.
* **Layered Architecture**: Every context folder strictly follows:
    `Domain` (No framework deps) ➡️ `Application` (Commands/Queries/UoW) ➡️ `Infrastructure` (DB/Cache) ➡️ `API` (Endpoints)
* **No Cross-Module Imports**: Enforced via Python **Import Linter**. Communication between modules is fully asynchronous via **Transactional Outbox Events** on an Event Bus.
* **Multi-Schema DB**: Isolation via separate Postgres Schemas per module (`identity.`, `orders.`, etc.).

---

## 🛠️ Developer Command Quick-Reference

### Workspace Root (Make commands)

| Command | Action |
| :--- | :--- |
| `make infra-up` | Spin up Postgres, Redis (Valkey), LocalStack, and Mailpit in Docker |
| `make infra-down` | Stop infrastructure containers |
| `make backend-dev` | Start the FastAPI backend API on `http://localhost:8000` |
| `make frontend-install` | Install dependencies for the Angular platform |
| `make frontend-dev` | Run the Angular Admin Dashboard development server |
| `make mobile-install` | Bootstrap Flutter apps & packages using Melos |

### Frontend Commands (from `frontend/`)

* `npm start` — Run developer Angular server on port `4200` (proxies `/api` requests to backend at `:8000`)
* `npm run build` — Compile highly optimized production artifact
* `npm test` — Run all unit test suites using high-speed Vitest
* `npm run lint` — Lint files and assert library isolation boundaries
* `npm run format` — Apply Prettier rules consistently

### Mobile Commands (from `mobile/` or using Melos)

* `dart run melos bootstrap` — Interlink and fetch dependencies for all workspace nodes
* `dart run melos run test` — Spin up tests across every app and shared package simultaneously
* `dart run melos run analyze` — Run strict code quality analysis in all directories
* `dart run melos run format-fix` — Instantly format Dart files globally
* `dart run melos run generate` — Build code generation files (`freezed`, `json_serializable`)
