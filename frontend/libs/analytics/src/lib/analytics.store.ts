import { signalStore, withState, withMethods, patchState } from '@ngrx/signals';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { tapResponse } from '@ngrx/operators';
import { of, delay, switchMap } from 'rxjs';

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
  commissionTrend: [
    { label: 'Mon', value: 240 },
    { label: 'Tue', value: 310 },
    { label: 'Wed', value: 360 },
    { label: 'Thu', value: 280 },
    { label: 'Fri', value: 440 },
    { label: 'Sat', value: 620 },
    { label: 'Sun', value: 580 },
  ],
  peakHours: [
    { label: '08:00 - 11:00', value: 85 },
    { label: '11:00 - 14:00 (Lunch)', value: 420 },
    { label: '14:00 - 17:00', value: 120 },
    { label: '17:00 - 20:00 (Dinner)', value: 680 },
    { label: '20:00 - 23:00', value: 310 },
  ],
  restaurantPerformance: [
    { name: 'Pizza Roma', orders_count: 320, rating: 4.8, revenue: 6400 },
    { name: 'Burger Joint', orders_count: 280, rating: 4.5, revenue: 4200 },
    { name: 'Sushi Zen', orders_count: 150, rating: 4.9, revenue: 5800 },
    { name: 'Taco Express', orders_count: 410, rating: 4.2, revenue: 3690 },
    { name: 'Salad House', orders_count: 90, rating: 4.6, revenue: 1170 },
  ],
  loading: false,
  error: null,
};

export const AnalyticsStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),
  withMethods((store) => ({
    loadAnalyticsData: rxMethod<void>(
      pipe => pipe.pipe(
        switchMap(() => {
          patchState(store, { loading: true, error: null });
          return of({
            commissionTrend: [...store.commissionTrend()],
            peakHours: [...store.peakHours()],
            restaurantPerformance: [...store.restaurantPerformance()],
          }).pipe(
            delay(250),
            tapResponse({
              next: (data) => patchState(store, { ...data, loading: false }),
              error: (err: unknown) => patchState(store, { error: String(err), loading: false }),
            })
          );
        })
      )
    ),
  }))
);

export type AnalyticsStoreType = InstanceType<typeof AnalyticsStore>;
