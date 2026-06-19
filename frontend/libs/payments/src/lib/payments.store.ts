import { inject } from '@angular/core';
import { signalStore, withState, withMethods, withComputed, patchState } from '@ngrx/signals';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { tapResponse } from '@ngrx/operators';
import { pipe, switchMap, debounceTime, distinctUntilChanged } from 'rxjs';
import { computed } from '@angular/core';
import { PaymentTransaction, PaymentListParams, PaymentStatus } from './payments.model';
import { PaymentsService } from './payments.service';

export interface PaymentsState {
  payments: PaymentTransaction[];
  total: number;
  loading: boolean;
  error: string | null;
  skip: number;
  limit: number;
  search: string;
  statusFilter: PaymentStatus | 'ALL';
}

const initialState: PaymentsState = {
  payments: [],
  total: 0,
  loading: false,
  error: null,
  skip: 0,
  limit: 10,
  search: '',
  statusFilter: 'ALL',
};

export const PaymentsStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),

  withComputed((store) => ({
    totalPages: computed(() => Math.ceil(store.total() / store.limit())),
    currentPage: computed(() => Math.floor(store.skip() / store.limit())),
    hasResults: computed(() => store.payments().length > 0),
  })),

  withMethods((store, paymentsService = inject(PaymentsService)) => ({
    loadPayments: rxMethod<PaymentListParams | void>(
      pipe(
        debounceTime(250),
        distinctUntilChanged(),
        switchMap((params) => {
          patchState(store, { loading: true, error: null });
          const mergedParams: PaymentListParams = {
            skip: store.skip(),
            limit: store.limit(),
            search: store.search() || undefined,
            status: store.statusFilter(),
            ...(params || {}),
          };
          return paymentsService.list(mergedParams).pipe(
            tapResponse({
              next: (result) =>
                patchState(store, {
                  payments: result.items,
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

    refundTransaction: rxMethod<string>(
      pipe(
        switchMap((id) => {
          patchState(store, { loading: true });
          return paymentsService.refund(id).pipe(
            tapResponse({
              next: (updatedTx) => {
                const updated = store.payments().map((p) => (p.id === id ? updatedTx : p));
                patchState(store, {
                  payments: updated,
                  loading: false,
                });
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

    setStatusFilter(status: PaymentStatus | 'ALL'): void {
      patchState(store, { statusFilter: status, skip: 0 });
    },

    setPage(page: number): void {
      patchState(store, { skip: page * store.limit() });
    },
  })),
);

export type PaymentsStoreType = InstanceType<typeof PaymentsStore>;
