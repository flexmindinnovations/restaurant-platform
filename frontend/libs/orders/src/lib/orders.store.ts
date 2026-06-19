import { inject } from '@angular/core';
import { signalStore, withState, withMethods, withComputed, patchState } from '@ngrx/signals';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { tapResponse } from '@ngrx/operators';
import { pipe, switchMap } from 'rxjs';
import { computed } from '@angular/core';
import { Order, OrderListParams, OrderStatus } from '@app/api-client';
import { OrdersService } from '@app/api-client';

export interface OrdersState {
  orders: Order[];
  selectedOrder: Order | null;
  total: number;
  loading: boolean;
  detailLoading: boolean;
  error: string | null;
  statusFilter: OrderStatus | 'ALL';
  skip: number;
  limit: number;
}

const initialState: OrdersState = {
  orders: [],
  selectedOrder: null,
  total: 0,
  loading: false,
  detailLoading: false,
  error: null,
  statusFilter: 'ALL',
  skip: 0,
  limit: 20,
};

export const OrdersStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),

  withComputed((store) => ({
    totalPages: computed(() => Math.ceil(store.total() / store.limit())),
    hasResults: computed(() => store.orders().length > 0),
  })),

  withMethods((store, ordersService = inject(OrdersService)) => ({
    loadOrders: rxMethod<void>(
      pipe(
        switchMap(() => {
          patchState(store, { loading: true, error: null });
          const params: OrderListParams = {
            skip: store.skip(),
            limit: store.limit(),
            ...(store.statusFilter() !== 'ALL'
              ? { status: store.statusFilter() as OrderStatus }
              : {}),
          };
          return ordersService.list(params).pipe(
            tapResponse({
              next: (r) =>
                patchState(store, { orders: r.items, total: r.total, loading: false }),
              error: (err: unknown) =>
                patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    loadOrder: rxMethod<string>(
      pipe(
        switchMap((id) => {
          patchState(store, { detailLoading: true, error: null });
          return ordersService.get(id).pipe(
            tapResponse({
              next: (order) =>
                patchState(store, { selectedOrder: order, detailLoading: false }),
              error: (err: unknown) =>
                patchState(store, { error: String(err), detailLoading: false }),
            }),
          );
        }),
      ),
    ),

    confirmOrder: rxMethod<string>(
      pipe(
        switchMap((id) => {
          return ordersService.confirm(id).pipe(
            tapResponse({
              next: () => {
                const update = (o: Order): Order =>
                  o.id === id ? { ...o, status: 'CONFIRMED' as OrderStatus } : o;
                patchState(store, {
                  orders: store.orders().map(update),
                  selectedOrder:
                    store.selectedOrder()?.id === id
                      ? update(store.selectedOrder()!)
                      : store.selectedOrder(),
                });
              },
              error: (err: unknown) => patchState(store, { error: String(err) }),
            }),
          );
        }),
      ),
    ),

    cancelOrder: rxMethod<{ id: string; reason: string }>(
      pipe(
        switchMap(({ id, reason }) => {
          return ordersService.cancel(id, reason).pipe(
            tapResponse({
              next: () => {
                const update = (o: Order): Order =>
                  o.id === id
                    ? { ...o, status: 'CANCELLED' as OrderStatus, cancellation_reason: reason }
                    : o;
                patchState(store, {
                  orders: store.orders().map(update),
                  selectedOrder:
                    store.selectedOrder()?.id === id
                      ? update(store.selectedOrder()!)
                      : store.selectedOrder(),
                });
              },
              error: (err: unknown) => patchState(store, { error: String(err) }),
            }),
          );
        }),
      ),
    ),

    setStatusFilter(status: OrderStatus | 'ALL'): void {
      patchState(store, { statusFilter: status, skip: 0 });
    },

    setPage(page: number): void {
      patchState(store, { skip: page * store.limit() });
    },

    selectOrder(order: Order | null): void {
      patchState(store, { selectedOrder: order });
    },

    clearError(): void {
      patchState(store, { error: null });
    },
  })),
);

export type OrdersStoreType = InstanceType<typeof OrdersStore>;
