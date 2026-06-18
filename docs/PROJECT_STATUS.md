# Project Status — Restaurant Platform

> Last updated: 2026-06-18

## Phase 1 — Core Foundation (Sprints 0–1)

### Sprint 0: Infrastructure & Scaffolding ✅

| Area | Status | Notes |
|------|--------|-------|
| Monorepo setup (uv, Angular CLI, Melos) | ✅ Done | |
| Docker Compose (Postgres, Valkey, LocalStack, Mailpit) | ✅ Done | Pinned versions |
| Terraform modules (networking, compute, database, cache, CDN, storage, security, monitoring, CI/CD) | ✅ Done | Security hardened |
| Backend FastAPI factory + config | ✅ Done | |
| Shared kernel (domain primitives, UoW, event bus, outbox) | ✅ Done | |
| Frontend Angular shell + sidenav | ✅ Done | |
| Module scaffolding (12 bounded contexts) | ✅ Done | |
| DB init scripts (extensions, schemas, roles, RLS) | ✅ Done | |
| Alembic migrations setup | ✅ Done | |

### Sprint 1: Identity, Users, Restaurants — Backend ✅

#### Identity Module

| Feature | Status | Notes |
|---------|--------|-------|
| Domain: Account entity, Email/Password/Phone/Role VOs | ✅ Done | |
| Domain: Account events (Created, Verified, Deactivated, PasswordChanged, RoleAssigned) | ✅ Done | |
| Application: RegisterAccount command | ✅ Done | |
| Application: Login command | ✅ Done | Email verification enforced |
| Application: VerifyEmail command | ✅ Done | |
| Application: ChangePassword command | ✅ Done | |
| Application: ForgotPassword command | ✅ Done | 1h token expiry |
| Application: ResetPassword command | ✅ Done | Separate reset_token field |
| Application: RefreshToken command | ✅ Done | Token rotation |
| Application: AuthService (login, refresh, verify, logout) | ✅ Done | |
| Application: GetAccount query | ✅ Done | |
| Application: Ports (AccountRepository, PasswordHasher, TokenService, EmailSender) | ✅ Done | |
| Infrastructure: SQLAlchemy models + repository | ✅ Done | |
| Infrastructure: JWT token service | ✅ Done | |
| Infrastructure: Bcrypt password hasher | ✅ Done | |
| API: Auth routes (register, login, logout, refresh, verify, forgot/reset password, me) | ✅ Done | |
| Unit tests: Domain entities & value objects | ✅ Done | |
| Unit tests: Command handler logic | ✅ Done | Mocked ports |

#### Users Module

| Feature | Status | Notes |
|---------|--------|-------|
| Domain: UserProfile entity (AggregateRoot) | ✅ Done | |
| Application: CreateProfile command | ✅ Done | |
| Application: UpdateProfile command | ✅ Done | |
| Application: GetProfile query | ✅ Done | |
| Application: Ports (UserRepository) | ✅ Done | |
| Infrastructure: SQLAlchemy models + repository | ✅ Done | |
| API: Profile routes (get, update) | ✅ Done | |
| Event handler: AccountCreated → auto-create profile | ✅ Done | Decoupled via subscribe_by_name |
| Unit tests: Domain entities | ✅ Done | |
| Unit tests: Command handler logic | ✅ Done | Mocked ports |

#### Restaurants Module

| Feature | Status | Notes |
|---------|--------|-------|
| Domain: Restaurant entity, Address VO (shared), OperatingHours VO | ✅ Done | |
| Domain: Restaurant events (Registered, Updated, Verified, Deactivated) | ✅ Done | |
| Application: RegisterRestaurant command | ✅ Done | |
| Application: UpdateRestaurant command | ✅ Done | Partial update support |
| Application: VerifyRestaurant command | ✅ Done | |
| Application: GetRestaurant query | ✅ Done | |
| Application: ListRestaurants query | ✅ Done | Pagination + search |
| Application: Ports (RestaurantRepository) | ✅ Done | |
| Infrastructure: SQLAlchemy models + repository | ✅ Done | LIKE injection escaped |
| API: Restaurant routes (register, get, list, update, verify) | ✅ Done | |
| Ownership checker callback | ✅ Done | Registered from restaurants.startup |
| Unit tests: Domain entities & value objects | ✅ Done | |
| Unit tests: Command/query handler logic | ✅ Done | Mocked ports |

#### Cross-Cutting (Sprint 1+)

| Feature | Status | Notes |
|---------|--------|-------|
| AbstractUnitOfWork in shared.application.ports | ✅ Done | Clean architecture compliant |
| Transactional outbox in UoW commit | ✅ Done | Events → outbox → publish |
| Event bus subscribe_by_name (string-based) | ✅ Done | Avoids cross-module imports |
| Architecture tests (import-linter) | ✅ Done | test_import_boundaries.py |
| Integration test: Auth flow (register → verify → login → refresh → logout) | ✅ Done | Uses raw SQL, no cross-module imports |
| Shared API security (JWT auth, RBAC, tenant access) | ✅ Done | shared/api/security.py |
| WebSocket infrastructure (Redis pub/sub, throttled tracking) | ✅ Done | shared/api/websockets.py |
| Cross-module adapter pattern (app/adapters/) | ✅ Done | MenuServiceAdapter bridges menus→orders |

---

## Phase 2 — Ordering & Menus (Sprint 2–3) ✅

### Menus Module ✅
- [x] Domain: Menu aggregate root, MenuItem aggregate root, Category entity
- [x] Domain: Price via shared Money VO, availability rules (is_available, publish/unpublish)
- [x] Domain: Events (MenuCreated, MenuUpdated, MenuPublished, MenuUnpublished, MenuItemCreated, MenuItemUpdated, MenuItemRemoved)
- [x] Application: Commands (CreateMenu, UpdateMenu, DeleteMenu, AddCategory, UpdateCategory, DeleteCategory, CreateMenuItem, UpdateMenuItem, DeleteMenuItem)
- [x] Application: Queries (GetMenu with categories, ListMenus, GetMenuItem, ListMenuItems)
- [x] Application: Ports (MenuRepository, CategoryRepository, MenuItemRepository)
- [x] Infrastructure: SQLAlchemy models (MenuModel, CategoryModel, MenuItemModel) with schema menus.*
- [x] Infrastructure: Repository implementations with CRUD and filtering
- [x] API: Full CRUD routes (menus, categories, items) under /api/v1/menus
- [x] API: Pydantic request/response schemas with validation
- [x] Migration: 0003_menus_module (menus, categories, menu_items tables + RLS on menu_items)
- [x] Unit tests: 18 domain tests + 23 handler tests (41 total)

### Orders Module ✅
- [x] Domain: Order aggregate (OrderNumber, Money breakdown with subtotal/tax/delivery_fee/tip, state machine transitions, per-status timestamps, cancellation rules), OrderItem, OrderStatus
- [x] Domain: Cart aggregate (single-restaurant constraint, item merging, quantity management)
- [x] Domain: Order lifecycle events (OrderPlaced, OrderConfirmed, OrderPreparing, OrderReady, OrderOutForDelivery, OrderDelivered, OrderCompleted, OrderCancelled)
- [x] Application: Commands (AddToCart, UpdateCartItem, RemoveFromCart, ClearCart, PlaceOrder, ConfirmOrder, UpdateOrderStatus, CancelOrder) and Queries (GetCart, GetOrder, ListCustomerOrders, ListRestaurantOrders)
- [x] Application: MenuService anti-corruption layer (port + adapter in app/adapters/) to validate menu items without cross-module imports
- [x] Infrastructure: SQLAlchemy models (CartModel, CartItemModel, OrderModel, OrderItemModel) with schema orders.*, write-through Valkey (Redis) caching layer (24h TTL)
- [x] API: Dual routers — Checkout (/api/v1/checkout/) and Orders (/api/v1/orders/) with auth + RBAC
- [x] Event handlers: DeliveryCompleted → auto-transition order to COMPLETED
- [x] Migration: 0004_orders_module (carts, cart_items, orders, order_items tables + RLS)
- [x] Unit tests: 31 tests covering domain invariants (17) and command handlers (14) — 100% green

---

## Phase 3 — Payments & Delivery (Sprint 4–5) ✅

### Payments Module ✅
- [x] Domain: Payment entity (AggregateRoot), PaymentMethod entity, PaymentStatus enum, payment events (Initiated, Completed, Failed, Refunded, MethodAdded, MethodRemoved)
- [x] Application: Commands (InitiatePayment, CapturePayment, RefundPayment, AddPaymentMethod, RemovePaymentMethod, SetDefaultPaymentMethod) and Queries (GetPayment, ListPaymentMethods)
- [x] Application: Ports (PaymentRepository, PaymentMethodRepository, PaymentGateway)
- [x] Infrastructure: SQLAlchemy models (PaymentModel, PaymentMethodModel) with schema payments.*, repository implementations
- [x] Infrastructure: PaymentGateway implementations (MockGateway for dev, StripeGateway stub for prod)
- [x] API: Payment routes (/api/v1/payments/) with full CRUD
- [x] Event handlers: OrderPlaced → auto-initiate payment, PaymentCompleted → confirm order
- [x] Unit tests: 4 tests covering domain and command handlers (100% green)

### Deliveries Module ✅
- [x] Domain: Delivery entity (AggregateRoot), DeliveryPartner entity, DeliveryStatus enum, Location/GeoLocation VOs, VehicleType enum
- [x] Domain: Delivery events (Created, Assigned, PickedUp, InTransit, Completed, Failed, PartnerRegistered, PartnerLocationUpdated)
- [x] Application: Commands (CreateDelivery, AssignPartner, AcceptAssignment, UpdateDeliveryStatus, RegisterPartner, TogglePartnerAvailability, TogglePartnerOnline, UpdatePartnerLocation) and Queries (GetDelivery, GetPartner, ListPartnerDeliveries)
- [x] Application: Ports (DeliveryRepository, PartnerRepository, LocationCache)
- [x] Infrastructure: SQLAlchemy models with PostGIS geography columns for location tracking, Redis-backed LocationCache
- [x] Infrastructure: Repository implementations with ST_GeogFromText/ST_DWithin spatial queries
- [x] API: Dual routers — delivery assignments (/api/v1/delivery-assignments/) and partners (/api/v1/partners/)
- [x] API: WebSocket endpoint (/ws/orders/{id}/tracking) for real-time delivery tracking with Redis pub/sub and location throttling
- [x] Event handlers: OrderConfirmed → auto-create delivery and assign nearest partner
- [x] Migration: 0005_payments_deliveries (payments.*, deliveries.* tables with PostGIS + RLS)
- [x] Unit tests: 4 tests covering domain and command handlers (100% green)

---

## Phase 4 — Engagement & Analytics (Sprint 6–7) 🟡

### Notifications Module ✅
- [x] Domain: Notification entity (AggregateRoot), NotificationChannel enum (EMAIL, SMS, PUSH, IN_APP)
- [x] Application: SendNotification command, ports (NotificationDispatcher, NotificationRepository)
- [x] Infrastructure: SMTP email dispatcher, SQLAlchemy models + repository
- [x] API: Notification routes (/api/v1/notifications/)
- [x] Event handlers: OrderPlaced/OrderConfirmed/DeliveryAssigned/DeliveryCompleted → auto-send notifications
- [ ] Unit tests: Not yet written

### Reviews Module 🔲
- [ ] Domain: Review entity, rating aggregation
- [ ] Application: SubmitReview, ModerateReview

### Promotions Module 🔲
- [ ] Domain: Promotion entity, discount rules
- [ ] Application: CreatePromotion, ApplyPromotion

### Analytics Module 🔲
- [ ] Domain: Event aggregation models
- [ ] Infrastructure: Analytics pipeline

---

## Phase 5 — AI Services (Sprint 8) 🔲

### AI Module
- [ ] Recommendation engine
- [ ] Demand forecasting
- [ ] Smart search / NLP

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Complete |
| 🔲 | Not started |
| 🟡 | In progress |
