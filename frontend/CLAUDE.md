# Frontend — Admin Dashboard

Angular 22 CLI workspace with path-mapped libraries.

## Commands
- `npm start` — Dev server (port 4200, proxies /api to localhost:8000)
- `npm run build` — Production build
- `npm test` — Run unit tests (Vitest via @angular/build:unit-test)
- `npm run lint` — ESLint with boundary rules
- `npm run e2e` — Playwright E2E tests
- `npm run format` — Prettier formatting

## Library Structure
Libraries live in `libs/` and are imported via `@app/*` tsconfig paths (not published packages).

### Dependency Rules (enforced by eslint-plugin-boundaries)
- **core** — Zero dependencies on other libs
- **design-system** — Can depend on: core
- **api-client** — Can depend on: core
- **shared** — Can depend on: core, design-system
- **feature libs** — Can depend on: core, shared, design-system, api-client
- **Feature libs cannot import from each other**

## Theming
- Angular Material M3 theme (SCSS in `src/styles.scss`)
- TailwindCSS v4 utilities (CSS in `src/tailwind.css`)
- Light/dark mode via `prefers-color-scheme` and `.dark`/`.light` class overrides
- Inter font loaded from Google Fonts
- WCAG AA compliant: focus-visible outlines, reduced-motion support, skip-to-content link

## Conventions
- OnPush change detection on all components
- SCSS for component styles (configured in angular.json schematics)
- Angular Signals + NgRx Signal Store for state
- Lazy-loaded feature routes
- Vitest for unit tests (native Angular 22 support)
- Playwright for E2E
