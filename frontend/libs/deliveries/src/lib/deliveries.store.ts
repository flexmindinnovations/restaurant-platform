import { inject } from '@angular/core';
import { signalStore, withState, withMethods, patchState } from '@ngrx/signals';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { tapResponse } from '@ngrx/operators';
import { forkJoin, pipe, switchMap } from 'rxjs';
import { DeliveryPartner, ActiveDelivery } from './deliveries.model';
import { DeliveriesService } from './deliveries.service';

export interface DeliveriesState {
  partners: DeliveryPartner[];
  deliveries: ActiveDelivery[];
  selectedDelivery: ActiveDelivery | null;
  loading: boolean;
  error: string | null;
}

const initialState: DeliveriesState = {
  partners: [],
  deliveries: [],
  selectedDelivery: null,
  loading: false,
  error: null,
};

export const DeliveriesStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),
  withMethods((store, service = inject(DeliveriesService)) => ({
    loadAll: rxMethod<void>(
      pipe(
        switchMap(() => {
          patchState(store, { loading: true, error: null });
          return forkJoin({
            partners: service.getPartners(),
            deliveries: service.getActiveDeliveries(),
          }).pipe(
            tapResponse({
              next: (result) =>
                patchState(store, {
                  partners: result.partners,
                  deliveries: result.deliveries,
                  loading: false,
                }),
              error: (err: unknown) =>
                patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    assignPartner: rxMethod<{ deliveryId: string; partnerId: string | null }>(
      pipe(
        switchMap(({ deliveryId, partnerId }) => {
          patchState(store, { loading: true });
          return service.overrideAssignment(deliveryId, partnerId).pipe(
            tapResponse({
              next: (result) => {
                const updatedSel = result.deliveries.find((d) => d.id === deliveryId) || null;
                patchState(store, {
                  partners: result.partners,
                  deliveries: result.deliveries,
                  selectedDelivery: store.selectedDelivery()?.id === deliveryId ? updatedSel : store.selectedDelivery(),
                  loading: false,
                });
              },
              error: (err: unknown) => patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    selectDelivery(delivery: ActiveDelivery | null): void {
      patchState(store, { selectedDelivery: delivery });
    },
  })),
);

export type DeliveriesStoreType = InstanceType<typeof DeliveriesStore>;
