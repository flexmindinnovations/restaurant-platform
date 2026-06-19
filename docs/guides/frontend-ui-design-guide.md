# Frontend UI Design Guide — Restaurant Admin Platform

> Design system reference for all Angular dashboard UI work.
> Updated: 2026-06-18

## Design Philosophy

**Elevated Minimal** — inspired by Linear, Vercel, and Supabase dashboards.
Clean surfaces, subtle depth, information-dense layouts, and confident use of whitespace.

### Core Principles

1. **Surface hierarchy over decoration**: Use background layers (page → card → element) to create depth. No gradients or heavy shadows on containers.
2. **Data-first layout**: Numbers, statuses, and actions are the stars. Chrome (headers, borders, icons) should recede.
3. **Consistent color language**: One primary color (emerald) used sparingly for CTAs, active states, and positive indicators. Never competing hues.
4. **Tight, intentional spacing**: Dense layouts feel professional. Use 8px grid but favor the smaller end (8–16px gaps between related items, 24–32px between sections).
5. **Motion as feedback, not flair**: Transitions on hover/focus only (150–200ms). No entrance animations, no sliding panels.

## Color System

### Unified Palette

All UI surfaces use these CSS custom properties. Material components are themed to match.

| Token                    | Light              | Dark               | Usage                        |
|--------------------------|--------------------|--------------------|------------------------------|
| `--color-primary`        | `#16a34a`          | `#4ade80`          | CTAs, active nav, links      |
| `--color-primary-hover`  | `#15803d`          | `#22c55e`          | Hover state for primary      |
| `--color-primary-subtle` | `#f0fdf4`          | `rgba(34,197,94,0.1)` | Badges, tinted backgrounds |
| `--color-accent`         | `#8b5cf6`          | `#a78bfa`          | Secondary actions, charts    |
| `--color-surface-0`      | `#f8fafc`          | `#0a0a0a`          | Page background              |
| `--color-surface-1`      | `#ffffff`          | `#141414`          | Cards, panels                |
| `--color-surface-2`      | `#f1f5f9`          | `#1e1e1e`          | Nested elements, table heads |
| `--color-border`         | `#e2e8f0`          | `#262626`          | Card borders, dividers       |
| `--color-border-subtle`  | `#f1f5f9`          | `#1a1a1a`          | Inner dividers               |
| `--color-text-1`         | `#0f172a`          | `#fafafa`          | Primary text                 |
| `--color-text-2`         | `#475569`          | `#a1a1aa`          | Secondary text, labels       |
| `--color-text-3`         | `#94a3b8`          | `#52525b`          | Tertiary, timestamps         |

### Status Colors

| Status    | Color     | Badge BG (light)        | Usage                     |
|-----------|-----------|-------------------------|---------------------------|
| Success   | `#16a34a` | `#f0fdf4`              | Completed, verified, paid |
| Warning   | `#d97706` | `#fffbeb`              | Pending, processing       |
| Error     | `#dc2626` | `#fef2f2`              | Failed, cancelled         |
| Info      | `#2563eb` | `#eff6ff`              | Neutral info states       |

### Key Rule

Material M3 theme primary palette MUST match the CSS variable primary color. No competing hues (e.g., orange toolbar + green sidebar = bad).

## Typography

- **Font**: Inter (loaded from Google Fonts CDN)
- **Page title**: 24px / 600 weight
- **Section title**: 16px / 600 weight
- **Body**: 14px / 400 weight
- **Caption/label**: 12px / 500 weight, uppercase for table headers
- **Data values (KPIs)**: 28–32px / 700 weight, tabular-nums for alignment
- **Monospace**: JetBrains Mono or system monospace for IDs, codes, amounts

## Card Pattern

Cards are the primary content container. Use this structure:

```
┌─────────────────────────────────┐  ← 1px border (--color-border)
│  Title            [Action btn]  │  ← 16px padding, 14px semibold title
│─────────────────────────────────│  ← border-bottom divider
│                                 │
│  Content area                   │  ← 16px padding
│                                 │
└─────────────────────────────────┘
```

### Card Styling Rules

- Background: `--color-surface-1` (white in light mode)
- Border: `1px solid --color-border`
- Border-radius: `12px`
- Shadow: **none** in light mode (border provides definition), subtle shadow on hover only
- No glassmorphism in light mode — it's invisible on white. Reserve for dark mode accent cards.

## KPI Cards

Compact stat cards in a 4-column grid:

```
┌──────────────────┐
│ ↗ Label          │  ← 12px muted label + trend icon
│ 1,482            │  ← 28px bold value
│ +12.4% vs last   │  ← 12px colored trend text
└──────────────────┘
```

- Trend icon: small colored arrow (green up / red down)
- No large icons eating card space
- No chart canvases in KPI cards — use sparkline SVG or omit
- Grid: `grid-template-columns: repeat(4, 1fr)` with `minmax(200px, 1fr)` fallback

## Sidebar

- Width: 240px (not 280px — tighter is more modern)
- Background: `--color-surface-1`
- Logo area: simple text, no gradient background
- Nav items: 36px height, 8px border-radius, 12px horizontal padding
- Active state: primary-subtle background + primary text + 2px left accent bar
- Icons: 20px, muted by default, primary when active
- Dividers: 1px `--color-border-subtle` with 16px vertical margin

## Toolbar

- Height: 48px (not 64px — less chrome, more content)
- Background: `--color-surface-1` (not colored gradient)
- Border-bottom: 1px solid `--color-border`
- Content: breadcrumb or page context on left, actions on right
- No heavy colored toolbar — modern dashboards use neutral top bars

## Tables

- Header: `--color-surface-2` background, 12px uppercase labels, 500 weight
- Rows: 48px height, hover `--color-surface-2`
- Borders: horizontal only (`--color-border-subtle`)
- Cell padding: 12px 16px
- Status badges: pill-shaped, colored bg + text, no border

## Responsive Breakpoints

| Breakpoint | Sidebar      | KPI Grid    | Table           |
|------------|-------------|-------------|-----------------|
| > 1280px   | 240px fixed | 4 columns   | Full columns    |
| 768–1280px | Collapsed   | 2 columns   | Hide low-prio   |
| < 768px    | Hidden      | 1 column    | Card layout     |

## Do / Don't

| Do | Don't |
|----|-------|
| Use borders for card definition in light mode | Use glassmorphism on white backgrounds |
| Keep toolbar neutral/white | Use colored toolbar gradients |
| 4 KPIs per row on desktop | 2 KPIs per row (wastes space) |
| Monospace for data values | Variable-width font for numbers |
| Subtle hover transitions (150ms) | Entrance animations, transform effects |
| Dense 8px-grid spacing | Excessive padding (24px+ everywhere) |
| One primary color throughout | Multiple competing accent colors |
