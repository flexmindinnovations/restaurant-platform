import { signalStore, withState, withMethods, patchState } from '@ngrx/signals';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { tapResponse } from '@ngrx/operators';
import { of, forkJoin, switchMap, catchError } from 'rxjs';
import { inject } from '@angular/core';
import { AnalyticsService } from '@app/api-client';

export interface AnalyticPoint {
  label: string;
  value: number;
}

export interface RestaurantPerformance {
  name: string;
  orders_count: number;
  rating: number;
  revenue: number;
}

export interface AnalyticsState {
  commissionTrend: AnalyticPoint[];
  peakHours: AnalyticPoint[];
  restaurantPerformance: RestaurantPerformance[];
  loading: boolean;
  error: string | null;
}

const initialState: AnalyticsState = {
  commissionTrend: [],
  peakHours: [
    { label: '08:00 - 11:00', value: 85 },
    { label: '11:00 - 14:00 (Lunch)', value: 420 },
    { label: '14:00 - 17:00', value: 120 },
    { label: '17:00 - 20:00 (Dinner)', value: 680 },
    { label: '20:00 - 23:00', value: 310 },
  ],
  restaurantPerformance: [],
  loading: false,
  error: null,
};

export const AnalyticsStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),
  withMethods((store, analyticsService = inject(AnalyticsService)) => ({
    loadAnalyticsData: rxMethod<void>((trigger$) =>
      trigger$.pipe(
        switchMap(() => {
          patchState(store, { loading: true, error: null });

          return forkJoin([
            analyticsService.getRevenueBreakdown().pipe(
              catchError((err) => {
                console.error('Error fetching revenue breakdown:', err);
                return of(null);
              }),
            ),
            analyticsService.getPlatformDashboard().pipe(
              catchError((err) => {
                console.error('Error fetching platform dashboard:', err);
                return of(null);
              }),
            ),
          ]).pipe(
            tapResponse({
              next: ([revenueData, platformData]) => {
                if (!revenueData) {
                  patchState(store, { error: 'Failed to load analytics data.', loading: false });
                  return;
                }

                // Calculate daily commissions
                const ratio =
                  Number(revenueData.total_revenue) > 0
                    ? Number(revenueData.commission_revenue) / Number(revenueData.total_revenue)
                    : 0.15;

                const commissionTrend = (revenueData.daily_revenue || []).map((s) => ({
                  label: new Date(s.date).toLocaleDateString(undefined, { weekday: 'short' }),
                  value: Math.round(Number(s.revenue) * ratio),
                }));

                const restaurantPerformance = (revenueData.top_restaurants || []).map((r) => ({
                  name: r.name,
                  orders_count: r.order_count,
                  rating: Number(r.average_rating),
                  revenue: Number(r.revenue),
                }));

                patchState(store, {
                  commissionTrend,
                  restaurantPerformance,
                  loading: false,
                });
              },
              error: (err: unknown) => {
                patchState(store, { error: String(err), loading: false });
              },
            }),
          );
        }),
      ),
    ),
  })),
);

export type AnalyticsStoreType = InstanceType<typeof AnalyticsStore>;
