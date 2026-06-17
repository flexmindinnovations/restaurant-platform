# Coding Standards

## Python (Backend)

### Tooling

| Tool | Purpose | Config |
|------|---------|--------|
| ruff | Linting + formatting | `pyproject.toml` `[tool.ruff]` |
| mypy | Static type checking (strict mode) | `pyproject.toml` `[tool.mypy]` |
| import-linter | Module boundary enforcement | `backend/.importlinter` |

### Style

- **Line length:** 120 characters
- **Target:** Python 3.13+
- **Formatter:** ruff format (Black-compatible)
- **Import order:** stdlib → third-party → first-party (enforced by ruff `I` rules)
- **Type hints:** Required on all public functions and methods
- **Docstrings:** Only when the "why" is non-obvious. No boilerplate docstrings.

### Naming

| Element | Convention | Example |
|---------|-----------|---------|
| Modules | snake_case | `account_repository.py` |
| Classes | PascalCase | `AccountRepository` |
| Functions | snake_case | `get_account_by_email` |
| Constants | UPPER_SNAKE | `MAX_LOGIN_ATTEMPTS` |
| Type vars | PascalCase + T suffix | `EntityT` |

### Architecture Rules

- **Domain layer** (`modules/*/domain/`): Zero framework imports. Pure Python, dataclasses, enums, ABCs only.
- **Application layer** (`modules/*/application/`): Depends on domain only. Uses ports (interfaces) for I/O.
- **Infrastructure layer** (`modules/*/infrastructure/`): Implements ports. SQLAlchemy, Redis, HTTP clients live here.
- **API layer** (`modules/*/api/`): FastAPI routes, Pydantic schemas. Thin — delegates to application layer.
- **Modules cannot import from each other.** Cross-module communication uses domain events via the event bus.

### Ruff Rules

The project enables a broad set of rules. Key categories:

```
E, W, F    — pycodestyle + pyflakes basics
I          — isort-compatible import sorting
N          — pep8-naming
UP         — pyupgrade (modern Python syntax)
S          — bandit security checks (S101 ignored for tests)
B          — bugbear (common pitfalls)
SIM        — simplify (unnecessary complexity)
TCH        — type-checking imports (move to TYPE_CHECKING block)
RUF        — ruff-specific rules
```

### Testing

- **pytest** with async support via `pytest-asyncio` (auto mode)
- **Markers:** `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.architecture`
- **Coverage target:** 80% on `src/`
- **Naming:** `test_<what>_<condition>_<expected>`, e.g., `test_place_order_empty_cart_raises`
- **Fixtures:** Shared in `conftest.py`, scoped appropriately (function/session)
- **Integration tests:** Use testcontainers for PostgreSQL and Redis

---

## Angular (Frontend)

### Tooling

| Tool | Purpose | Config |
|------|---------|--------|
| ESLint | Linting | `eslint.config.mjs` |
| Prettier | Formatting | `.prettierrc` |
| eslint-plugin-boundaries | Module boundary rules | `eslint.config.mjs` |
| Vitest | Unit tests | `angular.json` (`@angular/build:unit-test`) |
| Playwright | E2E tests | `playwright.config.ts` |

### Component Conventions

- **Standalone components** — no NgModules. Every component, directive, pipe is standalone.
- **OnPush change detection** — configured as default in `angular.json` schematics.
- **Signals** — prefer Angular Signals over RxJS for component state. Use `signal()`, `computed()`, `effect()`.
- **Input/Output** — use `input()`, `input.required()`, `output()` signal functions (not decorators).
- **File naming:** `<name>.ts` for single-class components (not `.component.ts`), e.g., `shell.ts`, `placeholder.ts`

### State Management

- **NgRx Signal Store** for feature-level state
- Each feature lib that needs state creates a store in `src/lib/<feature>.store.ts`
- Stores use `signalStore()`, `withState()`, `withComputed()`, `withMethods()`

### Library Structure

| Type | Path | Can import |
|------|------|------------|
| core | `libs/core/` | Nothing |
| design-system | `libs/design-system/` | core |
| api-client | `libs/api-client/` | core |
| shared | `libs/shared/` | core, design-system |
| feature | `libs/<feature>/` | core, shared, design-system, api-client |

**Features cannot import from other features.** This is enforced by `eslint-plugin-boundaries`.

### Routing

- All feature routes are lazy-loaded via `loadChildren`
- Routes are defined in each feature lib's `<feature>.routes.ts`
- Route data binding via `withComponentInputBinding()`

### Styling

- **Angular Material M3** theme in `src/styles.scss`
- **TailwindCSS v4** utilities in `src/tailwind.css` (separate file — do not mix with SCSS)
- **Component styles:** SCSS (configured in angular.json schematics)
- **WCAG AA** compliance: focus-visible outlines, reduced-motion support, skip-to-content link

### Testing

- **Vitest** for unit tests (native Angular 22 support via `@angular/build:unit-test`)
- Test files: `*.spec.ts` colocated with source
- **Playwright** for E2E tests in `e2e/`
- Target: 80% coverage on Signal Stores and services

---

## Flutter (Mobile)

### Tooling

| Tool | Purpose | Config |
|------|---------|--------|
| dart analyze | Static analysis (strict) | `analysis_options.yaml` |
| very_good_analysis | Lint rules | `analysis_options.yaml` |
| Melos | Workspace management | `mobile/pubspec.yaml` under `melos:` |
| mocktail | Mocking in tests | dev dependency |

### Architecture

- **Feature-first** directory structure: `lib/features/<feature>/`
- Each feature contains its screens, widgets, providers, and models
- Shared code lives in `packages/` (design_system, core, networking, authentication, etc.)

### State Management — Riverpod

- All apps wrap their root widget with `ProviderScope`
- Use `Provider` for singletons (router, HTTP client)
- Use `NotifierProvider` / `AsyncNotifierProvider` for mutable state
- Use `.family` modifier for parameterized providers
- Keep providers close to features that use them

### Navigation — GoRouter

- Router defined in `lib/navigation/router.dart` per app
- Router exposed as a Riverpod `Provider<GoRouter>`
- Use `context.goNamed('route')` for navigation (named routes)
- Auth guard via `redirect` parameter on GoRouter

### Naming

| Element | Convention | Example |
|---------|-----------|---------|
| Files | snake_case | `home_screen.dart` |
| Classes | PascalCase | `HomeScreen` |
| Providers | camelCase + Provider | `routerProvider` |
| Packages | snake_case | `design_system` |

### Code Generation

- **freezed** for immutable models: `@freezed class User with _$User { ... }`
- **json_serializable** for JSON parsing
- Generated files: `*.g.dart`, `*.freezed.dart` — excluded from analysis
- Run: `dart run melos run generate`

### Testing

- **Widget tests** for screens and complex widgets
- **Unit tests** for providers and business logic
- Test files in `test/` directory, mirroring `lib/` structure
- Use `ProviderScope` overrides for dependency injection in tests

---

## Git Conventions

### Branch Naming

```
feature/<context>/<short-description>    — new functionality
fix/<context>/<short-description>        — bug fixes
chore/<context>/<short-description>      — tooling, config, infra
docs/<short-description>                 — documentation only
release/v<major>.<minor>.<patch>         — release candidates
```

Examples: `feature/orders/place-order-flow`, `fix/payments/capture-timeout`, `chore/infra/terraform-vpc`

### Commit Messages

Conventional commits format (enforced by commit-msg hook):

```
type(scope): description

Types: feat | fix | chore | docs | refactor | test | perf | ci | build | style
Scope: optional, lowercase, bounded context name or area
```

Examples:
- `feat(orders): add place order endpoint`
- `fix(payments): handle timeout on capture`
- `chore(infra): update Docker Compose`
- `docs: update development setup guide`

### Pull Requests

- Target `develop` for feature work (squash merge)
- Target `main` for releases only (merge commit)
- PR title follows commit convention: `feat(orders): add checkout flow`
- Fill in the PR template (summary, test plan, breaking changes)
- Require at least 1 approval for `develop`, 2 for `main`
- All CI checks must pass before merge

### Code Review Checklist

- [ ] Architecture rules followed (no cross-module imports, domain purity)
- [ ] Tests cover the change (unit + integration where appropriate)
- [ ] No secrets or credentials in code
- [ ] Error handling is appropriate (no swallowed exceptions)
- [ ] Performance: no N+1 queries, no unnecessary re-renders
- [ ] Accessibility: WCAG AA for frontend changes
