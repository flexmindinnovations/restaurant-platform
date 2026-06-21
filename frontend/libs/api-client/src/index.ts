// Models
export type {
  Restaurant,
  CreateRestaurantRequest,
  UpdateRestaurantRequest,
  RestaurantListParams,
  PaginatedResponse,
  ApiResponse,
} from './lib/models/restaurant.model';
export type {
  Menu,
  Category,
  MenuItem,
  CreateMenuRequest,
  UpdateMenuRequest,
  CreateCategoryRequest,
  UpdateCategoryRequest,
  CreateMenuItemRequest,
  UpdateMenuItemRequest,
  MenuListParams,
} from './lib/models/menu.model';
export type {
  Order,
  OrderItem,
  OrderStatus,
  OrderListParams,
  OrderListResponse,
  UpdateOrderStatusRequest,
  CancelOrderRequest,
} from './lib/models/order.model';
export { ORDER_STATUS_LABELS, ORDER_STATUS_COLORS } from './lib/models/order.model';
export type {
  DailyOrderStatsResponse,
  PopularItemResponse,
  PeakHourResponse,
  DeliveryStatsResponse,
  CustomerStatsResponse,
  TopRestaurantResponse,
  RestaurantDashboardResponse,
  PlatformDashboardResponse,
  RevenueBreakdownResponse,
} from './lib/models/analytics.model';

// Services
export { RestaurantsService } from './lib/services/restaurants.service';
export { MenusService } from './lib/services/menus.service';
export { OrdersService } from './lib/services/orders.service';
export { AnalyticsService } from './lib/services/analytics.service';

// Interceptor
export { authInterceptor } from './lib/auth.interceptor';
