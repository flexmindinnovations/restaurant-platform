export interface Promotion {
  id: string;
  code: string;
  discount_type: 'PERCENTAGE' | 'FIXED';
  discount_value: number;
  min_order_value: number;
  start_date: string;
  end_date: string;
  status: 'ACTIVE' | 'EXPIRED' | 'PAUSED';
  usage_count: number;
  max_usages: number | null;
  restaurant_id: string | null;
  restaurant_name: string | null;
  total_discount_amount: number;
}
