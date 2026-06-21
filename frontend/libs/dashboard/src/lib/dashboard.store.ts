import { signalStore, withState, withMethods, withComputed, patchState } from '@ngrx/signals';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { tapResponse } from '@ngrx/operators';
import { of, forkJoin, switchMap, catchError } from 'rxjs';
import { computed, inject } from '@angular/core';
import { AnalyticsService, RestaurantsService, OrdersService } from '@app/api-client';
import { AuthService, DecodedToken } from '@app/auth';

export interface DashboardKPI {
  value: string;
  change: string;
  isPositive: boolean;
  label: string;
  icon: string;
}

export interface TrendPoint {
  label: string;
  value: number;
}

export interface RecentOrder {
  id: string;
  customer: string;
  amount: string;
  status: 'Pending' | 'Completed' | 'Cancelled';
  time: string;
}

export interface DashboardState {
  kpis: {
    orders: DashboardKPI;
    revenue: DashboardKPI;
    partners: DashboardKPI;
    users: DashboardKPI;
  };
  ordersTrend: TrendPoint[];
  revenueTrend: TrendPoint[];
  recentOrders: RecentOrder[];
  loading: boolean;
  error: string | null;
}

const initialState: DashboardState = {
  kpis: {
    orders: {
      label: 'Total Orders',
      value: '0',
      change: '0%',
      isPositive: true,
      icon: 'shopping-bag',
    },
    revenue: {
      label: 'Total Revenue',
      value: '₹0.00',
      change: '0%',
      isPositive: true,
      icon: 'indian-rupee',
    },
    partners: {
      label: 'Active Partners',
      value: '0',
      change: '0%',
      isPositive: true,
      icon: 'store',
    },
    users: { label: 'New Users', value: '0', change: '0%', isPositive: true, icon: 'user-plus' },
  },
  ordersTrend: [],
  revenueTrend: [],
  recentOrders: [],
  loading: false,
  error: null,
};

function mapOrderStatus(status: string): 'Pending' | 'Completed' | 'Cancelled' {
  if (status === 'COMPLETED') return 'Completed';
  if (status === 'CANCELLED') return 'Cancelled';
  return 'Pending';
}

function formatRelativeTime(dateStr: string): string {
  try {
    const diffMs = new Date().getTime() - new Date(dateStr).getTime();
    const diffMin = Math.floor(diffMs / 60000);
    if (diffMin < 1) return 'Just now';
    if (diffMin < 60) return `${diffMin} min ago`;
    const diffHr = Math.floor(diffMin / 60);
    if (diffHr < 24) return `${diffHr} hr ago`;
    return new Date(dateStr).toLocaleDateString();
  } catch {
    return 'recently';
  }
}

export const DashboardStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),
  withComputed((store) => ({
    isLoading: computed(() => store.loading()),
    hasError: computed(() => !!store.error()),
  })),
  withMethods(
    (
      store,
      analyticsService = inject(AnalyticsService),
      restaurantsService = inject(RestaurantsService),
      ordersService = inject(OrdersService),
      authService = inject(AuthService),
    ) => {
      const handlePlatformData = (platformData: any, ordersList: any) => {
        if (!platformData) return;

        const dailyStats = platformData.daily_stats || [];
        const ordersTrend = dailyStats.map((s: any) => ({
          label: new Date(s.date).toLocaleDateString(undefined, { weekday: 'short' }),
          value: s.order_count,
        }));
        const revenueTrend = dailyStats.map((s: any) => ({
          label: new Date(s.date).toLocaleDateString(undefined, { weekday: 'short' }),
          value: Number(s.revenue),
        }));

        const recentOrders = (ordersList?.items || []).map((o: any) => ({
          id: o.order_number,
          customer: `Customer #${o.customer_id.substring(0, 5)}`,
          amount: Number(o.total_amount).toFixed(2),
          status: mapOrderStatus(o.status),
          time: formatRelativeTime(o.placed_at || o.created_at),
        }));

        patchState(store, {
          kpis: {
            orders: {
              label: 'Total Orders',
              value: platformData.total_orders.toLocaleString(),
              change: '+0.0%',
              isPositive: true,
              icon: 'shopping-bag',
            },
            revenue: {
              label: 'Total Revenue',
              value: `₹${Number(platformData.total_revenue).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
              change: '+0.0%',
              isPositive: true,
              icon: 'indian-rupee',
            },
            partners: {
              label: 'Active Partners',
              value: platformData.total_restaurants.toString(),
              change: '+0.0%',
              isPositive: true,
              icon: 'store',
            },
            users: {
              label: 'Total Customers',
              value: platformData.total_customers.toString(),
              change: '+0.0%',
              isPositive: true,
              icon: 'users',
            },
          },
          ordersTrend,
          revenueTrend,
          recentOrders,
          loading: false,
        });
      };

      const handleRestaurantData = (restaurantData: any, ordersList: any) => {
        if (!restaurantData) return;

        const dailyStats = restaurantData.daily_stats || [];
        const ordersTrend = dailyStats.map((s: any) => ({
          label: new Date(s.date).toLocaleDateString(undefined, { weekday: 'short' }),
          value: s.order_count,
        }));
        const revenueTrend = dailyStats.map((s: any) => ({
          label: new Date(s.date).toLocaleDateString(undefined, { weekday: 'short' }),
          value: Number(s.revenue),
        }));

        const recentOrders = (ordersList?.items || []).map((o: any) => ({
          id: o.order_number,
          customer: `Customer #${o.customer_id.substring(0, 5)}`,
          amount: Number(o.total_amount).toFixed(2),
          status: mapOrderStatus(o.status),
          time: formatRelativeTime(o.placed_at || o.created_at),
        }));

        patchState(store, {
          kpis: {
            orders: {
              label: 'Total Orders',
              value: restaurantData.total_orders.toLocaleString(),
              change: '+0.0%',
              isPositive: true,
              icon: 'shopping-bag',
            },
            revenue: {
              label: 'Total Revenue',
              value: `₹${Number(restaurantData.total_revenue).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
              change: '+0.0%',
              isPositive: true,
              icon: 'indian-rupee',
            },
            partners: {
              label: 'Average Rating',
              value: restaurantData.average_rating.toFixed(1),
              change: '',
              isPositive: true,
              icon: 'star',
            },
            users: {
              label: 'Popular Items',
              value: restaurantData.popular_items.length.toString(),
              change: '',
              isPositive: true,
              icon: 'utensils-crossed',
            },
          },
          ordersTrend,
          revenueTrend,
          recentOrders,
          loading: false,
        });
      };

      return {
        loadDashboardData: rxMethod<void>((trigger$) =>
          trigger$.pipe(
            switchMap(() => {
              patchState(store, { loading: true, error: null });

              if (typeof window === 'undefined') {
                return of(null);
              }

              const user: DecodedToken | null = authService.getDecodedToken();
              if (!user || !authService.isLoggedIn()) {
                patchState(store, {
                  error: 'Your session has expired. Please log in again.',
                  loading: false,
                });
                authService.logout();
                return of(null);
              }

              const roles: string[] = user.roles || [];
              const isSuperAdmin = roles.includes('SUPER_ADMIN');
              const isRestaurantStaff =
                roles.includes('RESTAURANT_OWNER') || roles.includes('RESTAURANT_MANAGER');

              if (isSuperAdmin) {
                return forkJoin([
                  analyticsService.getPlatformDashboard().pipe(
                    catchError((err) => {
                      console.error('Error fetching platform dashboard:', err);
                      return of(null);
                    }),
                  ),
                  ordersService.list({ limit: 5 }).pipe(
                    catchError((err) => {
                      console.error('Error fetching recent orders:', err);
                      return of({ items: [], total: 0 });
                    }),
                  ),
                ]).pipe(
                  tapResponse({
                    next: ([platformData, ordersList]) =>
                      handlePlatformData(platformData, ordersList),
                    error: (err: unknown) => {
                      patchState(store, { error: String(err), loading: false });
                    },
                  }),
                );
              } else if (isRestaurantStaff) {
                return restaurantsService.list().pipe(
                  switchMap((resList) => {
                    const myRestaurant = (resList.items || []).find(
                      (r: any) => r.owner_id === user.sub,
                    );
                    if (!myRestaurant) {
                      throw new Error('No restaurant associated with this account found.');
                    }
                    const rId = myRestaurant.id;
                    return forkJoin([
                      analyticsService.getRestaurantDashboard(rId).pipe(
                        catchError((err) => {
                          console.error('Error fetching restaurant dashboard:', err);
                          return of(null);
                        }),
                      ),
                      ordersService.list({ restaurant_id: rId, limit: 5 }).pipe(
                        catchError((err) => {
                          console.error('Error fetching restaurant orders:', err);
                          return of({ items: [], total: 0 });
                        }),
                      ),
                    ]);
                  }),
                  tapResponse({
                    next: ([restaurantData, ordersList]) =>
                      handleRestaurantData(restaurantData, ordersList),
                    error: (err: unknown) => {
                      patchState(store, { error: String(err), loading: false });
                    },
                  }),
                );
              } else {
                patchState(store, {
                  error: 'Access denied: Dashboard restricted to admins/owners.',
                  loading: false,
                });
                return of(null);
              }
            }),
          ),
        ),
      };
    },
  ),
);

export type DashboardStoreType = InstanceType<typeof DashboardStore>;
