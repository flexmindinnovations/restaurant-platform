export interface DailyOrderStatsResponse {
  date: string;
  order_count: number;
  revenue: number;
  average_order_value: number;
  currency: string;
}

export interface PopularItemResponse {
  menu_item_id: string;
  name: string;
  order_count: number;
  total_revenue: number;
  currency: string;
}

export interface PeakHourResponse {
  hour: number;
  order_count: number;
  average_revenue: number;
  currency: string;
}

export interface DeliveryStatsResponse {
  total_deliveries: number;
  average_delivery_minutes: number;
  on_time_percentage: number;
}

export interface CustomerStatsResponse {
  total_customers: number;
  new_customers: number;
  returning_customers: number;
  retention_rate: number;
}

export interface TopRestaurantResponse {
  restaurant_id: string;
  name: string;
  order_count: number;
  revenue: number;
  average_rating: number;
  currency: string;
}

export interface RestaurantDashboardResponse {
  restaurant_id: string;
  daily_stats: DailyOrderStatsResponse[];
  popular_items: PopularItemResponse[];
  peak_hours: PeakHourResponse[];
  delivery_stats: DeliveryStatsResponse | null;
  total_orders: number;
  total_revenue: number;
  average_rating: number;
  currency: string;
}

export interface PlatformDashboardResponse {
  total_restaurants: number;
  total_orders: number;
  total_revenue: number;
  total_customers: number;
  daily_stats: DailyOrderStatsResponse[];
  customer_stats: CustomerStatsResponse | null;
  delivery_stats: DeliveryStatsResponse | null;
  top_restaurants: TopRestaurantResponse[];
  currency: string;
}

export interface RevenueBreakdownResponse {
  total_revenue: number;
  commission_revenue: number;
  delivery_revenue: number;
  daily_revenue: DailyOrderStatsResponse[];
  top_restaurants: TopRestaurantResponse[];
  currency: string;
}
