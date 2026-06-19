import { inject } from '@angular/core';
import { signalStore, withState, withMethods, withComputed, patchState } from '@ngrx/signals';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { tapResponse } from '@ngrx/operators';
import { pipe, switchMap, debounceTime, distinctUntilChanged, of, delay } from 'rxjs';
import { computed } from '@angular/core';
import { Restaurant, RestaurantListParams } from '@app/api-client';
import { RestaurantsService } from '@app/api-client';

export interface RestaurantsState {
  restaurants: Restaurant[];
  selectedRestaurant: Restaurant | null;
  total: number;
  loading: boolean;
  error: string | null;
  skip: number;
  limit: number;
  search: string;
  filterVerified: boolean | null;
}

const initialState: RestaurantsState = {
  restaurants: [],
  selectedRestaurant: null,
  total: 0,
  loading: false,
  error: null,
  skip: 0,
  limit: 20,
  search: '',
  filterVerified: null,
};

export const RestaurantsStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),

  withComputed((store) => ({
    totalPages: computed(() => Math.ceil(store.total() / store.limit())),
    currentPage: computed(() => Math.floor(store.skip() / store.limit())),
    hasResults: computed(() => store.restaurants().length > 0),
  })),

  withMethods((store, restaurantsService = inject(RestaurantsService)) => ({
    loadRestaurants: rxMethod<RestaurantListParams | void>(
      pipe(
        debounceTime(300),
        distinctUntilChanged(),
        switchMap((params) => {
          patchState(store, { loading: true, error: null });
          const mergedParams: RestaurantListParams = {
            skip: store.skip(),
            limit: store.limit(),
            search: store.search() || undefined,
            ...(store.filterVerified() !== null ? { is_verified: store.filterVerified()! } : {}),
            ...(params || {}),
          };
          return restaurantsService.list(mergedParams).pipe(
            tapResponse({
              next: (result) =>
                patchState(store, {
                  restaurants: result.items,
                  total: result.total,
                  loading: false,
                }),
              error: (err: unknown) =>
                patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    loadRestaurant: rxMethod<string>(
      pipe(
        switchMap((id) => {
          patchState(store, { loading: true, error: null });
          return restaurantsService.get(id).pipe(
            tapResponse({
              next: (r) => patchState(store, { selectedRestaurant: r, loading: false }),
              error: (err: unknown) =>
                patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    verifyRestaurant: rxMethod<string>(
      pipe(
        switchMap((id) => {
          return restaurantsService.verify(id).pipe(
            tapResponse({
              next: () => {
                const updated = store
                  .restaurants()
                  .map((r) => (r.id === id ? { ...r, is_verified: true } : r));
                patchState(store, { restaurants: updated });
                const sel = store.selectedRestaurant();
                if (sel?.id === id) {
                  patchState(store, { selectedRestaurant: { ...sel, is_verified: true } });
                }
              },
              error: (err: unknown) => patchState(store, { error: String(err) }),
            }),
          );
        }),
      ),
    ),

    rejectRestaurant: rxMethod<string>(
      pipe(
        switchMap((id) => {
          patchState(store, { loading: true });
          return of(null).pipe(
            delay(200),
            tapResponse({
              next: () => {
                const updated = store.restaurants().filter((r) => r.id !== id);
                patchState(store, {
                  restaurants: updated,
                  total: Math.max(0, store.total() - 1),
                  loading: false,
                });
                if (store.selectedRestaurant()?.id === id) {
                  patchState(store, { selectedRestaurant: null });
                }
              },
              error: (err: unknown) => patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    setSearch(search: string): void {
      patchState(store, { search, skip: 0 });
    },

    setFilterVerified(value: boolean | null): void {
      patchState(store, { filterVerified: value, skip: 0 });
    },

    setPage(page: number): void {
      patchState(store, { skip: page * store.limit() });
    },

    clearSelected(): void {
      patchState(store, { selectedRestaurant: null });
    },
  })),
);

export type RestaurantsStoreType = InstanceType<typeof RestaurantsStore>;
