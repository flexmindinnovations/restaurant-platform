import { signalStore, withState, withMethods, withComputed, patchState } from '@ngrx/signals';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { tapResponse } from '@ngrx/operators';
import { of, delay, switchMap } from 'rxjs';
import { computed } from '@angular/core';

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
    orders: { label: 'Total Orders', value: '1,482', change: '+12.4%', isPositive: true, icon: 'shopping_bag' },
    revenue: { label: 'Total Revenue', value: '$28,450.00', change: '+8.5%', isPositive: true, icon: 'attach_money' },
    partners: { label: 'Active Partners', value: '42', change: '+4.8%', isPositive: true, icon: 'storefront' },
    users: { label: 'New Users', value: '156', change: '+18.2%', isPositive: true, icon: 'person_add' },
  },
  ordersTrend: [
    { label: 'Mon', value: 120 },
    { label: 'Tue', value: 150 },
    { label: 'Wed', value: 180 },
    { label: 'Thu', value: 140 },
    { label: 'Fri', value: 220 },
    { label: 'Sat', value: 310 },
    { label: 'Sun', value: 290 },
  ],
  revenueTrend: [
    { label: 'Mon', value: 2400 },
    { label: 'Tue', value: 3100 },
    { label: 'Wed', value: 3600 },
    { label: 'Thu', value: 2800 },
    { label: 'Fri', value: 4400 },
    { label: 'Sat', value: 6200 },
    { label: 'Sun', value: 5800 },
  ],
  recentOrders: [
    { id: '001', customer: 'John Doe', amount: '45.99', status: 'Completed', time: '2 min ago' },
    { id: '002', customer: 'Jane Smith', amount: '82.50', status: 'Completed', time: '5 min ago' },
    { id: '003', customer: 'Mike Johnson', amount: '120.00', status: 'Pending', time: '10 min ago' },
    { id: '004', customer: 'Sarah Williams', amount: '65.75', status: 'Completed', time: '15 min ago' },
    { id: '005', customer: 'Tom Brown', amount: '156.30', status: 'Completed', time: '22 min ago' },
  ],
  loading: false,
  error: null,
};

export const DashboardStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),
  withComputed((store) => ({
    isLoading: computed(() => store.loading()),
    hasError: computed(() => !!store.error()),
  })),
  withMethods((store) => ({
    loadDashboardData: rxMethod<void>((trigger$) =>
      trigger$.pipe(
        switchMap(() => {
          patchState(store, { loading: true, error: null });
          // Simulating API call
          return of({
            kpis: { ...store.kpis() },
            ordersTrend: [...store.ordersTrend()],
            revenueTrend: [...store.revenueTrend()],
            recentOrders: [...store.recentOrders()],
          }).pipe(
            delay(300),
            tapResponse({
              next: (data) => patchState(store, { ...data, loading: false }),
              error: (err: unknown) =>
                patchState(store, { error: String(err), loading: false }),
            })
          );
        })
      )
    ),
  }))
);

export type DashboardStoreType = InstanceType<typeof DashboardStore>;
