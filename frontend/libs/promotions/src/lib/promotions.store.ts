import { inject } from '@angular/core';
import { signalStore, withState, withMethods, patchState } from '@ngrx/signals';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { tapResponse } from '@ngrx/operators';
import { pipe, switchMap } from 'rxjs';
import { Promotion } from './promotions.model';
import { PromotionsService } from './promotions.service';

export interface PromotionsState {
  promotions: Promotion[];
  loading: boolean;
  error: string | null;
  selectedPromotion: Promotion | null;
}

const initialState: PromotionsState = {
  promotions: [],
  loading: false,
  error: null,
  selectedPromotion: null,
};

export const PromotionsStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),
  withMethods((store, service = inject(PromotionsService)) => ({
    loadAll: rxMethod<void>(
      pipe(
        switchMap(() => {
          patchState(store, { loading: true, error: null });
          return service.getPromotions().pipe(
            tapResponse({
              next: (promotions) => patchState(store, { promotions, loading: false }),
              error: (err: unknown) => patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    create: rxMethod<Partial<Promotion>>(
      pipe(
        switchMap((promo) => {
          patchState(store, { loading: true, error: null });
          return service.createPromotion(promo).pipe(
            tapResponse({
              next: (promotions) => patchState(store, { promotions, loading: false }),
              error: (err: unknown) => patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    update: rxMethod<{ id: string; updated: Partial<Promotion> }>(
      pipe(
        switchMap(({ id, updated }) => {
          patchState(store, { loading: true, error: null });
          return service.updatePromotion(id, updated).pipe(
            tapResponse({
              next: (promotions) => {
                const updatedSelected = promotions.find((p) => p.id === id) || null;
                patchState(store, {
                  promotions,
                  selectedPromotion: store.selectedPromotion()?.id === id ? updatedSelected : store.selectedPromotion(),
                  loading: false,
                });
              },
              error: (err: unknown) => patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    delete: rxMethod<string>(
      pipe(
        switchMap((id) => {
          patchState(store, { loading: true, error: null });
          return service.deletePromotion(id).pipe(
            tapResponse({
              next: (promotions) => patchState(store, { promotions, loading: false }),
              error: (err: unknown) => patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    selectPromotion(promo: Promotion | null): void {
      patchState(store, { selectedPromotion: promo });
    },
  })),
);

export type PromotionsStoreType = InstanceType<typeof PromotionsStore>;
