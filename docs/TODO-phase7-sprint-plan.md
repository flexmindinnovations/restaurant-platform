# Sprint Plan — Phase 7-10 Feature Expansion

> **Last updated**: 2026-06-21
> **Status**: Planning
> **Reference**: [REQUIREMENTS-PHASE-NEXT.md](REQUIREMENTS-PHASE-NEXT.md)
> **Architecture**: Clean Architecture (Domain → Application → Infrastructure → API)
> **Conventions**: schema-per-module, RLS with `restaurant_id`, cross-schema by UUID only, transactional outbox for events

---

## Table of Contents

- [Phase 7 — Dine-in Operations](#phase-7--dine-in-operations-sprints-7-8)
  - [EPIC-7A: Table Management & Reservations](#epic-7a-table-management--reservations)
  - [EPIC-7B: Kitchen Display System (KDS)](#epic-7b-kitchen-display-system-kds)
  - [EPIC-7C: Parcel / Takeaway Orders](#epic-7c-parcel--takeaway-orders)
  - [EPIC-7D: Invoicing & Receipt Printing](#epic-7d-invoicing--receipt-printing)
- [Phase 8 — Cost Control & Staffing](#phase-8--cost-control--staffing-sprints-9-10)
  - [EPIC-8A: Inventory & Stock Management](#epic-8a-inventory--stock-management)
  - [EPIC-8B: Supplier & Vendor Management](#epic-8b-supplier--vendor-management)
  - [EPIC-8C: Staff & Workforce Management](#epic-8c-staff--workforce-management)
  - [EPIC-8D: Menu Engineering & Food Cost Analysis](#epic-8d-menu-engineering--food-cost-analysis)
- [Phase 9 — Customer Experience](#phase-9--customer-experience--engagement-sprints-11-12)
  - [EPIC-9A: QR Code Ordering](#epic-9a-qr-code-ordering)
  - [EPIC-9B: Bill Splitting](#epic-9b-bill-splitting)
  - [EPIC-9C: Customer Loyalty & CRM](#epic-9c-customer-loyalty--crm)
- [Phase 10 — Enterprise & Scale](#phase-10--enterprise--scale-sprints-13-14)
  - [EPIC-10A: Third-Party Integrations](#epic-10a-third-party-integrations)
  - [EPIC-10B: Multi-Location / Franchise](#epic-10b-multi-location--franchise-management)
  - [EPIC-10C: Waste Management](#epic-10c-waste-management--tracking)
  - [EPIC-10D: Compliance & Food Safety](#epic-10d-compliance--food-safety)

---

# Phase 7 — Dine-in Operations (Sprints 7-8)

**Goal**: Enable complete dine-in restaurant operations — table management, kitchen coordination, takeaway, and billing.
**Duration**: 6-8 weeks (4 sprints × 2 weeks)
**New Bounded Contexts**: `TableManagement`, `Kitchen`, `Invoicing`

---

## EPIC-7A: Table Management & Reservations

| Field | Value |
|-------|-------|
| **Epic ID** | EPIC-7A |
| **Priority** | P0 — Must Have |
| **Bounded Context** | NEW — `TableManagement` (schema: `tables`) |
| **Depends On** | Orders (order-table linking), Restaurants (restaurant context) |
| **Estimate** | 2 sprints (4 weeks) |
| **Competitors** | TouchBistro Reservations, Toast Tables, Square Table Management, OpenTable (Lightspeed), Restroworks Floor Management |

### Description

A complete dine-in operations module covering floor plan management, table status tracking, reservation/booking, waitlist management, and linking orders to specific tables and seats. Essential for any restaurant platform supporting dine-in service.

### User Stories

| ID | Role | Story | Acceptance Criteria |
|----|------|-------|-------------------|
| US-7A.1 | Restaurant Owner | I want to design my floor plan with tables of different sizes and shapes so I can visually manage my dining area | Floor plan editor renders tables by shape/position; tables draggable; changes persist on save |
| US-7A.2 | Customer | I want to reserve a table for a specific date, time, and party size so I have a guaranteed seat | Available time slots shown for party size; reservation created with PENDING status; confirmation email/SMS sent |
| US-7A.3 | Host / Staff | I want to see real-time table status (available, occupied, reserved, cleaning) so I can seat guests efficiently | Floor plan shows color-coded statuses; updates via WebSocket within 2s of status change |
| US-7A.4 | Server | I want to associate an order with a specific table and seat number so food is delivered correctly | Order creation accepts `table_id` + `seat_number`; multiple orders per table supported |
| US-7A.5 | Customer | I want to join a digital waitlist when the restaurant is full so I get notified when my table is ready | Waitlist entry created with estimated wait time; push notification sent when table becomes available |
| US-7A.6 | Restaurant Manager | I want to see reservation analytics (no-show rate, peak hours, avg turn time) so I can optimize seating | Dashboard shows occupancy heatmap, no-show %, avg turn time per table/section |

### Database Schema

#### `tables.sections`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Section identifier |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | Tenant key |
| `name` | `VARCHAR(100)` | NOT NULL | Section name (e.g., "Main Hall", "Patio", "Private Room") |
| `description` | `TEXT` | NULLABLE | Optional description |
| `display_order` | `INTEGER` | NOT NULL, default `0` | Sort order |
| `is_active` | `BOOLEAN` | NOT NULL, default `true` | Soft delete |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

**Indexes**: `ix_tables_sections_restaurant_id (restaurant_id)`
**RLS**: `enable_tenant_rls('tables', 'sections', 'restaurant_id')`

#### `tables.tables`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Table identifier |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | Tenant key |
| `section_id` | `UUID` | FK → `tables.sections(id)` ON DELETE SET NULL, NULLABLE | Section assignment |
| `number` | `VARCHAR(20)` | NOT NULL | Table number/label (e.g., "T1", "A12") |
| `capacity_min` | `INTEGER` | NOT NULL, default `1`, CHECK `>= 1` | Minimum guests |
| `capacity_max` | `INTEGER` | NOT NULL, CHECK `>= capacity_min` | Maximum guests |
| `shape` | `VARCHAR(20)` | NOT NULL, default `'SQUARE'` | Enum: `ROUND`, `SQUARE`, `RECTANGULAR`, `BOOTH`, `BAR_SEAT` |
| `position_x` | `INTEGER` | NOT NULL, default `0` | X coordinate on floor plan grid |
| `position_y` | `INTEGER` | NOT NULL, default `0` | Y coordinate on floor plan grid |
| `status` | `VARCHAR(20)` | NOT NULL, default `'AVAILABLE'` | Enum: `AVAILABLE`, `OCCUPIED`, `RESERVED`, `CLEANING`, `BLOCKED` |
| `turn_time_minutes` | `INTEGER` | NOT NULL, default `90` | Expected avg time a party occupies the table |
| `buffer_minutes` | `INTEGER` | NOT NULL, default `15` | Cleaning/reset buffer between seatings |
| `is_active` | `BOOLEAN` | NOT NULL, default `true` | Soft delete |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

**Indexes**: `ix_tables_tables_restaurant_id (restaurant_id)`, `ix_tables_tables_section_id (section_id)`
**Unique**: `uq_tables_restaurant_number (restaurant_id, number)`
**RLS**: `enable_tenant_rls('tables', 'tables', 'restaurant_id')`

#### `tables.reservations`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Reservation identifier |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | Tenant key |
| `table_id` | `UUID` | FK → `tables.tables(id)` ON DELETE CASCADE, NULLABLE | Assigned table (null until confirmed) |
| `customer_id` | `UUID` | NULLABLE, INDEX | Reference to identity.accounts (cross-schema UUID) |
| `customer_name` | `VARCHAR(255)` | NOT NULL | Guest name (for walk-in or non-registered) |
| `customer_phone` | `VARCHAR(20)` | NULLABLE | Contact phone |
| `customer_email` | `VARCHAR(255)` | NULLABLE | Contact email |
| `date` | `DATE` | NOT NULL, INDEX | Reservation date |
| `start_time` | `TIME` | NOT NULL | Start time |
| `end_time` | `TIME` | NOT NULL | End time (computed from start_time + turn_time) |
| `party_size` | `INTEGER` | NOT NULL, CHECK `>= 1` | Number of guests |
| `status` | `VARCHAR(20)` | NOT NULL, default `'PENDING'` | Enum: `PENDING`, `CONFIRMED`, `SEATED`, `COMPLETED`, `NO_SHOW`, `CANCELLED` |
| `special_requests` | `TEXT` | NULLABLE | Guest notes (allergies, preferences, occasion) |
| `internal_notes` | `TEXT` | NULLABLE | Staff-only notes |
| `hold_until` | `TIMESTAMPTZ` | NULLABLE | Auto-release time for no-show (start_time + hold_minutes) |
| `seated_at` | `TIMESTAMPTZ` | NULLABLE | Actual seating timestamp |
| `completed_at` | `TIMESTAMPTZ` | NULLABLE | Checkout timestamp |
| `cancelled_at` | `TIMESTAMPTZ` | NULLABLE | Cancellation timestamp |
| `cancellation_reason` | `TEXT` | NULLABLE | Why cancelled |
| `source` | `VARCHAR(20)` | NOT NULL, default `'PLATFORM'` | Enum: `PLATFORM`, `PHONE`, `WALK_IN`, `THIRD_PARTY` |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

**Indexes**: `ix_tables_reservations_restaurant_id (restaurant_id)`, `ix_tables_reservations_date (restaurant_id, date)`, `ix_tables_reservations_customer_id (customer_id)`, `ix_tables_reservations_table_id (table_id)`
**RLS**: `enable_tenant_rls('tables', 'reservations', 'restaurant_id')`

#### `tables.waitlist_entries`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Waitlist entry identifier |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | Tenant key |
| `customer_name` | `VARCHAR(255)` | NOT NULL | Guest name |
| `customer_phone` | `VARCHAR(20)` | NOT NULL | Contact phone (for notification) |
| `customer_id` | `UUID` | NULLABLE | Registered customer reference |
| `party_size` | `INTEGER` | NOT NULL, CHECK `>= 1` | Number of guests |
| `estimated_wait_minutes` | `INTEGER` | NOT NULL | Calculated estimated wait |
| `queue_position` | `INTEGER` | NOT NULL | Position in queue |
| `status` | `VARCHAR(20)` | NOT NULL, default `'WAITING'` | Enum: `WAITING`, `NOTIFIED`, `SEATED`, `LEFT`, `CANCELLED` |
| `preferred_section` | `UUID` | FK → `tables.sections(id)`, NULLABLE | Optional section preference |
| `special_requests` | `TEXT` | NULLABLE | Notes |
| `notified_at` | `TIMESTAMPTZ` | NULLABLE | When SMS/push notification was sent |
| `seated_at` | `TIMESTAMPTZ` | NULLABLE | When seated |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

**Indexes**: `ix_tables_waitlist_restaurant_id (restaurant_id)`, `ix_tables_waitlist_status (restaurant_id, status)`
**RLS**: `enable_tenant_rls('tables', 'waitlist_entries', 'restaurant_id')`

### Domain Events

| Event | Trigger | Payload | Consumers |
|-------|---------|---------|-----------|
| `TableStatusChanged` | Table status updated | `table_id`, `restaurant_id`, `old_status`, `new_status`, `changed_by` | WebSocket broadcaster, Analytics |
| `ReservationCreated` | New reservation | `reservation_id`, `restaurant_id`, `customer_name`, `date`, `time`, `party_size` | Notifications (confirmation SMS/email) |
| `ReservationConfirmed` | Staff confirms reservation | `reservation_id`, `table_id` | Notifications (confirmation to customer) |
| `ReservationCancelled` | Customer/staff cancels | `reservation_id`, `reason`, `cancelled_by` | Analytics (cancellation tracking) |
| `GuestSeated` | Reservation → SEATED | `reservation_id`, `table_id`, `seated_at` | Orders (enable table ordering) |
| `GuestNoShow` | Hold time expired | `reservation_id`, `table_id` | Analytics, Notifications |
| `WaitlistJoined` | Customer joins waitlist | `waitlist_id`, `restaurant_id`, `party_size`, `estimated_wait` | — |
| `WaitlistNotified` | Table available, customer notified | `waitlist_id`, `customer_phone` | Notifications (SMS/push) |

### API Endpoints

| Method | Path | Description | Auth | Request Body | Response |
|--------|------|-------------|------|-------------|----------|
| `POST` | `/api/v1/tables/sections` | Create section | Staff+ | `{ name, description?, display_order? }` | `201 SectionResponse` |
| `GET` | `/api/v1/tables/sections` | List sections | Staff+ | — | `200 { data: { items: SectionResponse[], total } }` |
| `PATCH` | `/api/v1/tables/sections/{id}` | Update section | Staff+ | `{ name?, description?, display_order? }` | `200 SectionResponse` |
| `DELETE` | `/api/v1/tables/sections/{id}` | Delete section | Manager+ | — | `204` |
| `POST` | `/api/v1/tables` | Create table | Manager+ | `{ number, section_id?, capacity_min, capacity_max, shape, position_x, position_y }` | `201 TableResponse` |
| `GET` | `/api/v1/tables` | List tables (floor plan) | Staff+ | Query: `restaurant_id`, `section_id?`, `status?` | `200 { data: { items: TableResponse[], total } }` |
| `PATCH` | `/api/v1/tables/{id}` | Update table | Manager+ | `{ number?, capacity_min?, capacity_max?, shape?, position_x?, position_y?, turn_time_minutes?, buffer_minutes? }` | `200 TableResponse` |
| `PATCH` | `/api/v1/tables/{id}/status` | Update table status | Staff+ | `{ status }` | `200 TableResponse` |
| `DELETE` | `/api/v1/tables/{id}` | Delete table | Manager+ | — | `204` |
| `POST` | `/api/v1/reservations` | Create reservation | Customer/Staff | `{ restaurant_id, date, start_time, party_size, customer_name, customer_phone?, customer_email?, special_requests?, table_id? }` | `201 ReservationResponse` |
| `GET` | `/api/v1/reservations` | List reservations | Staff+ | Query: `restaurant_id`, `date?`, `status?`, `customer_id?` | `200 { data: { items: ReservationResponse[], total } }` |
| `GET` | `/api/v1/reservations/{id}` | Get reservation | Staff/Owner | — | `200 ReservationResponse` |
| `PATCH` | `/api/v1/reservations/{id}` | Update reservation | Staff+ | `{ date?, start_time?, party_size?, table_id?, special_requests? }` | `200 ReservationResponse` |
| `POST` | `/api/v1/reservations/{id}/confirm` | Confirm reservation | Staff+ | `{ table_id }` | `200 ReservationResponse` |
| `POST` | `/api/v1/reservations/{id}/seat` | Mark as seated | Staff+ | — | `200 ReservationResponse` |
| `POST` | `/api/v1/reservations/{id}/cancel` | Cancel reservation | Customer/Staff | `{ reason? }` | `200 ReservationResponse` |
| `POST` | `/api/v1/reservations/{id}/no-show` | Mark no-show | Staff+ | — | `200 ReservationResponse` |
| `GET` | `/api/v1/tables/availability` | Get available time slots | Public | Query: `restaurant_id`, `date`, `party_size` | `200 { slots: [{ start_time, end_time, table_id }] }` |
| `POST` | `/api/v1/waitlist` | Join waitlist | Customer/Staff | `{ restaurant_id, customer_name, customer_phone, party_size, preferred_section? }` | `201 WaitlistResponse` |
| `GET` | `/api/v1/waitlist` | Get waitlist | Staff+ | Query: `restaurant_id`, `status?` | `200 { data: { items: WaitlistResponse[], total } }` |
| `POST` | `/api/v1/waitlist/{id}/notify` | Notify waitlist customer | Staff+ | — | `200 WaitlistResponse` |
| `POST` | `/api/v1/waitlist/{id}/seat` | Seat from waitlist | Staff+ | `{ table_id }` | `200 WaitlistResponse` |
| `DELETE` | `/api/v1/waitlist/{id}` | Remove from waitlist | Staff+ | — | `204` |

**WebSocket**: `ws://{host}/ws/tables/{restaurant_id}` — broadcasts `TableStatusChanged` events to connected clients.

### Implementation Tasks

#### Backend

- [x] **TASK-7A.01**: Create module scaffold `backend/src/modules/tables/` with domain, application, infrastructure, api layers
- [x] **TASK-7A.02**: Implement domain entities — `Table`, `Section`, `Reservation`, `WaitlistEntry`
- [x] **TASK-7A.03**: Implement value objects — `TableStatus`, `ReservationStatus`, `TableShape`, `WaitlistStatus`, `ReservationSource`
- [x] **TASK-7A.04**: Implement domain events — all 8 events listed above
- [x] **TASK-7A.05**: Implement `TimeSlotAvailabilityService` — find tables matching party_size, check against existing reservations, apply turn_time + buffer
- [x] **TASK-7A.06**: Implement application commands — `CreateTable`, `UpdateTable`, `DeleteTable`, `UpdateTableStatus`
- [x] **TASK-7A.07**: Implement application commands — `CreateSection`, `UpdateSection`, `DeleteSection`
- [x] **TASK-7A.08**: Implement application commands — `CreateReservation`, `ConfirmReservation`, `CancelReservation`, `SeatReservation`, `MarkNoShow`
- [x] **TASK-7A.09**: Implement application commands — `JoinWaitlist`, `NotifyWaitlistCustomer`, `SeatFromWaitlist`, `RemoveFromWaitlist`
- [x] **TASK-7A.10**: Implement application queries — `GetFloorPlan`, `GetTablesBySection`, `GetAvailableTimeSlots`, `GetReservationsByDate`, `GetWaitlist`
- [x] **TASK-7A.11**: Implement repository ports — `TableRepository`, `SectionRepository`, `ReservationRepository`, `WaitlistRepository`
- [x] **TASK-7A.12**: Implement event handlers — TableStatusChanged → Redis pub/sub broadcast
- [x] **TASK-7A.13**: Alembic migration — `tables` schema with all 4 tables, indexes, constraints, RLS
- [x] **TASK-7A.14**: SQLAlchemy ORM models — `TableModel`, `SectionModel`, `ReservationModel`, `WaitlistEntryModel`
- [x] **TASK-7A.15**: Repository implementations — all 4 repositories with SQLAlchemy
- [x] **TASK-7A.16**: FastAPI routes — sections CRUD, tables CRUD, status update
- [x] **TASK-7A.17**: FastAPI routes — reservations CRUD, confirm/seat/cancel/no-show
- [x] **TASK-7A.18**: FastAPI routes — availability query, waitlist CRUD
- [x] **TASK-7A.19**: Pydantic request/response schemas — all endpoints
- [x] **TASK-7A.20**: Dependency injection wiring — `dependencies.py`
- [x] **TASK-7A.21**: WebSocket endpoint — `/ws/tables/{restaurant_id}` broadcasting table status changes
- [x] **TASK-7A.22**: Unit tests — `TimeSlotAvailabilityService`, status transitions, no-show auto-release
- [ ] **TASK-7A.23**: Integration tests — full reservation lifecycle, waitlist flow, API endpoint tests

#### Frontend

- [x] **TASK-7A.30**: Create Angular feature module `libs/tables/` with routes, lazy loading
- [x] **TASK-7A.31**: API client — `TablesService`, `ReservationsService`, `WaitlistService` in `libs/api-client/`
- [x] **TASK-7A.32**: Frontend models — `Table`, `Section`, `Reservation`, `WaitlistEntry` interfaces in `libs/api-client/`
- [x] **TASK-7A.33**: NgRx Signal Store — `TablesStore` (tables, sections, reservations, waitlist state)
- [x] **TASK-7A.34**: Floor plan view — visual grid with draggable tables, color-coded by status, section grouping
- [x] **TASK-7A.35**: Table CRUD dialog — create/edit table (number, capacity, section, shape, position)
- [ ] **TASK-7A.36**: Section management — create/edit/delete sections panel
- [ ] **TASK-7A.37**: Reservation calendar — day/week view with reservation blocks per table row
- [x] **TASK-7A.38**: Reservation create dialog — date picker, time slot dropdown, party size, customer search/input, special requests
- [x] **TASK-7A.39**: Waitlist panel — queue list with estimated wait, position, notify/seat/remove actions
- [ ] **TASK-7A.40**: WebSocket integration — subscribe to table status changes, update floor plan in real-time
- [ ] **TASK-7A.41**: Reservation analytics — no-show rate, peak hours heatmap, avg turn time cards

#### Mobile

- [ ] **TASK-7A.50**: Customer app — reservation booking flow (restaurant → date → time → party size → confirm)
- [ ] **TASK-7A.51**: Customer app — waitlist join screen + real-time position tracking
- [ ] **TASK-7A.52**: Customer app — push notification handling for waitlist ready / reservation reminder
- [ ] **TASK-7A.53**: Restaurant app — floor plan view with real-time color-coded table statuses
- [ ] **TASK-7A.54**: Restaurant app — seat/clear/clean table actions via tap
- [ ] **TASK-7A.55**: Restaurant app — today's reservation list with confirm/seat/no-show actions

### Acceptance Criteria (Definition of Done)

- [ ] Floor plan renders tables by shape at (x, y) coordinates with correct color per status
- [ ] Table statuses update within 2 seconds via WebSocket across all connected clients
- [ ] Reservation booking shows only available time slots for requested party size and date
- [ ] No double-booking: system prevents overlapping reservations for the same table (enforced in domain)
- [ ] No-show auto-detection: reservation auto-marks as NO_SHOW after `hold_minutes` past start_time
- [ ] Waitlist estimated time recalculates when tables are freed or parties cancel
- [ ] All tables RLS-scoped — tenant A cannot see tenant B's tables or reservations
- [ ] Reservation confirmation sends notification (email or SMS) to customer
- [ ] API returns proper error codes: `409` for conflicts, `422` for validation, `404` for not found

---

## EPIC-7B: Kitchen Display System (KDS)

| Field | Value |
|-------|-------|
| **Epic ID** | EPIC-7B |
| **Priority** | P0 — Must Have |
| **Bounded Context** | NEW — `Kitchen` (schema: `kitchen`) |
| **Depends On** | Orders (order items), Menus (item-station mapping), TableManagement (table reference) |
| **Estimate** | 2 sprints (4 weeks) |
| **Competitors** | Toast KDS, Oracle MICROS KDS, Square KDS, Lightspeed Kitchen Display, 3S POS KDS |

### Description

Digital display system replacing paper tickets. Routes order items to correct kitchen stations, tracks preparation status in real-time, provides timing metrics. Critical for kitchen efficiency, order accuracy, and front-of-house / back-of-house coordination.

### User Stories

| ID | Role | Story | Acceptance Criteria |
|----|------|-------|-------------------|
| US-7B.1 | Kitchen Manager | I want incoming orders displayed on screen organized by station so each cook sees only their items | Orders split by station; each station screen shows only its items |
| US-7B.2 | Cook | I want to tap an item to mark it "in progress" then "ready" so servers know when to pick up | Item status cycles: NEW → IN_PROGRESS → READY; updates visible on expo screen |
| US-7B.3 | Restaurant Owner | I want to see average prep times per item and station to identify bottlenecks | Analytics dashboard with avg prep time, items/hour, overdue percentage per station |
| US-7B.4 | Server | I want to see an expo screen showing when all items for a table are ready | Expo view groups by table; table highlighted when all items READY |
| US-7B.5 | Kitchen Manager | I want to flag rush orders with visual priority | Rush orders display red border + "RUSH" badge; sorted to top of queue |

### Database Schema

#### `kitchen.stations`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | Station identifier |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | Tenant key |
| `name` | `VARCHAR(100)` | NOT NULL | Station name (e.g., "Grill", "Fryer", "Salad") |
| `station_type` | `VARCHAR(20)` | NOT NULL | Enum: `GRILL`, `FRYER`, `SALAD`, `DESSERT`, `BAR`, `PREP`, `EXPO`, `OTHER` |
| `display_order` | `INTEGER` | NOT NULL, default `0` | Sort order on configuration screen |
| `color` | `VARCHAR(7)` | NULLABLE | Hex color for visual identification (e.g., `#FF5733`) |
| `target_prep_minutes` | `INTEGER` | NOT NULL, default `15` | Default target prep time for items at this station |
| `warning_threshold_minutes` | `INTEGER` | NOT NULL, default `12` | Time before target when order turns yellow |
| `is_active` | `BOOLEAN` | NOT NULL, default `true` | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

**Unique**: `uq_kitchen_station_name (restaurant_id, name)`

#### `kitchen.item_station_mappings`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | Mapping identifier |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | Tenant key |
| `menu_item_id` | `UUID` | NOT NULL, INDEX | Cross-schema reference to `menus.menu_items(id)` |
| `station_id` | `UUID` | FK → `kitchen.stations(id)` ON DELETE CASCADE | Assigned station |
| `prep_time_override_minutes` | `INTEGER` | NULLABLE | Item-specific prep time (overrides station default) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

**Unique**: `uq_kitchen_item_station (menu_item_id, station_id)`

#### `kitchen.kitchen_orders`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | Kitchen order identifier |
| `order_id` | `UUID` | NOT NULL, INDEX | Cross-schema reference to `orders.orders(id)` |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | Tenant key |
| `table_number` | `VARCHAR(20)` | NULLABLE | Denormalized from table for display |
| `order_type` | `VARCHAR(20)` | NOT NULL | `DINE_IN`, `DELIVERY`, `TAKEAWAY` |
| `order_number` | `VARCHAR(20)` | NOT NULL | Human-readable order number |
| `status` | `VARCHAR(20)` | NOT NULL, default `'NEW'` | Enum: `NEW`, `IN_PROGRESS`, `READY`, `SERVED`, `RECALLED` |
| `priority` | `VARCHAR(10)` | NOT NULL, default `'NORMAL'` | Enum: `NORMAL`, `RUSH`, `VIP` |
| `course` | `VARCHAR(20)` | NOT NULL, default `'MAIN'` | Enum: `STARTER`, `MAIN`, `DESSERT`, `BEVERAGE` |
| `fire_at` | `TIMESTAMPTZ` | NULLABLE | Scheduled fire time (for course sequencing) |
| `fired_at` | `TIMESTAMPTZ` | NULLABLE | When order was sent to kitchen |
| `started_at` | `TIMESTAMPTZ` | NULLABLE | When first item started |
| `completed_at` | `TIMESTAMPTZ` | NULLABLE | When all items ready |
| `served_at` | `TIMESTAMPTZ` | NULLABLE | When served to guest |
| `recalled_at` | `TIMESTAMPTZ` | NULLABLE | When recalled after bump |
| `special_instructions` | `TEXT` | NULLABLE | Order-level notes |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

**Indexes**: `ix_kitchen_orders_restaurant_status (restaurant_id, status)`, `ix_kitchen_orders_order_id (order_id)`

#### `kitchen.kitchen_order_items`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | Item identifier |
| `kitchen_order_id` | `UUID` | FK → `kitchen.kitchen_orders(id)` ON DELETE CASCADE | Parent order |
| `menu_item_id` | `UUID` | NOT NULL | Cross-schema reference to `menus.menu_items(id)` |
| `station_id` | `UUID` | FK → `kitchen.stations(id)` | Routed station |
| `name` | `VARCHAR(255)` | NOT NULL | Denormalized item name |
| `quantity` | `INTEGER` | NOT NULL, default `1`, CHECK `>= 1` | |
| `modifiers` | `JSONB` | NOT NULL, default `'[]'` | Array of modifier names applied |
| `special_instructions` | `TEXT` | NULLABLE | Item-level notes |
| `status` | `VARCHAR(20)` | NOT NULL, default `'NEW'` | Enum: `NEW`, `IN_PROGRESS`, `READY` |
| `started_at` | `TIMESTAMPTZ` | NULLABLE | |
| `completed_at` | `TIMESTAMPTZ` | NULLABLE | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

**Indexes**: `ix_kitchen_order_items_station_status (station_id, status)`, `ix_kitchen_order_items_kitchen_order_id (kitchen_order_id)`

### Domain Events

| Event | Trigger | Payload | Consumers |
|-------|---------|---------|-----------|
| `KitchenOrderReceived` | Order placed → kitchen order created | `kitchen_order_id`, `order_id`, `restaurant_id`, `items[]` | KDS WebSocket broadcaster |
| `KitchenItemStarted` | Cook starts item | `kitchen_order_item_id`, `station_id` | KDS display, Expo |
| `KitchenItemReady` | Cook marks item ready | `kitchen_order_item_id`, `station_id` | KDS display, Expo |
| `KitchenOrderReady` | All items in order are READY | `kitchen_order_id`, `order_id`, `table_number` | Expo screen, Server notification |
| `KitchenOrderServed` | Server confirms delivery | `kitchen_order_id` | Analytics |
| `KitchenOrderRecalled` | Order recalled after bump | `kitchen_order_id` | KDS display |

### API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `POST` | `/api/v1/kitchen/stations` | Create station | Manager+ |
| `GET` | `/api/v1/kitchen/stations` | List stations | Staff+ |
| `PATCH` | `/api/v1/kitchen/stations/{id}` | Update station | Manager+ |
| `DELETE` | `/api/v1/kitchen/stations/{id}` | Delete station | Manager+ |
| `POST` | `/api/v1/kitchen/item-station-mappings` | Map menu items to station | Manager+ |
| `GET` | `/api/v1/kitchen/item-station-mappings` | List mappings | Staff+ |
| `DELETE` | `/api/v1/kitchen/item-station-mappings/{id}` | Remove mapping | Manager+ |
| `GET` | `/api/v1/kitchen/display/{station_id}` | Station display (active orders) | Staff+ |
| `GET` | `/api/v1/kitchen/expo` | Expo display (all stations) | Staff+ |
| `PATCH` | `/api/v1/kitchen/items/{id}/status` | Update item status | Staff+ |
| `POST` | `/api/v1/kitchen/orders/{id}/bump` | Bump order (all items → SERVED) | Staff+ |
| `POST` | `/api/v1/kitchen/orders/{id}/recall` | Recall bumped order | Staff+ |
| `POST` | `/api/v1/kitchen/orders/{id}/priority` | Set order priority | Staff+ |
| `GET` | `/api/v1/kitchen/analytics` | Prep time & throughput analytics | Manager+ |

**WebSocket**: `ws://{host}/ws/kitchen/{restaurant_id}/{station_id}` — real-time order item updates per station.

### Implementation Tasks

#### Backend

- [ ] **TASK-7B.01**: Create module scaffold `backend/src/modules/kitchen/`
- [ ] **TASK-7B.02**: Domain entities — `Station`, `KitchenOrder`, `KitchenOrderItem`, `ItemStationMapping`
- [ ] **TASK-7B.03**: Value objects — `KitchenOrderStatus`, `KitchenItemStatus`, `StationType`, `OrderPriority`, `Course`
- [ ] **TASK-7B.04**: Domain events — all 6 events
- [ ] **TASK-7B.05**: `OrderRoutingService` — split order items across stations based on item-station mapping
- [ ] **TASK-7B.06**: Application commands — station CRUD, item-station mapping CRUD
- [ ] **TASK-7B.07**: Application commands — `UpdateItemStatus`, `BumpOrder`, `RecallOrder`, `SetOrderPriority`
- [ ] **TASK-7B.08**: Application queries — `GetStationDisplay`, `GetExpoDisplay`, `GetKitchenAnalytics`
- [ ] **TASK-7B.09**: Event handler — listen `OrderPlaced` → create KitchenOrder, route items to stations
- [ ] **TASK-7B.10**: Alembic migration — `kitchen` schema, all 4 tables, indexes, RLS
- [ ] **TASK-7B.11**: SQLAlchemy models + repository implementations
- [ ] **TASK-7B.12**: FastAPI routes — all endpoints listed above
- [ ] **TASK-7B.13**: Pydantic schemas
- [ ] **TASK-7B.14**: WebSocket — per-station real-time broadcasting
- [ ] **TASK-7B.15**: Unit tests — routing logic, status transitions, timing
- [ ] **TASK-7B.16**: Integration tests — order → kitchen routing end-to-end

#### Frontend

- [ ] **TASK-7B.20**: Station management page — CRUD with type, color, target prep time
- [ ] **TASK-7B.21**: Item-station mapping page — select station, bulk assign menu items/categories
- [ ] **TASK-7B.22**: KDS analytics dashboard — avg prep time per station, items/hour chart, overdue %

#### Mobile / Tablet

- [ ] **TASK-7B.30**: Restaurant app — KDS screen per station (full-screen mode)
- [ ] **TASK-7B.31**: Order cards — order number, table/type, items with modifiers, elapsed timer, color coding (green/yellow/red)
- [ ] **TASK-7B.32**: Touch actions — tap item to cycle status, swipe to bump
- [ ] **TASK-7B.33**: Expo screen — consolidated view, highlight tables with all items READY
- [ ] **TASK-7B.34**: Audio alerts — new order chime, overdue warning tone

### Acceptance Criteria

- [ ] Order with items from 3 different stations creates 3 station-specific kitchen orders
- [ ] Each station screen shows only its assigned items; items from other stations hidden
- [ ] Item status changes propagate to all KDS screens via WebSocket within 1 second
- [ ] Elapsed time timer starts from `created_at` and changes color at warning/overdue thresholds
- [ ] Expo screen correctly identifies when all items for a table order are READY
- [ ] Recalled orders reappear on station display with visual recall indicator
- [ ] Rush orders sort to top of queue with red priority badge
- [ ] Analytics accurately calculate avg prep time as `completed_at - started_at` per item

---

## EPIC-7C: Parcel / Takeaway Orders

| Field | Value |
|-------|-------|
| **Epic ID** | EPIC-7C |
| **Priority** | P0 — Must Have |
| **Bounded Context** | Extends existing `Orders` module |
| **Depends On** | Orders, Notifications |
| **Estimate** | 1 sprint (2 weeks) |
| **Competitors** | Toast Takeout, Square Online Ordering, Restroworks Takeaway, Petpooja Takeaway POS |

### Description

Add a distinct "takeaway/pickup" order type alongside dine-in and delivery. Includes pickup time scheduling, pickup token generation, order-ready notifications, and a pickup counter queue display.

### User Stories

| ID | Role | Story | Acceptance Criteria |
|----|------|-------|-------------------|
| US-7C.1 | Customer | I want to place a takeaway order with a scheduled pickup time so my food is ready when I arrive | Checkout shows pickup time slots; order placed with TAKEAWAY type and selected time |
| US-7C.2 | Staff | I want to see takeaway orders in a dedicated queue so I can prioritize by pickup time | Pickup queue shows orders sorted by scheduled_pickup_time; filterable by status |
| US-7C.3 | Customer | I want a notification when my takeaway order is ready | Push notification + SMS sent when status changes to READY_FOR_PICKUP |
| US-7C.4 | Staff | I want to mark a takeaway order as picked up so it leaves the queue | "Mark Picked Up" button updates status and records actual_pickup_time |

### Schema Changes (Extend `orders.orders`)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `order_type` | `VARCHAR(20)` | NOT NULL, default `'DELIVERY'` | **ALTER**: Add `TAKEAWAY` to enum — `DINE_IN`, `DELIVERY`, `TAKEAWAY` |
| `scheduled_pickup_time` | `TIMESTAMPTZ` | NULLABLE | When customer wants to pick up (only for TAKEAWAY) |
| `actual_pickup_time` | `TIMESTAMPTZ` | NULLABLE | When actually collected |
| `pickup_token` | `VARCHAR(6)` | NULLABLE, INDEX | Short alphanumeric code (e.g., "A7X2") for pickup verification |

**New status value**: `READY_FOR_PICKUP` added to `OrderStatus` enum.

### Domain Events

| Event | Trigger | Payload | Consumers |
|-------|---------|---------|-----------|
| `TakeawayOrderReady` | Order status → READY_FOR_PICKUP | `order_id`, `pickup_token`, `customer_id`, `customer_phone` | Notifications (push + SMS) |
| `TakeawayOrderPickedUp` | Staff marks as picked up | `order_id`, `pickup_token`, `actual_pickup_time` | Analytics |

### API Changes

| Method | Path | Description | Changes |
|--------|------|-------------|---------|
| `POST` | `/api/v1/orders` | Create order | Accept `order_type: TAKEAWAY`, `scheduled_pickup_time` |
| `GET` | `/api/v1/orders/pickup-queue` | Pickup queue | NEW — Query: `restaurant_id`, returns TAKEAWAY orders with `READY_FOR_PICKUP` status |
| `POST` | `/api/v1/orders/{id}/picked-up` | Mark collected | NEW — Updates status, records `actual_pickup_time` |
| `GET` | `/api/v1/orders` | List orders | Add `order_type` filter parameter |

### Implementation Tasks

- [ ] **TASK-7C.01**: Add `TAKEAWAY` to `OrderType` enum, add columns to Order entity
- [ ] **TASK-7C.02**: Alembic migration — add `scheduled_pickup_time`, `actual_pickup_time`, `pickup_token` columns, `READY_FOR_PICKUP` status
- [ ] **TASK-7C.03**: Pickup token generator — 6-char alphanumeric, unique per restaurant per day
- [ ] **TASK-7C.04**: Update order creation command — validate pickup time within operating hours, skip delivery fee for TAKEAWAY
- [ ] **TASK-7C.05**: Domain events — `TakeawayOrderReady`, `TakeawayOrderPickedUp`
- [ ] **TASK-7C.06**: Event handler — on `READY_FOR_PICKUP` → trigger notification (push + SMS with token)
- [ ] **TASK-7C.07**: API — pickup queue endpoint, mark-picked-up endpoint, order_type filter
- [ ] **TASK-7C.08**: Pydantic schema updates
- [ ] **TASK-7C.09**: Unit tests — pickup token generation, operating hours validation
- [ ] **TASK-7C.10**: Integration tests — full takeaway lifecycle
- [ ] **TASK-7C.20**: Frontend — order type filter on orders list (All / Dine-in / Delivery / Takeaway)
- [ ] **TASK-7C.21**: Frontend — pickup queue tab with token, customer, scheduled time, status actions
- [ ] **TASK-7C.30**: Customer app — order type selector at checkout (Delivery / Takeaway)
- [ ] **TASK-7C.31**: Customer app — pickup time slot picker
- [ ] **TASK-7C.32**: Customer app — pickup token display on order confirmation screen
- [ ] **TASK-7C.33**: Restaurant app — takeaway queue tab with mark-picked-up action

### Acceptance Criteria

- [ ] Takeaway orders skip delivery address requirement and delivery fee
- [ ] Pickup tokens are unique within a restaurant for a given day
- [ ] Customer receives push notification + SMS when order status becomes READY_FOR_PICKUP
- [ ] Pickup queue shows only TAKEAWAY orders sorted by scheduled_pickup_time
- [ ] Analytics correctly splits revenue by order type (dine-in vs delivery vs takeaway)

---

## EPIC-7D: Invoicing & Receipt Printing

| Field | Value |
|-------|-------|
| **Epic ID** | EPIC-7D |
| **Priority** | P0 — Must Have |
| **Bounded Context** | NEW — `Invoicing` (schema: `invoicing`) |
| **Depends On** | Orders (order data), Payments (payment data), Restaurants (tax config) |
| **Estimate** | 2 sprints (4 weeks) |
| **Competitors** | All major platforms — Toast, Square, Lightspeed, TouchBistro, Restroworks, Petpooja |

### Description

Generate professional invoices and receipts in PDF format, support thermal printer output (ESC/POS protocol), email/SMS digital receipts, and maintain invoice records for tax compliance. Supports Indian GST (CGST + SGST) and international VAT.

### User Stories

| ID | Role | Story | Acceptance Criteria |
|----|------|-------|-------------------|
| US-7D.1 | Cashier | I want to print a receipt on thermal printer when a customer pays | Receipt prints within 3s of payment with all line items, taxes, total |
| US-7D.2 | Customer | I want a digital receipt via email or SMS | Invoice PDF emailed/SMS-linked within 30s of payment |
| US-7D.3 | Restaurant Owner | I want to customize invoice template with my logo and tax ID | Template editor saves logo, header, footer, GSTIN; reflected in all receipts |
| US-7D.4 | Accountant | I want daily settlement reports summarizing all transactions | Report shows total sales, cash/card split, refunds, tax collected, tip total |
| US-7D.5 | Restaurant Owner | I want configurable GST rates (CGST + SGST / IGST) per restaurant | Tax config supports multiple rates; invoice line items show tax breakdown |

### Database Schema

#### `invoicing.tax_configs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | Tenant key |
| `name` | `VARCHAR(50)` | NOT NULL | Tax name (e.g., "CGST", "SGST", "VAT", "Service Tax") |
| `rate` | `NUMERIC(5,2)` | NOT NULL, CHECK `>= 0 AND <= 100` | Tax percentage (e.g., 9.00 for 9%) |
| `tax_type` | `VARCHAR(20)` | NOT NULL | Enum: `GST_CGST`, `GST_SGST`, `GST_IGST`, `VAT`, `SERVICE_TAX`, `CUSTOM` |
| `is_inclusive` | `BOOLEAN` | NOT NULL, default `false` | Tax inclusive in menu price or added on top |
| `applies_to` | `VARCHAR(20)` | NOT NULL, default `'ALL'` | Enum: `ALL`, `FOOD`, `BEVERAGE`, `CUSTOM` |
| `is_active` | `BOOLEAN` | NOT NULL, default `true` | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

#### `invoicing.invoice_templates`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `restaurant_id` | `UUID` | NOT NULL, UNIQUE, RLS | One template per restaurant |
| `logo_url` | `VARCHAR(500)` | NULLABLE | Restaurant logo for invoice header |
| `header_text` | `TEXT` | NULLABLE | Text above line items |
| `footer_text` | `TEXT` | NULLABLE | Text below total (thank you message, return policy) |
| `tax_registration_number` | `VARCHAR(50)` | NULLABLE | GSTIN / VAT number displayed on invoice |
| `address_line` | `TEXT` | NULLABLE | Restaurant address on invoice |
| `phone` | `VARCHAR(20)` | NULLABLE | Contact number on invoice |
| `paper_width_mm` | `INTEGER` | NOT NULL, default `80` | Thermal paper width: 58 or 80 |
| `show_customer_info` | `BOOLEAN` | NOT NULL, default `true` | Display customer details on receipt |
| `custom_fields` | `JSONB` | NOT NULL, default `'{}'` | Additional configurable fields |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

#### `invoicing.invoices`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | Tenant key |
| `order_id` | `UUID` | NOT NULL, INDEX | Cross-schema reference to `orders.orders(id)` |
| `invoice_number` | `VARCHAR(30)` | NOT NULL | Sequential per restaurant (e.g., "INV-2026-000042") |
| `invoice_type` | `VARCHAR(20)` | NOT NULL, default `'SALES'` | Enum: `SALES`, `CREDIT_NOTE`, `PROFORMA` |
| `status` | `VARCHAR(20)` | NOT NULL, default `'ISSUED'` | Enum: `DRAFT`, `ISSUED`, `PAID`, `VOID` |
| `customer_name` | `VARCHAR(255)` | NULLABLE | |
| `customer_email` | `VARCHAR(255)` | NULLABLE | |
| `customer_phone` | `VARCHAR(20)` | NULLABLE | |
| `subtotal` | `NUMERIC(12,2)` | NOT NULL | Sum of line item totals before tax |
| `tax_total` | `NUMERIC(12,2)` | NOT NULL | Sum of all taxes |
| `discount_total` | `NUMERIC(12,2)` | NOT NULL, default `0` | Applied discounts/promotions |
| `tip_amount` | `NUMERIC(12,2)` | NOT NULL, default `0` | |
| `grand_total` | `NUMERIC(12,2)` | NOT NULL | subtotal + tax_total - discount_total + tip_amount |
| `currency` | `VARCHAR(3)` | NOT NULL, default `'INR'` | |
| `payment_method` | `VARCHAR(20)` | NULLABLE | `CASH`, `CARD`, `UPI`, `WALLET`, `SPLIT` |
| `payment_reference` | `VARCHAR(100)` | NULLABLE | Transaction ID / reference number |
| `notes` | `TEXT` | NULLABLE | Invoice-level notes |
| `issued_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `voided_at` | `TIMESTAMPTZ` | NULLABLE | |
| `void_reason` | `TEXT` | NULLABLE | |
| `pdf_url` | `VARCHAR(500)` | NULLABLE | S3/storage URL of generated PDF |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

**Unique**: `uq_invoicing_invoice_number (restaurant_id, invoice_number)`
**Indexes**: `ix_invoicing_invoices_restaurant_id (restaurant_id)`, `ix_invoicing_invoices_order_id (order_id)`, `ix_invoicing_invoices_issued_at (restaurant_id, issued_at)`

#### `invoicing.invoice_line_items`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `invoice_id` | `UUID` | FK → `invoicing.invoices(id)` ON DELETE CASCADE | Parent invoice |
| `name` | `VARCHAR(255)` | NOT NULL | Item name |
| `description` | `TEXT` | NULLABLE | Item description / modifiers |
| `quantity` | `INTEGER` | NOT NULL, CHECK `>= 1` | |
| `unit_price` | `NUMERIC(10,2)` | NOT NULL | Price per unit |
| `total` | `NUMERIC(10,2)` | NOT NULL | quantity × unit_price |
| `tax_details` | `JSONB` | NOT NULL, default `'[]'` | Array of `{ name, rate, amount }` per tax applied |
| `display_order` | `INTEGER` | NOT NULL, default `0` | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

#### `invoicing.daily_settlements`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | Tenant key |
| `date` | `DATE` | NOT NULL | Settlement date |
| `total_sales` | `NUMERIC(14,2)` | NOT NULL | Gross sales |
| `total_tax` | `NUMERIC(14,2)` | NOT NULL | Total tax collected |
| `total_discounts` | `NUMERIC(14,2)` | NOT NULL | Total discounts |
| `total_tips` | `NUMERIC(14,2)` | NOT NULL | Total tips |
| `total_refunds` | `NUMERIC(14,2)` | NOT NULL | Total refunds / credit notes |
| `net_revenue` | `NUMERIC(14,2)` | NOT NULL | Sales - discounts - refunds |
| `cash_total` | `NUMERIC(14,2)` | NOT NULL | Cash payments |
| `card_total` | `NUMERIC(14,2)` | NOT NULL | Card payments |
| `upi_total` | `NUMERIC(14,2)` | NOT NULL | UPI payments |
| `other_total` | `NUMERIC(14,2)` | NOT NULL | Other payment methods |
| `order_count` | `INTEGER` | NOT NULL | Total orders |
| `invoice_count` | `INTEGER` | NOT NULL | Total invoices issued |
| `generated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `generated_by` | `UUID` | NULLABLE | Staff who generated |

**Unique**: `uq_invoicing_daily_settlement (restaurant_id, date)`

### Domain Events

| Event | Trigger | Payload | Consumers |
|-------|---------|---------|-----------|
| `InvoiceGenerated` | Payment captured → invoice auto-created | `invoice_id`, `order_id`, `restaurant_id`, `invoice_number`, `grand_total` | Notifications (digital receipt), Analytics |
| `InvoiceSent` | Receipt emailed/SMS | `invoice_id`, `recipient`, `channel` | — |
| `InvoiceVoided` | Staff voids invoice | `invoice_id`, `reason`, `voided_by` | Analytics, Accounting integration |

### Implementation Tasks

#### Backend

- [ ] **TASK-7D.01**: Create module scaffold `backend/src/modules/invoicing/`
- [ ] **TASK-7D.02**: Domain entities — `Invoice`, `InvoiceLineItem`, `TaxConfig`, `InvoiceTemplate`, `DailySettlement`
- [ ] **TASK-7D.03**: Value objects — `InvoiceType`, `InvoiceStatus`, `TaxType`, `PaymentMethod`
- [ ] **TASK-7D.04**: Domain events — `InvoiceGenerated`, `InvoiceSent`, `InvoiceVoided`
- [ ] **TASK-7D.05**: `InvoiceNumberGenerator` — sequential per restaurant, configurable format (prefix, year, sequence)
- [ ] **TASK-7D.06**: `TaxCalculator` — support multiple tax rates, inclusive/exclusive, per-item calculation
- [ ] **TASK-7D.07**: Application commands — `GenerateInvoice`, `VoidInvoice`, `SendInvoice`, `ConfigureTax`, `UpdateInvoiceTemplate`, `GenerateDailySettlement`
- [ ] **TASK-7D.08**: Application queries — `GetInvoice`, `ListInvoices`, `GetInvoicePdf`, `GetDailySettlement`
- [ ] **TASK-7D.09**: Event handler — listen `PaymentCaptured` → auto-generate invoice
- [ ] **TASK-7D.10**: Alembic migration — `invoicing` schema, all 5 tables, indexes, RLS
- [ ] **TASK-7D.11**: SQLAlchemy models + repository implementations
- [ ] **TASK-7D.12**: PDF generator — WeasyPrint with HTML/CSS template, logo, tax breakdown
- [ ] **TASK-7D.13**: ESC/POS formatter — thermal printer byte stream for 58mm and 80mm paper
- [ ] **TASK-7D.14**: FastAPI routes — all endpoints
- [ ] **TASK-7D.15**: Pydantic schemas
- [ ] **TASK-7D.16**: Unit tests — tax calculation (inclusive/exclusive, multiple rates), invoice numbering, settlement totals
- [ ] **TASK-7D.17**: Integration tests — payment → invoice flow, PDF generation, daily settlement

#### Frontend

- [ ] **TASK-7D.20**: Angular feature module `libs/invoicing/`
- [ ] **TASK-7D.21**: API client — `InvoicingService` in `libs/api-client/`
- [ ] **TASK-7D.22**: Invoice list page — filterable/sortable table (date, number, customer, amount, status)
- [ ] **TASK-7D.23**: Invoice detail page — itemized view with tax breakdown, PDF download, void action
- [ ] **TASK-7D.24**: Tax configuration page — add/edit/toggle tax rates (CGST, SGST, VAT etc.)
- [ ] **TASK-7D.25**: Invoice template editor — logo upload, header/footer text, GSTIN, paper width, preview
- [ ] **TASK-7D.26**: Daily settlement page — date picker, summary cards, printable report
- [ ] **TASK-7D.27**: Send invoice dialog — email/SMS input fields, send action with status feedback

#### Mobile

- [ ] **TASK-7D.30**: Restaurant app — print receipt button on order completion (ESC/POS to connected printer)
- [ ] **TASK-7D.31**: Restaurant app — daily settlement summary view
- [ ] **TASK-7D.32**: Customer app — digital receipt in order history, PDF download

### Acceptance Criteria

- [ ] Invoice auto-generates on payment capture with correct line items, quantities, prices
- [ ] Tax calculation correct for CGST 9% + SGST 9% scenario (total 18% GST)
- [ ] Tax-inclusive pricing correctly back-calculates base price from menu price
- [ ] Invoice numbers are sequential per restaurant with no gaps
- [ ] PDF renders restaurant logo, GSTIN, itemized list, tax breakdown, total, payment method
- [ ] ESC/POS output formats correctly on 80mm and 58mm thermal printers
- [ ] Voided invoices cannot be re-issued; credit note created for refunds
- [ ] Daily settlement totals match sum of individual invoices for the day

---

# Phase 8 — Cost Control & Staffing (Sprints 9-10)

> **Phase 8 covers**: Inventory, Suppliers, Staff, Menu Engineering.
> Detailed schema and task breakdowns follow the same pattern as Phase 7.
> Abbreviated here for readability — expand each EPIC using the same template.

---

## EPIC-8A: Inventory & Stock Management

| Field | Value |
|-------|-------|
| **Epic ID** | EPIC-8A |
| **Priority** | P0 — Must Have |
| **Bounded Context** | NEW — `Inventory` (schema: `inventory`) |
| **Depends On** | Menus (recipe-item linking), Orders (auto-deduction on order) |
| **Estimate** | 2 sprints (4 weeks) |

### Key Schema Tables

#### `inventory.ingredients`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | Tenant key |
| `name` | `VARCHAR(255)` | NOT NULL | Ingredient name |
| `category` | `VARCHAR(50)` | NOT NULL | Category: `VEGETABLE`, `MEAT`, `DAIRY`, `GRAIN`, `SPICE`, `OIL`, `BEVERAGE`, `OTHER` |
| `unit_of_measure` | `VARCHAR(10)` | NOT NULL | `KG`, `G`, `LITER`, `ML`, `PIECE`, `DOZEN`, `BUNCH`, `PACKET` |
| `current_stock` | `NUMERIC(12,3)` | NOT NULL, default `0`, CHECK `>= 0` | Current quantity in stock |
| `reorder_point` | `NUMERIC(12,3)` | NOT NULL, default `0` | Alert threshold |
| `cost_per_unit` | `NUMERIC(10,2)` | NOT NULL, default `0` | Last known cost |
| `is_perishable` | `BOOLEAN` | NOT NULL, default `true` | Whether item has expiry |
| `shelf_life_days` | `INTEGER` | NULLABLE | Expected shelf life |
| `is_active` | `BOOLEAN` | NOT NULL, default `true` | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

**Unique**: `uq_inventory_ingredient_name (restaurant_id, name)`

#### `inventory.recipes`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | Tenant key |
| `menu_item_id` | `UUID` | NOT NULL, UNIQUE INDEX | Cross-schema ref to `menus.menu_items(id)` — one recipe per item |
| `yield_quantity` | `INTEGER` | NOT NULL, default `1` | How many servings this recipe produces |
| `notes` | `TEXT` | NULLABLE | Preparation notes |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

#### `inventory.recipe_ingredients`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `recipe_id` | `UUID` | FK → `inventory.recipes(id)` ON DELETE CASCADE | |
| `ingredient_id` | `UUID` | FK → `inventory.ingredients(id)` ON DELETE CASCADE | |
| `quantity` | `NUMERIC(10,3)` | NOT NULL, CHECK `> 0` | Amount needed per yield |
| `unit` | `VARCHAR(10)` | NOT NULL | Unit for this recipe step (may differ from ingredient base unit) |

**Unique**: `uq_recipe_ingredient (recipe_id, ingredient_id)`

#### `inventory.stock_movements`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | |
| `ingredient_id` | `UUID` | FK → `inventory.ingredients(id)` | |
| `movement_type` | `VARCHAR(20)` | NOT NULL | `PURCHASE`, `USAGE`, `WASTE`, `ADJUSTMENT`, `TRANSFER` |
| `quantity` | `NUMERIC(12,3)` | NOT NULL | Positive for inflow, negative for outflow |
| `unit_cost` | `NUMERIC(10,2)` | NULLABLE | Cost per unit at time of movement |
| `reference_type` | `VARCHAR(20)` | NULLABLE | `ORDER`, `PURCHASE_ORDER`, `STOCK_TAKE`, `MANUAL` |
| `reference_id` | `UUID` | NULLABLE | ID of the related order/PO/adjustment |
| `notes` | `TEXT` | NULLABLE | |
| `created_by` | `UUID` | NULLABLE | Staff who logged |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

#### `inventory.purchase_orders`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | |
| `supplier_id` | `UUID` | FK → `inventory.suppliers(id)`, NULLABLE | |
| `po_number` | `VARCHAR(30)` | NOT NULL | Sequential per restaurant |
| `status` | `VARCHAR(20)` | NOT NULL, default `'DRAFT'` | `DRAFT`, `SENT`, `PARTIALLY_RECEIVED`, `RECEIVED`, `CANCELLED` |
| `total_amount` | `NUMERIC(14,2)` | NOT NULL, default `0` | |
| `currency` | `VARCHAR(3)` | NOT NULL, default `'INR'` | |
| `notes` | `TEXT` | NULLABLE | |
| `ordered_at` | `TIMESTAMPTZ` | NULLABLE | When sent to supplier |
| `expected_delivery` | `DATE` | NULLABLE | |
| `received_at` | `TIMESTAMPTZ` | NULLABLE | When fully received |
| `created_by` | `UUID` | NULLABLE | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

#### `inventory.purchase_order_items`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `purchase_order_id` | `UUID` | FK → `inventory.purchase_orders(id)` ON DELETE CASCADE | |
| `ingredient_id` | `UUID` | FK → `inventory.ingredients(id)` | |
| `ordered_quantity` | `NUMERIC(12,3)` | NOT NULL, CHECK `> 0` | |
| `received_quantity` | `NUMERIC(12,3)` | NOT NULL, default `0` | |
| `unit_cost` | `NUMERIC(10,2)` | NOT NULL | |
| `total` | `NUMERIC(12,2)` | NOT NULL | ordered_quantity × unit_cost |
| `notes` | `TEXT` | NULLABLE | Quality notes on receive |

### Implementation Tasks

- [ ] **TASK-8A.01–08**: Domain layer (entities, VOs, events, services — UnitConversionService, FoodCostCalculator)
- [ ] **TASK-8A.09–14**: Application layer (commands, queries, ports, event handlers — OrderConfirmed → auto-deduct)
- [ ] **TASK-8A.15–22**: Infrastructure (migration, models, repos, routes, schemas, tests)
- [ ] **TASK-8A.23–30**: Frontend (Angular module, store, ingredient CRUD, recipe builder, PO management, stock take, alerts)
- [ ] **TASK-8A.31–33**: Mobile (stock check, waste logging, goods receiving)

---

## EPIC-8B: Supplier & Vendor Management

| Field | Value |
|-------|-------|
| **Epic ID** | EPIC-8B |
| **Priority** | P1 — Should Have |
| **Bounded Context** | Extends `Inventory` |
| **Depends On** | EPIC-8A (Inventory) |
| **Estimate** | 1 sprint (2 weeks) |

### Key Schema Tables

#### `inventory.suppliers`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | |
| `name` | `VARCHAR(255)` | NOT NULL | Supplier business name |
| `contact_name` | `VARCHAR(255)` | NULLABLE | Primary contact person |
| `email` | `VARCHAR(255)` | NULLABLE | |
| `phone` | `VARCHAR(20)` | NULLABLE | |
| `address` | `TEXT` | NULLABLE | Full address |
| `payment_terms` | `VARCHAR(50)` | NULLABLE | e.g., "NET30", "COD", "PREPAID" |
| `lead_time_days` | `INTEGER` | NOT NULL, default `1` | Typical delivery days |
| `rating` | `NUMERIC(2,1)` | NULLABLE, CHECK `>= 0 AND <= 5` | Internal supplier rating |
| `is_active` | `BOOLEAN` | NOT NULL, default `true` | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

#### `inventory.supplier_products`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `supplier_id` | `UUID` | FK → `inventory.suppliers(id)` ON DELETE CASCADE | |
| `ingredient_id` | `UUID` | FK → `inventory.ingredients(id)` | |
| `supplier_sku` | `VARCHAR(50)` | NULLABLE | Supplier's product code |
| `unit_price` | `NUMERIC(10,2)` | NOT NULL | Supplier price per unit |
| `min_order_quantity` | `NUMERIC(10,3)` | NOT NULL, default `1` | Minimum order quantity |
| `is_preferred` | `BOOLEAN` | NOT NULL, default `false` | Preferred supplier for this ingredient |
| `last_ordered_at` | `TIMESTAMPTZ` | NULLABLE | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

**Unique**: `uq_supplier_product (supplier_id, ingredient_id)`

### Implementation Tasks

- [ ] **TASK-8B.01–05**: Domain (entities, events, commands, queries)
- [ ] **TASK-8B.06–10**: Infrastructure (migration, models, repos, routes, schemas, tests)
- [ ] **TASK-8B.11–14**: Frontend (supplier list, detail, product catalog, price comparison)

---

## EPIC-8C: Staff & Workforce Management

| Field | Value |
|-------|-------|
| **Epic ID** | EPIC-8C |
| **Priority** | P1 — Should Have |
| **Bounded Context** | NEW — `Staff` (schema: `staff`) |
| **Depends On** | Restaurants (restaurant context), Identity (user linking) |
| **Estimate** | 2 sprints (4 weeks) |

### Key Schema Tables

#### `staff.employees`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | |
| `user_id` | `UUID` | NULLABLE, UNIQUE INDEX | Link to `identity.accounts(id)` — nullable for non-platform users |
| `first_name` | `VARCHAR(100)` | NOT NULL | |
| `last_name` | `VARCHAR(100)` | NOT NULL | |
| `email` | `VARCHAR(255)` | NULLABLE | |
| `phone` | `VARCHAR(20)` | NULLABLE | |
| `role` | `VARCHAR(30)` | NOT NULL | `SERVER`, `COOK`, `HOST`, `CASHIER`, `MANAGER`, `DELIVERY`, `CLEANER`, `CUSTOM` |
| `custom_role_name` | `VARCHAR(50)` | NULLABLE | If role = CUSTOM |
| `employment_type` | `VARCHAR(20)` | NOT NULL, default `'FULL_TIME'` | `FULL_TIME`, `PART_TIME`, `CONTRACT`, `INTERN` |
| `hourly_rate` | `NUMERIC(8,2)` | NULLABLE | For hourly employees |
| `monthly_salary` | `NUMERIC(10,2)` | NULLABLE | For salaried employees |
| `currency` | `VARCHAR(3)` | NOT NULL, default `'INR'` | |
| `hire_date` | `DATE` | NOT NULL | |
| `termination_date` | `DATE` | NULLABLE | |
| `emergency_contact_name` | `VARCHAR(255)` | NULLABLE | |
| `emergency_contact_phone` | `VARCHAR(20)` | NULLABLE | |
| `is_active` | `BOOLEAN` | NOT NULL, default `true` | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

#### `staff.schedules`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | |
| `week_start` | `DATE` | NOT NULL | Monday of the schedule week |
| `is_published` | `BOOLEAN` | NOT NULL, default `false` | |
| `published_at` | `TIMESTAMPTZ` | NULLABLE | |
| `published_by` | `UUID` | NULLABLE | |
| `notes` | `TEXT` | NULLABLE | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

**Unique**: `uq_staff_schedule_week (restaurant_id, week_start)`

#### `staff.shifts`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `schedule_id` | `UUID` | FK → `staff.schedules(id)` ON DELETE CASCADE | |
| `employee_id` | `UUID` | FK → `staff.employees(id)` | |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | |
| `date` | `DATE` | NOT NULL | Shift date |
| `start_time` | `TIME` | NOT NULL | |
| `end_time` | `TIME` | NOT NULL | |
| `role` | `VARCHAR(30)` | NOT NULL | Role for this shift |
| `break_minutes` | `INTEGER` | NOT NULL, default `0` | Scheduled break time |
| `status` | `VARCHAR(20)` | NOT NULL, default `'SCHEDULED'` | `SCHEDULED`, `CONFIRMED`, `IN_PROGRESS`, `COMPLETED`, `MISSED`, `SWAPPED` |
| `notes` | `TEXT` | NULLABLE | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

#### `staff.time_entries`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | |
| `employee_id` | `UUID` | FK → `staff.employees(id)` | |
| `shift_id` | `UUID` | FK → `staff.shifts(id)`, NULLABLE | Linked shift (null for unscheduled) |
| `clock_in` | `TIMESTAMPTZ` | NOT NULL | |
| `clock_out` | `TIMESTAMPTZ` | NULLABLE | Null if still clocked in |
| `break_minutes_actual` | `INTEGER` | NOT NULL, default `0` | |
| `total_hours` | `NUMERIC(5,2)` | NULLABLE | Computed on clock out |
| `overtime_hours` | `NUMERIC(5,2)` | NOT NULL, default `0` | |
| `geo_lat` | `NUMERIC(10,7)` | NULLABLE | Clock-in location latitude |
| `geo_lng` | `NUMERIC(10,7)` | NULLABLE | Clock-in location longitude |
| `status` | `VARCHAR(20)` | NOT NULL, default `'ACTIVE'` | `ACTIVE`, `COMPLETED`, `ADJUSTED` |
| `adjusted_by` | `UUID` | NULLABLE | Manager who made adjustment |
| `adjustment_reason` | `TEXT` | NULLABLE | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

#### `staff.shift_swap_requests`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | |
| `shift_id` | `UUID` | FK → `staff.shifts(id)` | Shift being swapped |
| `requester_id` | `UUID` | FK → `staff.employees(id)` | Employee requesting swap |
| `target_id` | `UUID` | FK → `staff.employees(id)` | Employee taking over |
| `status` | `VARCHAR(20)` | NOT NULL, default `'PENDING'` | `PENDING`, `APPROVED`, `DECLINED`, `CANCELLED` |
| `manager_notes` | `TEXT` | NULLABLE | |
| `responded_by` | `UUID` | NULLABLE | Manager who approved/declined |
| `responded_at` | `TIMESTAMPTZ` | NULLABLE | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

### Implementation Tasks

- [ ] **TASK-8C.01–10**: Domain + Application layers
- [ ] **TASK-8C.11–20**: Infrastructure (migration, models, repos, routes, schemas, tests)
- [ ] **TASK-8C.21–28**: Frontend (employee CRUD, schedule calendar, timesheet, labor cost report, swap approval)
- [ ] **TASK-8C.29–32**: Mobile (clock in/out with geo, schedule view, swap requests)

---

## EPIC-8D: Menu Engineering & Food Cost Analysis

| Field | Value |
|-------|-------|
| **Epic ID** | EPIC-8D |
| **Priority** | P1 — Should Have |
| **Bounded Context** | Extends `Analytics` + `Menus` + `Inventory` |
| **Depends On** | EPIC-8A (Inventory for food cost data) |
| **Estimate** | 1 sprint (2 weeks) |

### Implementation Tasks

- [ ] **TASK-8D.01**: `GetMenuEngineeringReport` query — join sales data + recipe cost per item
- [ ] **TASK-8D.02**: BCG matrix classifier — Stars, Plowhorses, Puzzles, Dogs based on profit margin vs popularity
- [ ] **TASK-8D.03**: `GetFoodCostTrend` query — food cost % over time periods
- [ ] **TASK-8D.04**: `PriceSimulationService` — what-if: new price → projected margin, revenue, classification change
- [ ] **TASK-8D.05**: API routes — `/api/v1/analytics/menu-engineering`, `/food-cost`, `/price-simulation`
- [ ] **TASK-8D.06**: Pydantic schemas + unit tests
- [ ] **TASK-8D.10**: Frontend — BCG matrix scatter chart (x: items sold, y: margin %)
- [ ] **TASK-8D.11**: Frontend — item profitability table (sortable, filterable)
- [ ] **TASK-8D.12**: Frontend — food cost trend line chart
- [ ] **TASK-8D.13**: Frontend — price simulation panel (select item → slider → see impact)
- [ ] **TASK-8D.14**: Frontend — alert badges for items exceeding target food cost %

---

# Phase 9 — Customer Experience & Engagement (Sprints 11-12)

## EPIC-9A: QR Code Ordering

| Field | Value |
|-------|-------|
| **Epic ID** | EPIC-9A |
| **Priority** | P1 |
| **Extends** | `Orders` + `TableManagement` |
| **Estimate** | 1.5 sprints (3 weeks) |

### Key Schema Addition

#### `orders.dine_in_sessions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | |
| `table_id` | `UUID` | NOT NULL, INDEX | Cross-schema ref to `tables.tables(id)` |
| `session_token` | `VARCHAR(32)` | NOT NULL, UNIQUE INDEX | URL-safe token for QR link |
| `status` | `VARCHAR(20)` | NOT NULL, default `'ACTIVE'` | `ACTIVE`, `CLOSED` |
| `started_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `closed_at` | `TIMESTAMPTZ` | NULLABLE | |

**Add to `orders.orders`**: `source VARCHAR(20) DEFAULT 'APP'` — Enum: `APP`, `WEB`, `QR_CODE`, `POS`, `AGGREGATOR`
**Add to `orders.orders`**: `dine_in_session_id UUID NULLABLE FK → orders.dine_in_sessions(id)`

### Implementation Tasks

- [ ] **TASK-9A.01–08**: Backend (session entity, QR URL scheme, multi-round ordering, WebSocket sync, QR image generation)
- [ ] **TASK-9A.10–14**: Frontend (QR management in table admin, bulk QR download/print)
- [ ] **TASK-9A.15–18**: PWA (responsive web menu, cart, checkout — no app install required)
- [ ] **TASK-9A.20–22**: Mobile (QR scanner, session join, multi-round ordering)

---

## EPIC-9B: Bill Splitting

| Field | Value |
|-------|-------|
| **Epic ID** | EPIC-9B |
| **Priority** | P1 |
| **Extends** | `Orders` + `Payments` |
| **Estimate** | 1 sprint (2 weeks) |

### Key Schema Addition

#### `orders.sub_checks`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `order_id` | `UUID` | FK → `orders.orders(id)` ON DELETE CASCADE | |
| `guest_label` | `VARCHAR(50)` | NOT NULL | "Guest 1", "Guest 2" or custom name |
| `split_type` | `VARCHAR(20)` | NOT NULL | `EQUAL`, `BY_ITEM`, `BY_AMOUNT`, `BY_PERCENTAGE` |
| `subtotal` | `NUMERIC(10,2)` | NOT NULL | |
| `tax` | `NUMERIC(10,2)` | NOT NULL | |
| `tip` | `NUMERIC(10,2)` | NOT NULL, default `0` | |
| `total` | `NUMERIC(10,2)` | NOT NULL | |
| `payment_status` | `VARCHAR(20)` | NOT NULL, default `'UNPAID'` | `UNPAID`, `PAID` |
| `payment_id` | `UUID` | NULLABLE | Cross-schema ref to `payments.payments(id)` |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

#### `orders.sub_check_items`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `sub_check_id` | `UUID` | FK → `orders.sub_checks(id)` ON DELETE CASCADE | |
| `order_item_id` | `UUID` | NOT NULL | Ref to original order line item |
| `quantity` | `INTEGER` | NOT NULL, default `1` | May be partial (2 of 3 pizzas to this guest) |

### Implementation Tasks

- [ ] **TASK-9B.01–06**: Backend (split logic, validation — subs must sum to total, partial payment tracking, sub-check → invoice event)
- [ ] **TASK-9B.10–13**: Frontend + Mobile (split dialog, sub-check views, per-guest payment)

---

## EPIC-9C: Customer Loyalty & CRM

| Field | Value |
|-------|-------|
| **Epic ID** | EPIC-9C |
| **Priority** | P1 |
| **Extends** | `Promotions` |
| **Estimate** | 2 sprints (4 weeks) |

### Key Schema Tables (in `promotions` schema)

#### `promotions.loyalty_programs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `restaurant_id` | `UUID` | NOT NULL, UNIQUE, RLS | One program per restaurant |
| `name` | `VARCHAR(100)` | NOT NULL | Program name |
| `earn_rate` | `NUMERIC(5,2)` | NOT NULL | Points earned per currency unit (e.g., 1 point per ₹10 → 0.10) |
| `redemption_rate` | `NUMERIC(5,2)` | NOT NULL | Currency value per point (e.g., 1 point = ₹0.50 → 0.50) |
| `min_redeem_points` | `INTEGER` | NOT NULL, default `100` | Minimum points for redemption |
| `points_expiry_days` | `INTEGER` | NULLABLE | Points expire after N days (null = never) |
| `is_active` | `BOOLEAN` | NOT NULL, default `true` | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

#### `promotions.loyalty_tiers`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `program_id` | `UUID` | FK → `promotions.loyalty_programs(id)` ON DELETE CASCADE | |
| `name` | `VARCHAR(50)` | NOT NULL | Tier name (Bronze, Silver, Gold, Platinum) |
| `min_points` | `INTEGER` | NOT NULL | Points threshold for this tier |
| `earn_multiplier` | `NUMERIC(3,1)` | NOT NULL, default `1.0` | Earn rate multiplier (Gold = 1.5×) |
| `benefits` | `JSONB` | NOT NULL, default `'{}'` | `{ "free_delivery": true, "birthday_reward": true }` |
| `display_order` | `INTEGER` | NOT NULL | |

#### `promotions.points_ledgers`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `customer_id` | `UUID` | NOT NULL, INDEX | Cross-schema ref to customer |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | |
| `total_earned` | `INTEGER` | NOT NULL, default `0` | Lifetime earned |
| `total_redeemed` | `INTEGER` | NOT NULL, default `0` | Lifetime redeemed |
| `balance` | `INTEGER` | NOT NULL, default `0` | Current available |
| `tier_id` | `UUID` | FK → `promotions.loyalty_tiers(id)`, NULLABLE | Current tier |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

**Unique**: `uq_points_ledger (customer_id, restaurant_id)`

#### `promotions.points_transactions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `ledger_id` | `UUID` | FK → `promotions.points_ledgers(id)` | |
| `type` | `VARCHAR(20)` | NOT NULL | `EARN`, `REDEEM`, `BONUS`, `EXPIRE`, `ADJUST` |
| `points` | `INTEGER` | NOT NULL | Positive for earn, negative for redeem |
| `order_id` | `UUID` | NULLABLE | Related order |
| `description` | `VARCHAR(255)` | NOT NULL | Human-readable reason |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

### Implementation Tasks

- [ ] **TASK-9C.01–12**: Backend (points engine, tier evaluation, RFM segmenter, rewards, campaigns, event handlers)
- [ ] **TASK-9C.13–18**: Frontend (loyalty config, customer profiles, segmentation, campaigns)
- [ ] **TASK-9C.20–25**: Mobile (points balance, tier progress, rewards catalog, referral sharing)

---

# Phase 10 — Enterprise & Scale (Sprints 13-14)

## EPIC-10A: Third-Party Integrations

| Field | Value |
|-------|-------|
| **Epic ID** | EPIC-10A |
| **Priority** | P1 |
| **Bounded Context** | NEW — `Integrations` (schema: `integrations`) |
| **Estimate** | 2 sprints (4 weeks) |

### Key Schema

#### `integrations.integrations`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | |
| `provider` | `VARCHAR(50)` | NOT NULL | `QUICKBOOKS`, `XERO`, `TALLY`, `SWIGGY`, `ZOMATO`, `UBER_EATS` |
| `integration_type` | `VARCHAR(30)` | NOT NULL | `ACCOUNTING`, `DELIVERY_AGGREGATOR`, `PAYMENT_GATEWAY`, `MARKETING` |
| `status` | `VARCHAR(20)` | NOT NULL, default `'INACTIVE'` | `INACTIVE`, `ACTIVE`, `ERROR`, `SUSPENDED` |
| `config` | `JSONB` | NOT NULL, default `'{}'` | Provider-specific configuration |
| `credentials_encrypted` | `BYTEA` | NULLABLE | Encrypted OAuth tokens / API keys |
| `last_sync_at` | `TIMESTAMPTZ` | NULLABLE | |
| `last_error` | `TEXT` | NULLABLE | |
| `sync_frequency` | `VARCHAR(20)` | NOT NULL, default `'DAILY'` | `REALTIME`, `HOURLY`, `DAILY`, `MANUAL` |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

#### `integrations.webhook_configs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | |
| `url` | `VARCHAR(500)` | NOT NULL | Webhook endpoint URL |
| `events` | `JSONB` | NOT NULL | Array of event names to trigger on |
| `secret` | `VARCHAR(255)` | NOT NULL | HMAC signing secret |
| `is_active` | `BOOLEAN` | NOT NULL, default `true` | |
| `last_triggered_at` | `TIMESTAMPTZ` | NULLABLE | |
| `failure_count` | `INTEGER` | NOT NULL, default `0` | Consecutive failures |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

### Implementation Tasks

- [ ] **TASK-10A.01–08**: Integration framework (adapter pattern, OAuth management, webhook dispatching)
- [ ] **TASK-10A.09–12**: Accounting adapters (QuickBooks, Xero, Tally)
- [ ] **TASK-10A.13–16**: Delivery aggregator adapters (Swiggy, Zomato, Uber Eats)
- [ ] **TASK-10A.20–24**: Frontend (integration gallery, setup wizard, health dashboard, webhook config)

---

## EPIC-10B: Multi-Location / Franchise Management

| Field | Value |
|-------|-------|
| **Epic ID** | EPIC-10B |
| **Priority** | P2 |
| **Extends** | `Restaurants` |
| **Estimate** | 1 sprint (2 weeks) |

### Key Schema Addition

#### `restaurants.restaurant_groups`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `name` | `VARCHAR(255)` | NOT NULL | Group/franchise name |
| `owner_id` | `UUID` | NOT NULL | Cross-schema ref to `identity.accounts(id)` |
| `settings` | `JSONB` | NOT NULL, default `'{}'` | Default settings for locations |
| `logo_url` | `VARCHAR(500)` | NULLABLE | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

**Add to `restaurants.restaurants`**: `group_id UUID NULLABLE FK → restaurants.restaurant_groups(id)`

### Implementation Tasks

- [ ] **TASK-10B.01–06**: Backend (group entity, menu sync, group promotions, aggregated analytics)
- [ ] **TASK-10B.10–14**: Frontend (group management, cross-location dashboard, location comparison)

---

## EPIC-10C: Waste Management & Tracking

| Field | Value |
|-------|-------|
| **Epic ID** | EPIC-10C |
| **Priority** | P2 |
| **Extends** | `Inventory` |
| **Estimate** | 0.5 sprint (1 week) |

### Key Schema Addition

#### `inventory.waste_logs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | |
| `ingredient_id` | `UUID` | FK → `inventory.ingredients(id)` | |
| `quantity` | `NUMERIC(10,3)` | NOT NULL, CHECK `> 0` | Amount wasted |
| `unit` | `VARCHAR(10)` | NOT NULL | Unit of measure |
| `reason` | `VARCHAR(30)` | NOT NULL | `EXPIRED`, `OVERPRODUCTION`, `PREPARATION`, `PLATE_WASTE`, `DAMAGED`, `SPILLAGE`, `OTHER` |
| `cost` | `NUMERIC(10,2)` | NOT NULL | Calculated from ingredient cost_per_unit |
| `station` | `VARCHAR(100)` | NULLABLE | Kitchen station where waste occurred |
| `notes` | `TEXT` | NULLABLE | |
| `logged_by` | `UUID` | NOT NULL | Staff who logged |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

### Implementation Tasks

- [ ] **TASK-10C.01–04**: Backend (waste log, reports, targets, alerts)
- [ ] **TASK-10C.10–13**: Frontend (waste form, dashboard, top wasted items, trend chart)
- [ ] **TASK-10C.20**: Mobile (quick waste log from kitchen)

---

## EPIC-10D: Compliance & Food Safety

| Field | Value |
|-------|-------|
| **Epic ID** | EPIC-10D |
| **Priority** | P2 |
| **Extends** | `Restaurants` or lightweight standalone |
| **Estimate** | 1 sprint (2 weeks) |

### Key Schema Tables

#### `compliance.checklist_templates`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | |
| `name` | `VARCHAR(255)` | NOT NULL | Template name |
| `checklist_type` | `VARCHAR(20)` | NOT NULL | `OPENING`, `CLOSING`, `TEMPERATURE`, `CLEANING`, `SAFETY` |
| `frequency` | `VARCHAR(20)` | NOT NULL | `DAILY`, `WEEKLY`, `MONTHLY` |
| `items` | `JSONB` | NOT NULL | Array of `{ description, expected_value, input_type, is_required }` |
| `is_active` | `BOOLEAN` | NOT NULL, default `true` | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

#### `compliance.checklist_completions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `template_id` | `UUID` | FK → `compliance.checklist_templates(id)` | |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | |
| `completed_by` | `UUID` | NOT NULL | Staff reference |
| `completed_at` | `TIMESTAMPTZ` | NOT NULL | |
| `items_data` | `JSONB` | NOT NULL | Array of `{ item_description, value, passed, corrective_action?, photo_url? }` |
| `overall_status` | `VARCHAR(10)` | NOT NULL | `PASS`, `FAIL`, `PARTIAL` |
| `notes` | `TEXT` | NULLABLE | |

**Immutable**: completions cannot be updated after creation (audit trail).

#### `compliance.temperature_logs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `restaurant_id` | `UUID` | NOT NULL, INDEX, RLS | |
| `equipment_name` | `VARCHAR(100)` | NOT NULL | "Walk-in Fridge", "Freezer A" |
| `temperature` | `NUMERIC(5,1)` | NOT NULL | Reading in Celsius |
| `min_safe` | `NUMERIC(5,1)` | NOT NULL | Minimum safe temp |
| `max_safe` | `NUMERIC(5,1)` | NOT NULL | Maximum safe temp |
| `is_in_range` | `BOOLEAN` | NOT NULL | Computed: min_safe <= temperature <= max_safe |
| `corrective_action` | `TEXT` | NULLABLE | Required if out of range |
| `logged_by` | `UUID` | NOT NULL | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

### Implementation Tasks

- [ ] **TASK-10D.01–06**: Backend (templates, completions, temperature logs, immutable audit trail, alerts)
- [ ] **TASK-10D.10–14**: Frontend (template builder, pending checklists, compliance history, temperature chart)
- [ ] **TASK-10D.20–22**: Mobile (daily checklist, temperature logging, photo capture)

---

# Summary

| Phase | Epics | Duration | Features | New Schemas |
|-------|-------|----------|----------|-------------|
| **Phase 7** | 7A-7D | 6-8 weeks | Tables, KDS, Takeaway, Invoicing | `tables`, `kitchen`, `invoicing` |
| **Phase 8** | 8A-8D | 6-8 weeks | Inventory, Suppliers, Staff, Menu Engineering | `inventory`, `staff` |
| **Phase 9** | 9A-9C | 5-6 weeks | QR Ordering, Bill Splitting, Loyalty/CRM | — (extends existing) |
| **Phase 10** | 10A-10D | 5-6 weeks | Integrations, Multi-Location, Waste, Compliance | `integrations`, `compliance` |
| **Total** | **15 epics** | **~24-28 weeks** | **15 features** | **7 new schemas** |

### Sprint Cadence

- **Sprint duration**: 2 weeks
- **Workflow per epic**: Backend Domain+App → Backend Infra+API → Frontend → Mobile
- **Definition of Done**:
  - [ ] All unit tests pass (domain logic, calculations, validations)
  - [ ] All integration tests pass (API endpoints, event flows, database operations)
  - [ ] Pydantic schemas complete with proper validation
  - [ ] RLS policies active on all tenant tables
  - [ ] API documented in route docstrings
  - [ ] Frontend pages functional with store, error handling, loading states
  - [ ] Mobile screens functional with proper state management
  - [ ] Code reviewed and merged to dev branch
  - [ ] No ruff lint errors, mypy strict mode passes
