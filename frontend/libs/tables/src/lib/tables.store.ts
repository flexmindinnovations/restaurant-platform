import { inject } from '@angular/core';
import { signalStore, withState, withMethods, withComputed, patchState } from '@ngrx/signals';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { tapResponse } from '@ngrx/operators';
import { pipe, switchMap } from 'rxjs';
import { computed } from '@angular/core';
import {
  RestaurantTable,
  Section,
  Reservation,
  WaitlistEntry,
  TableListParams,
  ReservationListParams,
  WaitlistListParams,
  CreateTableRequest,
  CreateReservationRequest,
  JoinWaitlistRequest,
} from '@app/api-client';
import { TablesService } from '@app/api-client';

export interface TablesState {
  tables: RestaurantTable[];
  sections: Section[];
  reservations: Reservation[];
  waitlistEntries: WaitlistEntry[];
  selectedRestaurantId: string | null;
  selectedSectionId: string | null;
  reservationDate: string | null;
  tablesTotal: number;
  reservationsTotal: number;
  waitlistTotal: number;
  loading: boolean;
  error: string | null;
}

const initialState: TablesState = {
  tables: [],
  sections: [],
  reservations: [],
  waitlistEntries: [],
  selectedRestaurantId: null,
  selectedSectionId: null,
  reservationDate: null,
  tablesTotal: 0,
  reservationsTotal: 0,
  waitlistTotal: 0,
  loading: false,
  error: null,
};

export const TablesStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),

  withComputed((store) => ({
    hasTables: computed(() => store.tables().length > 0),
    hasReservations: computed(() => store.reservations().length > 0),
    hasWaitlist: computed(() => store.waitlistEntries().length > 0),
    availableTables: computed(() => store.tables().filter((t) => t.status === 'AVAILABLE')),
    tablesBySection: computed(() => {
      const sections = store.sections();
      const tables = store.tables();
      const grouped = new Map<string | null, RestaurantTable[]>();
      for (const table of tables) {
        const key = table.section_id;
        if (!grouped.has(key)) grouped.set(key, []);
        grouped.get(key)!.push(table);
      }
      return { sections, grouped };
    }),
  })),

  withMethods((store, tablesService = inject(TablesService)) => ({
    setRestaurantId(restaurantId: string): void {
      patchState(store, { selectedRestaurantId: restaurantId });
    },

    setSectionFilter(sectionId: string | null): void {
      patchState(store, { selectedSectionId: sectionId });
    },

    setReservationDate(date: string | null): void {
      patchState(store, { reservationDate: date });
    },

    loadSections: rxMethod<string>(
      pipe(
        switchMap((restaurantId) => {
          patchState(store, { loading: true, error: null });
          return tablesService.listSections(restaurantId).pipe(
            tapResponse({
              next: (result) =>
                patchState(store, {
                  sections: result.items,
                  loading: false,
                }),
              error: (err: unknown) => patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    loadTables: rxMethod<TableListParams>(
      pipe(
        switchMap((params) => {
          patchState(store, { loading: true, error: null });
          return tablesService.listTables(params).pipe(
            tapResponse({
              next: (result) =>
                patchState(store, {
                  tables: result.items,
                  tablesTotal: result.total,
                  loading: false,
                }),
              error: (err: unknown) => patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    createTable: rxMethod<CreateTableRequest>(
      pipe(
        switchMap((body) => {
          patchState(store, { loading: true, error: null });
          return tablesService.createTable(body).pipe(
            tapResponse({
              next: (table) =>
                patchState(store, {
                  tables: [...store.tables(), table],
                  tablesTotal: store.tablesTotal() + 1,
                  loading: false,
                }),
              error: (err: unknown) => patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    updateTableStatus: rxMethod<{ id: string; status: string }>(
      pipe(
        switchMap(({ id, status }) => {
          return tablesService.updateTableStatus(id, status).pipe(
            tapResponse({
              next: () => {
                const updated = store
                  .tables()
                  .map((t) => (t.id === id ? { ...t, status: status as RestaurantTable['status'] } : t));
                patchState(store, { tables: updated });
              },
              error: (err: unknown) => patchState(store, { error: String(err) }),
            }),
          );
        }),
      ),
    ),

    deleteTable: rxMethod<string>(
      pipe(
        switchMap((id) => {
          return tablesService.deleteTable(id).pipe(
            tapResponse({
              next: () => {
                const updated = store.tables().filter((t) => t.id !== id);
                patchState(store, {
                  tables: updated,
                  tablesTotal: Math.max(0, store.tablesTotal() - 1),
                });
              },
              error: (err: unknown) => patchState(store, { error: String(err) }),
            }),
          );
        }),
      ),
    ),

    loadReservations: rxMethod<ReservationListParams>(
      pipe(
        switchMap((params) => {
          patchState(store, { loading: true, error: null });
          return tablesService.listReservations(params).pipe(
            tapResponse({
              next: (result) =>
                patchState(store, {
                  reservations: result.items,
                  reservationsTotal: result.total,
                  loading: false,
                }),
              error: (err: unknown) => patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    createReservation: rxMethod<CreateReservationRequest>(
      pipe(
        switchMap((body) => {
          patchState(store, { loading: true, error: null });
          return tablesService.createReservation(body).pipe(
            tapResponse({
              next: () => {
                // Reload reservations after creation
                const restaurantId = store.selectedRestaurantId();
                if (restaurantId) {
                  const params: ReservationListParams = { restaurant_id: restaurantId };
                  const date = store.reservationDate();
                  if (date) params.reservation_date = date;
                  tablesService.listReservations(params).subscribe((result) => {
                    patchState(store, {
                      reservations: result.items,
                      reservationsTotal: result.total,
                      loading: false,
                    });
                  });
                } else {
                  patchState(store, { loading: false });
                }
              },
              error: (err: unknown) => patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    confirmReservation: rxMethod<{ id: string; tableId: string }>(
      pipe(
        switchMap(({ id, tableId }) => {
          return tablesService.confirmReservation(id, tableId).pipe(
            tapResponse({
              next: () => {
                const updated = store
                  .reservations()
                  .map((r) => (r.id === id ? { ...r, status: 'CONFIRMED' as const, table_id: tableId } : r));
                patchState(store, { reservations: updated });
              },
              error: (err: unknown) => patchState(store, { error: String(err) }),
            }),
          );
        }),
      ),
    ),

    seatReservation: rxMethod<string>(
      pipe(
        switchMap((id) => {
          return tablesService.seatReservation(id).pipe(
            tapResponse({
              next: () => {
                const updated = store
                  .reservations()
                  .map((r) => (r.id === id ? { ...r, status: 'SEATED' as const } : r));
                patchState(store, { reservations: updated });
              },
              error: (err: unknown) => patchState(store, { error: String(err) }),
            }),
          );
        }),
      ),
    ),

    cancelReservation: rxMethod<{ id: string; reason?: string }>(
      pipe(
        switchMap(({ id, reason }) => {
          return tablesService.cancelReservation(id, reason ? { reason } : undefined).pipe(
            tapResponse({
              next: () => {
                const updated = store
                  .reservations()
                  .map((r) => (r.id === id ? { ...r, status: 'CANCELLED' as const } : r));
                patchState(store, { reservations: updated });
              },
              error: (err: unknown) => patchState(store, { error: String(err) }),
            }),
          );
        }),
      ),
    ),

    markNoShow: rxMethod<string>(
      pipe(
        switchMap((id) => {
          return tablesService.markNoShow(id).pipe(
            tapResponse({
              next: () => {
                const updated = store
                  .reservations()
                  .map((r) => (r.id === id ? { ...r, status: 'NO_SHOW' as const } : r));
                patchState(store, { reservations: updated });
              },
              error: (err: unknown) => patchState(store, { error: String(err) }),
            }),
          );
        }),
      ),
    ),

    loadWaitlist: rxMethod<WaitlistListParams>(
      pipe(
        switchMap((params) => {
          patchState(store, { loading: true, error: null });
          return tablesService.listWaitlist(params).pipe(
            tapResponse({
              next: (result) =>
                patchState(store, {
                  waitlistEntries: result.items,
                  waitlistTotal: result.total,
                  loading: false,
                }),
              error: (err: unknown) => patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    joinWaitlist: rxMethod<JoinWaitlistRequest>(
      pipe(
        switchMap((body) => {
          patchState(store, { loading: true, error: null });
          return tablesService.joinWaitlist(body).pipe(
            tapResponse({
              next: () => {
                const restaurantId = store.selectedRestaurantId();
                if (restaurantId) {
                  tablesService.listWaitlist({ restaurant_id: restaurantId }).subscribe((result) => {
                    patchState(store, {
                      waitlistEntries: result.items,
                      waitlistTotal: result.total,
                      loading: false,
                    });
                  });
                } else {
                  patchState(store, { loading: false });
                }
              },
              error: (err: unknown) => patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    notifyWaitlist: rxMethod<string>(
      pipe(
        switchMap((entryId) => {
          return tablesService.notifyWaitlist(entryId).pipe(
            tapResponse({
              next: () => {
                const updated = store
                  .waitlistEntries()
                  .map((e) => (e.id === entryId ? { ...e, status: 'NOTIFIED' as const } : e));
                patchState(store, { waitlistEntries: updated });
              },
              error: (err: unknown) => patchState(store, { error: String(err) }),
            }),
          );
        }),
      ),
    ),

    seatFromWaitlist: rxMethod<{ entryId: string; tableId: string }>(
      pipe(
        switchMap(({ entryId, tableId }) => {
          return tablesService.seatFromWaitlist(entryId, tableId).pipe(
            tapResponse({
              next: () => {
                const updated = store
                  .waitlistEntries()
                  .map((e) => (e.id === entryId ? { ...e, status: 'SEATED' as const } : e));
                patchState(store, { waitlistEntries: updated });
              },
              error: (err: unknown) => patchState(store, { error: String(err) }),
            }),
          );
        }),
      ),
    ),

    removeFromWaitlist: rxMethod<string>(
      pipe(
        switchMap((entryId) => {
          return tablesService.removeFromWaitlist(entryId).pipe(
            tapResponse({
              next: () => {
                const updated = store.waitlistEntries().filter((e) => e.id !== entryId);
                patchState(store, {
                  waitlistEntries: updated,
                  waitlistTotal: Math.max(0, store.waitlistTotal() - 1),
                });
              },
              error: (err: unknown) => patchState(store, { error: String(err) }),
            }),
          );
        }),
      ),
    ),
  })),
);

export type TablesStoreType = InstanceType<typeof TablesStore>;
