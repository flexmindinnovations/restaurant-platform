# TODO — Restaurant Platform

> Last updated: 2026-06-18
> Phases match [phase-wise-development-prompts.md](guides/phase-wise-development-prompts.md)

---

## Phase 0 — Bootstrap (Sprint 0) ✅

### Phase 0A — Backend bootstrap ✅ `700f470` `223724e` `9e7e72d` `e61d8a0`
- [x] Python project setup (pyproject.toml, uv, Python 3.13)
- [x] FastAPI application factory (main.py, config.py, dependencies.py)
- [x] Shared kernel (entity, VOs, events, exceptions, database, redis, UoW, event bus, outbox)
- [x] Module scaffolding (11 bounded contexts)
- [x] Database setup (Alembic, multi-schema migrations, extensions)
- [x] Import boundary enforcement (.importlinter)
- [x] Health check endpoint (GET /health)
- [x] Test infrastructure (conftest, unit/integration/architecture/e2e dirs)
- [x] Dockerfiles (api + worker)
- [x] Celery setup (workers/celery_app.py)
- [x] Structured logging (structlog)
- [x] OpenTelemetry instrumentation

### Phase 0B — Infrastructure bootstrap ✅ `aaf65c8`
- [x] PostgreSQL init scripts (extensions, schemas, roles, RLS)
- [x] Docker Compose (PostgreSQL 17/PostGIS, Valkey 8, LocalStack, Mailpit)
- [x] Terraform modules (networking, compute, database, cache, storage, CDN, monitoring, security, CI/CD, DNS)
- [x] Environment configurations (dev, staging, production)
- [x] CI workflows (infrastructure-ci, security-scan)
- [x] Dependabot configuration

### Phase 0C — Code quality & remaining ✅ `8e5535b`
- [x] Pre-commit hooks (.pre-commit-config.yaml)
- [x] Git hooks (commit-msg validation, pre-commit ruff)
- [x] Release workflow (.github/workflows/release.yml)
- [x] Mobile state management (Riverpod + GoRouter in 3 apps)
- [x] Development setup guide (docs/guides/development-setup.md)
- [x] Coding standards guide (docs/guides/coding-standards.md)
- [x] PowerShell convenience scripts

---

## Phase 1 — Foundation: Identity & core domain (Sprint 1) ✅

### Identity module ✅ `6e3a536` `c355619` `520eeff` · 22 tests
- [x] Domain: Account entity, Email/Password/Phone/Role VOs, 5 domain events
- [x] Application: RegisterAccount, Login, VerifyEmail, ChangePassword, ForgotPassword, ResetPassword, RefreshToken, GetAccount
- [x] Application: Ports (AccountRepository, PasswordHasher, TokenService, EmailSender)
- [x] Application: AuthService (login, refresh, verify, logout)
- [x] Infrastructure: SQLAlchemy models + repository, JWT token service, bcrypt hasher, SMTP email sender
- [x] API: 8 auth routes under /api/v1/auth
- [x] Migration: identity.accounts, identity.refresh_tokens
- [x] Unit tests: domain + command handlers (22 tests)

### Users module ✅ `6e3a536` `c355619` · 7 tests
- [x] Domain: UserProfile aggregate root, ProfileCreated/ProfileUpdated events
- [x] Application: CreateProfile, UpdateProfile, GetProfile
- [x] Application: Ports (UserRepository)
- [x] Infrastructure: SQLAlchemy models + repository
- [x] API: Profile routes (GET /api/v1/me, PATCH /api/v1/me)
- [x] Event handler: AccountCreated → auto-create profile (subscribe_by_name)
- [x] Migration: users.profiles
- [x] Unit tests: domain + command handlers (7 tests)

### Restaurants module ✅ `6e3a536` `c355619` · 17 tests
- [x] Domain: Restaurant entity, Address VO, OperatingHours VO, 4 events
- [x] Application: RegisterRestaurant, UpdateRestaurant, VerifyRestaurant, GetRestaurant, ListRestaurants
- [x] Application: Ports (RestaurantRepository)
- [x] Infrastructure: SQLAlchemy models + repository (LIKE injection escaped)
- [x] API: 5 routes under /api/v1/restaurants + ownership checker
- [x] Migration: restaurants.restaurants
- [x] Unit tests: domain + command/query handlers (17 tests)

### Cross-cutting (Sprint 1) ✅
- [x] Auth middleware + RBAC (shared/api/security.py) — get_current_user, require_roles, require_restaurant_access
- [x] Event infrastructure — subscribe_by_name, AccountCreated → Users.CreateProfile
- [x] Architecture tests (import-linter) — test_import_boundaries.py
- [x] Integration test: full auth flow (register → verify → login → refresh → logout)

---

## Phase 2 — Core ordering: Menus, cart, checkout (Sprint 2) ✅ (backend only)

### Menus module (backend) ✅ `aa10742` · 41 tests
- [x] Domain: Menu + MenuItem aggregates, Category entity, Money VO, 7 events
- [x] Application: 9 commands + 4 queries, 3 ports
- [x] Infrastructure: 3 SQLAlchemy models (menus.*), repos with filtering
- [x] API: Full CRUD under /api/v1/menus (menus, categories, items)
- [x] Migration: 0003_menus_module with RLS on menu_items
- [x] Unit tests: 18 domain + 23 handler (41 total)
- [ ] Full-text search with pg_trgm + GIN index → see **Backlog** section
- [ ] ModifierGroup/Modifier entities → see **Backlog** section

### Orders module (backend) ✅ `42f02b8` · 31 tests
- [x] Domain: Order aggregate (OrderNumber, financial breakdown, state machine, per-status timestamps), Cart aggregate (single-restaurant constraint, item merging), 8 events
- [x] Application: 8 commands + 4 queries, MenuService anti-corruption layer
- [x] Infrastructure: 4 models (orders.*), Redis write-through cache (24h TTL)
- [x] API: Dual routers — /api/v1/checkout + /api/v1/orders with auth + RBAC
- [x] Event handler: DeliveryCompleted → auto-transition order to COMPLETED
- [x] Migration: 0004_orders_module with RLS
- [x] Unit tests: 17 domain + 14 commands (31 total)

### Angular frontend — menu & order management 🔲
- [ ] Restaurants page: list restaurants from API, detail view
- [ ] Menus page: CRUD for menus, categories, items within a restaurant
- [ ] Orders page: live order list with status filtering, order detail, status update actions
- [ ] NgRx Signal Store for state management in each feature
- [ ] api-client lib for typed HTTP calls
- [ ] Responsive tables with Angular Material

---

## Phase 3 — Payments & delivery (Sprint 3) ✅ (backend only)

### Payments module (backend) ✅ `42f02b8` · 4 tests
- [x] Domain: Payment + PaymentMethod entities, PaymentStatus enum, 6 events
- [x] Application: 6 commands (InitiatePayment, CapturePayment, RefundPayment, VoidPayment, AddPaymentMethod, RemovePaymentMethod) + 2 queries
- [x] Application: Ports (PaymentRepository, PaymentMethodRepository, PaymentGateway)
- [x] Infrastructure: MockGateway + StripeGateway stub, SQLAlchemy repos (payments.*)
- [x] API: Payment routes under /api/v1/payments
- [x] Event handlers: OrderPlaced → initiate payment, PaymentCompleted → confirm order
- [x] Unit tests: domain + command handlers (4 tests)

### Deliveries module (backend) ✅ `42f02b8` · 4 tests
- [x] Domain: Delivery + DeliveryPartner entities, GeoLocation/Location VOs, VehicleType, DeliveryStatus, 8 events
- [x] Application: 8 commands + 3 queries, LocationCache port
- [x] Infrastructure: PostGIS geography columns, ST_DWithin spatial queries, Redis location cache
- [x] API: Dual routers — /api/v1/delivery-assignments + /api/v1/partners
- [x] Event handlers: OrderConfirmed → create delivery + assign nearest partner
- [x] Migration: 0005_payments_deliveries with PostGIS + RLS
- [x] Unit tests: domain + command handlers (4 tests)

### WebSocket — live tracking ✅ `42f02b8`
- [x] WebSocket endpoint: /ws/orders/{order_id}/tracking
- [x] JWT auth via query parameter
- [x] Redis pub/sub for broadcasting
- [x] Location update throttling (5-second intervals)

### Notifications module — basic setup ✅ `42f02b8` · 0 tests
- [x] Domain: Notification entity, NotificationChannel enum (EMAIL, SMS, PUSH, IN_APP)
- [x] Application: SendNotification command, dispatcher + repository ports
- [x] Infrastructure: SMTP email dispatcher, SQLAlchemy models + repository
- [x] API: Notification routes under /api/v1/notifications
- [x] Event handlers: OrderPlaced/OrderConfirmed/DeliveryAssigned/DeliveryCompleted → auto-notify
- [ ] Unit tests → see **Backlog** section
- [ ] Celery async sending → see **Backlog** section
- [ ] SMS/push placeholders → see **Backlog** section

### Cross-module event wiring ✅
- [x] OrderPlaced → Payments.InitiatePayment, Notifications.SendOrderConfirmation
- [x] OrderConfirmed → Deliveries.CreateDelivery
- [x] PaymentCompleted → Orders.ConfirmOrder
- [x] DeliveryCompleted → Orders.CompleteOrder
- [x] DeliveryAssigned → Notifications.SendPartnerAssigned
- [x] OrderCancelled → Payments.VoidPayment (if AUTHORIZED/PENDING) or RefundPayment (if CAPTURED)

---

## Backlog — Remaining items from prior phases

### From Phase 2 (Menus) ✅
- [x] pg_trgm full-text search with GIN index on menu_items (migration 0006, GET /api/v1/menus/search)
- [x] ModifierGroup + Modifier entities (domain, infra, API, migration 0007, 9 domain tests)

### From Phase 3 (Notifications) 🟡
- [x] Unit tests for Notification domain + SendNotification handler (9 tests)
- [x] SMS and push notification dispatcher placeholders (SmsDispatcher, PushDispatcher, CompositeDispatcher)
- [ ] Celery tasks for async notification sending (currently synchronous)

---

## Phase 4 — Mobile apps & admin dashboard (Sprint 4) 🔲

### Shared Flutter packages (`mobile/packages/`) 🔲
- [ ] **networking/** — Dio HTTP client, auth interceptor (JWT auto-refresh), retry interceptor, logging interceptor
- [ ] **authentication/** — JWT token management (flutter_secure_storage), session state (Riverpod provider), login/register/logout flows
- [ ] **design_system/** — Color tokens, typography (Inter), spacing, common widgets (AppButton, AppTextField, AppCard, LoadingOverlay, ErrorView, EmptyState), light + dark theme
- [ ] **core/** — Environment config (dev/staging/prod), error models (AppException hierarchy), logger, common types (Paginated, Result, LatLng)
- [ ] **realtime/** — WebSocket client with auto-reconnect, event parsing (OrderStatusUpdate, LocationUpdate), Riverpod tracking provider
- [ ] **maps/** — Google Maps integration wrapper
- [ ] **localization/** — i18n setup
- [ ] **storage/** — Local storage abstraction

### Customer app (`mobile/apps/customer_app/`) 🔲
- [ ] Authentication: login, register, forgot password, biometric auth
- [ ] Home: restaurant discovery grid/list, search, filter by cuisine, sort by rating/distance
- [ ] Restaurant detail: info, operating hours, menu tabs by category
- [ ] Menu item detail: description, price, modifier selection, quantity, add to cart
- [ ] Cart: summary, edit quantities, delivery address, special instructions, order total breakdown
- [ ] Checkout: payment method selection, add new card (Stripe), order review, confirm & pay
- [ ] Order tracking: real-time status, map with delivery partner location, estimated time, partner info
- [ ] Order history: past orders, reorder button, detail view
- [ ] Profile: edit profile, manage addresses, manage payment methods, notification preferences
- [ ] Navigation: GoRouter with bottom nav (Home, Orders, Profile), auth guard
- [ ] State: Riverpod providers (auth, restaurants, menu, cart, orders, tracking)

### Restaurant app (`mobile/apps/restaurant_app/`) 🔲
- [ ] Authentication: login for owners/staff
- [ ] Dashboard: today's stats (order count, revenue, avg prep time), pending orders badge
- [ ] Order management: incoming orders (accept/reject), active orders (status updates), order detail, audio notifications
- [ ] Menu management: list menus, toggle availability, edit prices, add items with image upload
- [ ] Restaurant profile: edit business info, operating hours, delivery zones
- [ ] Analytics: basic charts (orders/day, revenue/day, popular items)
- [ ] Navigation: GoRouter with bottom nav (Dashboard, Orders, Menu, Profile)

### Delivery app (`mobile/apps/delivery_app/`) 🔲
- [ ] Authentication: login for delivery partners
- [ ] Home/availability: online/offline toggle, current status, earnings summary
- [ ] Assignment: incoming assignment card, accept/decline with 30s countdown
- [ ] Active delivery: step-by-step (navigate → pickup → navigate → deliver), Google Maps, proof of delivery photo
- [ ] Contact: call customer/restaurant buttons
- [ ] Delivery history + earnings: daily/weekly/monthly breakdown, payout history
- [ ] Profile: edit profile, vehicle info, documents
- [ ] Background: location updates every 10s on active delivery (geolocator)

### Angular admin dashboard enhancement (`frontend/`) 🔲
- [ ] **Dashboard**: KPI cards (orders today, revenue, active users, active restaurants), charts (orders over time, revenue over time)
- [ ] **Users management**: users table with search, filter by role, detail view, activate/deactivate, assign roles
- [ ] **Restaurants management**: restaurant table, approval queue (pending verification), detail, approve/reject
- [ ] **Orders management**: orders table with status filter + date range picker, order detail modal, manual status update
- [ ] **Deliveries**: active deliveries map view, delivery partner list with status, assignment override
- [ ] **Payments**: transaction log table with filters, refund action
- [ ] **Analytics**: revenue charts, order volume charts, popular restaurants, avg delivery time
- [ ] **Settings**: platform configuration (commission rates, delivery radius, etc.)
- [ ] Each page: NgRx Signal Store, @app/api-client, Angular Material, responsive layout
- [ ] Vitest unit tests for Signal Stores
- [ ] Playwright E2E for admin login → view orders → refund

### Mobile tests 🔲
- [ ] Widget tests for critical flows (login, restaurant list, cart, checkout)
- [ ] Integration test per app: launch → login → primary action

---

## Phase 5 — AI features & polish (Sprint 5) 🔲

### Reviews module (backend) 🔲
- [ ] Domain: Review entity (order_id, customer_id, restaurant_id, rating 1-5, comment, sentiment, is_flagged, reply, images)
- [ ] Domain: RestaurantReviewSummary (avg rating, distribution, themes)
- [ ] Business rules: one review per order, only after delivery, editable within 48h
- [ ] Application: SubmitReview, ReplyToReview, GetReviews, GetReviewSummary
- [ ] Infrastructure: SQLAlchemy models (reviews.*), repository
- [ ] API: POST /orders/{id}/reviews, GET /restaurants/{id}/reviews, POST /reviews/{id}/reply, GET /restaurants/{id}/reviews/summary
- [ ] Migration + unit tests

### Promotions module (backend) 🔲
- [ ] Domain: Promotion entity (code, type: PERCENTAGE/FIXED_AMOUNT/FREE_DELIVERY/BUY_X_GET_Y, value, min_order, max_discount, validity, usage limits)
- [ ] Domain: CouponUsage tracking
- [ ] Business rules: validate expiry, usage limits, min order amount, one coupon per order
- [ ] Application: CreatePromotion, ApplyPromotion, ValidatePromotion, ListPromotions
- [ ] Infrastructure: SQLAlchemy models (promotions.*), repository
- [ ] API: POST /promotions, GET /promotions/available, POST /checkout/apply-coupon, DELETE /checkout/remove-coupon
- [ ] Integrate coupon validation into PlaceOrder flow
- [ ] Migration + unit tests

### Analytics module (backend) 🔲
- [ ] Read-only module consuming events from all other modules
- [ ] Materialized views: daily order counts + revenue per restaurant, popular items, avg delivery time, customer retention, peak hours
- [ ] API: GET /analytics/restaurant/{id}/dashboard, GET /admin/analytics/platform, GET /admin/analytics/revenue
- [ ] Migration + unit tests

### AI services module (`ai/`) 🔲
- [ ] **Semantic menu search**: pgvector embeddings (OpenAI text-embedding-3-small), vector similarity search, fallback to pg_trgm
- [ ] **AI support assistant**: conversational support (GPT-4o/Claude via LangGraph), order context, refund ticket creation, guardrails, rate limited (20 msg/user/hr)
- [ ] **Smart recommendations**: personalized restaurant + menu item recs, hybrid collaborative + content-based filtering, cold-start fallback
- [ ] **Review sentiment analysis**: auto-analyze on submission, extract sentiment + themes, aggregate into restaurant summary

### Production hardening 🔲
- [ ] **Rate limiting**: auth endpoints 5 req/min/IP, API 100 req/min/user, Redis sliding window
- [ ] **Caching strategy**: restaurant list 5min, menu data 10min (invalidate on update), search 2min
- [ ] **Error handling audit**: consistent error format, no stack traces in prod, domain exception → HTTP status mapping
- [ ] **Security hardening**: RLS policy audit, parameterized queries audit, request payload size limits, security headers

### Comprehensive testing 🔲
- [ ] Backend: unit coverage >=80% on all domain layers
- [ ] Backend: integration tests for every API endpoint
- [ ] Backend: full E2E test (register → browse → order → pay → track → review)
- [ ] Backend: load test with locust or k6 (100 concurrent order placements)
- [ ] Frontend: Vitest coverage >=80% on Signal Stores
- [ ] Frontend: Playwright E2E (admin full flow)
- [ ] Mobile: widget tests for all critical screens
- [ ] Mobile: integration test per app (mocked API)
- [ ] Mobile: golden tests for key UI components

### Mobile app updates (Phase 5 additions) 🔲
- [ ] Customer app: review submission after delivery
- [ ] Customer app: coupon/promotion in cart/checkout
- [ ] Customer app: AI search on home screen
- [ ] Restaurant app: analytics charts on dashboard
- [ ] Restaurant app: review management (reply)

### Angular dashboard updates (Phase 5 additions) 🔲
- [ ] Reviews management page: admin moderation, flagged reviews queue
- [ ] Promotions management page: CRUD promotions, usage stats
- [ ] Notifications management page: view/manage notification templates

---

## Phase 6 — MVP release & production deployment (Sprint 6) 🔲

### Terraform — production environment 🔲
- [ ] Networking: VPC (3 AZs), public/private subnets, NAT gateway, VPC flow logs
- [ ] Compute: ECS Fargate (api 2-4 tasks, worker 1-2, beat 1), auto-scaling (CPU 70%/30%)
- [ ] Database: RDS PostgreSQL 17 (db.r6g.large, Multi-AZ, 100GB gp3, 35-day backups, PITR, encrypted)
- [ ] Cache: ElastiCache Valkey 8 (cache.r6g.large, 2 nodes, encrypted in transit + at rest)
- [ ] Storage: S3 buckets (assets + CloudFront, documents, backups → Glacier lifecycle)
- [ ] Security: WAF (rate limiting, SQLi, XSS), KMS, Secrets Manager
- [ ] DNS: Route 53, ACM certificate, A records for API + frontend

### CI/CD — production pipeline 🔲
- [ ] Release workflow: manual dispatch → CI checks → Docker build → ECR push → ECS rolling deploy → S3 + CloudFront invalidation → health checks → GitHub Release → Slack notify
- [ ] Rollback procedure: one-click ECS task definition rollback, Alembic downgrade scripts
- [ ] Blue/green or rolling update strategy documented

### Monitoring & alerting 🔲
- [ ] CloudWatch dashboards (platform overview, database, cache, delivery)
- [ ] P1 alarms: API 5xx >5%, database unreachable, ECS tasks = 0
- [ ] P2 alarms: API P95 >1s, Celery queue >100, cache hit rate <50%, disk >80%
- [ ] P3 alarms: 4xx spike, unused resources, certificate expiry <30d
- [ ] Distributed tracing: OpenTelemetry → AWS X-Ray, 10% sample rate in prod

### Operational runbooks 🔲
- [ ] incident-response.md — severity classification, escalation, communication template
- [ ] deployment.md — step-by-step deploy, rollback, smoke test checklist
- [ ] database-operations.md — migration procedure, backup/restore, failover, scaling
- [ ] scaling.md — ECS/RDS/ElastiCache scaling guide with cost implications
- [ ] common-issues.md — connection pool exhaustion, cache invalidation, gateway timeouts

### Documentation finalization 🔲
- [ ] docs/guides/deployment.md — full deployment guide with architecture diagram
- [ ] docs/api/ — OpenAPI docs served at /docs (auto-generated from FastAPI)
- [ ] docs/architecture/adr/ — ADRs for key decisions
- [ ] Update development-setup.md, root README.md

### Security checklist 🔲
- [ ] All secrets in AWS Secrets Manager (none in code)
- [ ] JWT signing key rotatable
- [ ] CORS restricted to production domains
- [ ] Rate limiting active on all public endpoints
- [ ] WAF rules active (SQLi, XSS, rate limiting)
- [ ] RLS policies verified on all tenant tables
- [ ] TLS on all external endpoints
- [ ] No debug mode in production
- [ ] Gitleaks passes on entire repo
- [ ] Dependency audit: no critical vulnerabilities
- [ ] Password reset tokens expire (1h)
- [ ] Account lockout after 5 failed attempts
- [ ] API payloads validated (Pydantic strict mode)

### Mobile release preparation 🔲
- [ ] Android: signed APK/AAB for all 3 apps
- [ ] iOS: archive builds (macOS + Xcode)
- [ ] App store metadata, screenshots, privacy policy
- [ ] Firebase for push notifications (FCM)
- [ ] Version 1.0.0 for all apps

### Final integration testing 🔲
- [ ] Customer E2E: register → browse → AI search → cart → coupon → checkout → pay → track → receive → review
- [ ] Restaurant E2E: login → dashboard → receive order → accept → prepare → mark ready → analytics
- [ ] Delivery E2E: login → go online → receive assignment → accept → pickup → deliver → earnings
- [ ] Admin E2E: login → dashboard → manage restaurants → orders → refund → analytics
- [ ] Load test: 100 concurrent users, P95 <500ms, 0 errors

---

## Commit log

| Hash | Message | Date | Phase |
|------|---------|------|-------|
| `42f02b8` | feat(backend): implement Orders, Payments, Deliveries, Notifications | 2026-06-18 | Phase 2–3 |
| `aa10742` | feat(menus): implement Menus module — Sprint 2 | 2026-06-18 | Phase 2 |
| `520eeff` | fix(backend): add missing domain events and migration columns | 2026-06-18 | Phase 1 |
| `c355619` | test(backend): add unit tests for Sprint 1 command/query handlers | 2026-06-18 | Phase 1 |
| `6e3a536` | feat: implement Phase 1 modules (identity, users, restaurants) | 2026-06-17 | Phase 1 |
| `8e5535b` | chore: complete Sprint 0C — hooks, mobile state, docs, scripts | 2026-06-17 | Phase 0C |
| `e61d8a0` | style: run ruff format on updated files | 2026-06-17 | Phase 0A |
| `9e7e72d` | refactor(docker): sync project packages in Dockerfiles | 2026-06-17 | Phase 0A |
| `223724e` | refactor(backend): register top-level editable packages | 2026-06-17 | Phase 0A |
| `700f470` | feat(backend): backend bootstrap + shared kernel + scaffolding | 2026-06-17 | Phase 0A |
| `bca8667` | feat(frontend): add shell layout with Material sidenav | 2026-06-17 | Phase 0B |
| `d3f11d5` | docs: update spec to reflect actual implementation | 2026-06-17 | Phase 0B |
| `aaf65c8` | chore: initial project scaffolding | 2026-06-17 | Phase 0B |

## Summary

| Phase | Backend | Frontend | Mobile | Status |
|-------|---------|----------|--------|--------|
| 0 — Bootstrap | ✅ Done | ✅ Shell | ✅ Scaffolding | ✅ Complete |
| 1 — Foundation | ✅ 3 modules, 46 tests | — | — | ✅ Complete |
| 2 — Ordering | ✅ 2 modules, 72 tests | 🔲 Not started | — | 🟡 Backend done |
| 3 — Payments/Delivery | ✅ 4 modules, 8 tests | — | — | 🟡 Backend done |
| 4 — Mobile/Dashboard | — | 🔲 Not started | 🔲 Not started | 🔲 Not started |
| 5 — AI/Polish | 🔲 3 modules + AI | 🔲 3 pages | 🔲 5 features | 🔲 Not started |
| 6 — MVP Release | — | — | — | 🔲 Not started |

**Total unit tests**: 167 (all passing)
**Backend modules complete**: 7/11 (Identity, Users, Restaurants, Menus, Orders, Payments, Deliveries) + Notifications (9 tests)
**Backend modules remaining**: 3 (Reviews, Promotions, Analytics) + AI Services
**Backlog remaining**: Celery async notifications
**Frontend pages done**: 0/11 (all placeholder routes)
**Mobile features done**: 0 (all stub packages)
