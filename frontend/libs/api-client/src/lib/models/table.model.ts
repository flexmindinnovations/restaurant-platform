// Section
export interface Section {
  id: string;
  restaurant_id: string;
  name: string;
  description: string | null;
  display_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateSectionRequest {
  name: string;
  description?: string;
  display_order?: number;
}

export interface UpdateSectionRequest {
  name?: string;
  description?: string;
  display_order?: number;
}

// Table
export type TableStatus = 'AVAILABLE' | 'OCCUPIED' | 'RESERVED' | 'CLEANING' | 'BLOCKED';
export type TableShape = 'ROUND' | 'SQUARE' | 'RECTANGULAR' | 'BOOTH' | 'BAR_SEAT';

export interface RestaurantTable {
  id: string;
  restaurant_id: string;
  section_id: string | null;
  number: string;
  capacity_min: number;
  capacity_max: number;
  shape: TableShape;
  position_x: number;
  position_y: number;
  status: TableStatus;
  turn_time_minutes: number;
  buffer_minutes: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateTableRequest {
  number: string;
  section_id?: string;
  capacity_min?: number;
  capacity_max: number;
  shape?: string;
  position_x?: number;
  position_y?: number;
  turn_time_minutes?: number;
  buffer_minutes?: number;
}

export interface UpdateTableRequest {
  number?: string;
  section_id?: string;
  capacity_min?: number;
  capacity_max?: number;
  shape?: string;
  position_x?: number;
  position_y?: number;
  turn_time_minutes?: number;
  buffer_minutes?: number;
}

// Reservation
export type ReservationStatus = 'PENDING' | 'CONFIRMED' | 'SEATED' | 'COMPLETED' | 'NO_SHOW' | 'CANCELLED';
export type ReservationSource = 'PLATFORM' | 'PHONE' | 'WALK_IN' | 'THIRD_PARTY';

export interface Reservation {
  id: string;
  restaurant_id: string;
  table_id: string | null;
  customer_id: string | null;
  customer_name: string;
  customer_phone: string | null;
  customer_email: string | null;
  date: string;
  start_time: string;
  end_time: string;
  party_size: number;
  status: ReservationStatus;
  special_requests: string | null;
  internal_notes: string | null;
  source: ReservationSource;
  seated_at: string | null;
  completed_at: string | null;
  cancelled_at: string | null;
  cancellation_reason: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateReservationRequest {
  restaurant_id: string;
  date: string;
  start_time: string;
  party_size: number;
  customer_name: string;
  customer_phone?: string;
  customer_email?: string;
  special_requests?: string;
  table_id?: string;
  source?: string;
}

export interface CancelReservationRequest {
  reason?: string;
}

// Waitlist
export type WaitlistStatus = 'WAITING' | 'NOTIFIED' | 'SEATED' | 'LEFT' | 'CANCELLED';

export interface WaitlistEntry {
  id: string;
  restaurant_id: string;
  customer_name: string;
  customer_phone: string;
  customer_id: string | null;
  party_size: number;
  estimated_wait_minutes: number;
  queue_position: number;
  status: WaitlistStatus;
  preferred_section: string | null;
  special_requests: string | null;
  notified_at: string | null;
  seated_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface JoinWaitlistRequest {
  restaurant_id: string;
  customer_name: string;
  customer_phone: string;
  party_size: number;
  preferred_section?: string;
  special_requests?: string;
}

// Floor plan
export interface FloorPlanSection {
  section: Section;
  tables: RestaurantTable[];
}

export interface FloorPlan {
  sections: FloorPlanSection[];
  unassigned_tables: RestaurantTable[];
}

// Available slots
export interface AvailableSlot {
  start_time: string;
  end_time: string;
  table_id: string;
  table_number: string;
  capacity_min: number;
  capacity_max: number;
}

// List params
export interface TableListParams {
  restaurant_id: string;
  section_id?: string;
  active_only?: boolean;
  skip?: number;
  limit?: number;
}

export interface ReservationListParams {
  restaurant_id: string;
  reservation_date?: string;
  skip?: number;
  limit?: number;
}

export interface WaitlistListParams {
  restaurant_id: string;
  skip?: number;
  limit?: number;
}

// Status display helpers
export const TABLE_STATUS_LABELS: Record<TableStatus, string> = {
  AVAILABLE: 'Available',
  OCCUPIED: 'Occupied',
  RESERVED: 'Reserved',
  CLEANING: 'Cleaning',
  BLOCKED: 'Blocked',
};

export const TABLE_STATUS_COLORS: Record<TableStatus, string> = {
  AVAILABLE: 'success',
  OCCUPIED: 'error',
  RESERVED: 'warning',
  CLEANING: 'info',
  BLOCKED: 'neutral',
};

export const RESERVATION_STATUS_LABELS: Record<ReservationStatus, string> = {
  PENDING: 'Pending',
  CONFIRMED: 'Confirmed',
  SEATED: 'Seated',
  COMPLETED: 'Completed',
  NO_SHOW: 'No Show',
  CANCELLED: 'Cancelled',
};
