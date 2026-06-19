export type OrderStatus =
  | 'PENDING'
  | 'CONFIRMED'
  | 'PREPARING'
  | 'READY'
  | 'OUT_FOR_DELIVERY'
  | 'DELIVERED'
  | 'COMPLETED'
  | 'CANCELLED';

export interface OrderItem {
  id: string;
  menu_item_id: string;
  name: string;
  unit_price_amount: string;
  unit_price_currency: string;
  quantity: number;
  special_instructions: string | null;
  subtotal_amount: string;
}

export interface Order {
  id: string;
  restaurant_id: string;
  customer_id: string;
  order_number: string;
  status: OrderStatus;
  delivery_address_street: string;
  delivery_address_city: string;
  delivery_address_state: string;
  delivery_address_postal_code: string;
  delivery_address_country: string;
  delivery_notes: string | null;
  subtotal_amount: string;
  subtotal_currency: string;
  tax_amount: string;
  tax_currency: string;
  delivery_fee_amount: string;
  delivery_fee_currency: string;
  tip_amount: string;
  tip_currency: string;
  total_amount: string;
  total_currency: string;
  cancellation_reason: string | null;
  placed_at: string;
  confirmed_at: string | null;
  preparing_at: string | null;
  ready_at: string | null;
  picked_up_at: string | null;
  delivered_at: string | null;
  cancelled_at: string | null;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
}

export interface OrderListParams {
  status?: OrderStatus;
  restaurant_id?: string;
  skip?: number;
  limit?: number;
}

export interface OrderListResponse {
  items: Order[];
  total: number;
}

export interface UpdateOrderStatusRequest {
  status: OrderStatus;
}

export interface CancelOrderRequest {
  reason: string;
}

export const ORDER_STATUS_LABELS: Record<OrderStatus, string> = {
  PENDING: 'Pending',
  CONFIRMED: 'Confirmed',
  PREPARING: 'Preparing',
  READY: 'Ready',
  OUT_FOR_DELIVERY: 'Out for Delivery',
  DELIVERED: 'Delivered',
  COMPLETED: 'Completed',
  CANCELLED: 'Cancelled',
};

export const ORDER_STATUS_COLORS: Record<OrderStatus, string> = {
  PENDING: 'warn',
  CONFIRMED: 'primary',
  PREPARING: 'accent',
  READY: 'accent',
  OUT_FOR_DELIVERY: 'primary',
  DELIVERED: 'primary',
  COMPLETED: 'primary',
  CANCELLED: 'warn',
};
