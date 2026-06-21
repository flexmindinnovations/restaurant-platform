import { inject } from '@angular/core';
import { signalStore, withState, withMethods, withComputed, patchState } from '@ngrx/signals';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { tapResponse } from '@ngrx/operators';
import { pipe, switchMap, debounceTime, distinctUntilChanged } from 'rxjs';
import { computed } from '@angular/core';
import { User, UserListParams, UserRole } from './users.model';
import { UsersService } from './users.service';

export interface UsersState {
  users: User[];
  selectedUser: User | null;
  total: number;
  loading: boolean;
  error: string | null;
  skip: number;
  limit: number;
  search: string;
  roleFilter: UserRole | 'ALL';
}

const initialState: UsersState = {
  users: [],
  selectedUser: null,
  total: 0,
  loading: false,
  error: null,
  skip: 0,
  limit: 10,
  search: '',
  roleFilter: 'ALL',
};

export const UsersStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),

  withComputed((store) => ({
    totalPages: computed(() => Math.ceil(store.total() / store.limit())),
    currentPage: computed(() => Math.floor(store.skip() / store.limit())),
    hasResults: computed(() => store.users().length > 0),
  })),

  withMethods((store, usersService = inject(UsersService)) => ({
    loadUsers: rxMethod<UserListParams | void>(
      pipe(
        debounceTime(250),
        distinctUntilChanged(),
        switchMap((params) => {
          patchState(store, { loading: true, error: null });
          const mergedParams: UserListParams = {
            skip: store.skip(),
            limit: store.limit(),
            search: store.search() || undefined,
            role: store.roleFilter(),
            ...(params || {}),
          };
          return usersService.list(mergedParams).pipe(
            tapResponse({
              next: (result) =>
                patchState(store, {
                  users: result.items,
                  total: result.total,
                  loading: false,
                }),
              error: (err: unknown) => patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    updateUserRole: rxMethod<{ id: string; roles: UserRole[] }>(
      pipe(
        switchMap(({ id, roles }) => {
          patchState(store, { loading: true });
          return usersService.updateRole(id, roles).pipe(
            tapResponse({
              next: (updatedUser) => {
                const updated = store.users().map((u) => (u.id === id ? updatedUser : u));
                patchState(store, {
                  users: updated,
                  loading: false,
                  selectedUser:
                    store.selectedUser()?.id === id ? updatedUser : store.selectedUser(),
                });
              },
              error: (err: unknown) => patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    toggleUserStatus: rxMethod<string>(
      pipe(
        switchMap((id) => {
          patchState(store, { loading: true });
          return usersService.toggleStatus(id).pipe(
            tapResponse({
              next: (updatedUser) => {
                const updated = store.users().map((u) => (u.id === id ? updatedUser : u));
                patchState(store, {
                  users: updated,
                  loading: false,
                  selectedUser:
                    store.selectedUser()?.id === id ? updatedUser : store.selectedUser(),
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

    setRoleFilter(role: UserRole | 'ALL'): void {
      patchState(store, { roleFilter: role, skip: 0 });
    },

    setPage(page: number): void {
      patchState(store, { skip: page * store.limit() });
    },

    selectUser(user: User): void {
      patchState(store, { selectedUser: user });
    },

    clearSelected(): void {
      patchState(store, { selectedUser: null });
    },
  })),
);

export type UsersStoreType = InstanceType<typeof UsersStore>;
