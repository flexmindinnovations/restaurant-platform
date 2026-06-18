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

#### Cross-Cutting (Sprint 1)

| Feature | Status | Notes |
|---------|--------|-------|
| AbstractUnitOfWork in shared.application.ports | ✅ Done | Clean architecture compliant |
| Transactional outbox in UoW commit | ✅ Done | Events → outbox → publish |
| Event bus subscribe_by_name (string-based) | ✅ Done | Avoids cross-module imports |
| Architecture tests (import-linter) | ✅ Done | test_import_boundaries.py |
| Integration test: Auth flow (register → verify → login → refresh → logout) | ✅ Done | Uses raw SQL, no cross-module imports |

---

## Phase 2 — Ordering & Menus (Sprint 2–3) 🟡

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

### Orders Module
- [ ] Domain: Order aggregate, OrderItem, OrderStatus
- [ ] Domain: Order lifecycle events
- [ ] Application: PlaceOrder, UpdateOrderStatus, CancelOrder
- [ ] Infrastructure: Repository, models
- [ ] API: Order routes

---

## Phase 3 — Payments & Delivery (Sprint 4–5) 🔲

### Payments Module
- [ ] Domain: Payment entity, PaymentStatus, PaymentMethod
- [ ] Application: ProcessPayment, RefundPayment
- [ ] Infrastructure: Payment gateway integration
- [ ] API: Payment routes

### Deliveries Module
- [ ] Domain: Delivery entity, DeliveryStatus, Location tracking
- [ ] Application: AssignDriver, UpdateDeliveryStatus
- [ ] Infrastructure: Repository, models
- [ ] API: Delivery routes + WebSocket tracking

---

## Phase 4 — Engagement & Analytics (Sprint 6–7) 🔲

### Notifications Module
- [ ] Domain: Notification entity, channels (email, push, SMS)
- [ ] Infrastructure: SES/SNS integration

### Reviews Module
- [ ] Domain: Review entity, rating aggregation
- [ ] Application: SubmitReview, ModerateReview

### Promotions Module
- [ ] Domain: Promotion entity, discount rules
- [ ] Application: CreatePromotion, ApplyPromotion

### Analytics Module
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
