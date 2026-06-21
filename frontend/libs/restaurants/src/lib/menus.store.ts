import { inject } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { signalStore, withState, withMethods, patchState } from '@ngrx/signals';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { tapResponse } from '@ngrx/operators';
import { HttpErrorResponse } from '@angular/common/http';
import { pipe, switchMap } from 'rxjs';
import {
  Category,
  CreateCategoryRequest,
  CreateMenuItemRequest,
  CreateMenuRequest,
  Menu,
  MenuItem,
  UpdateMenuRequest,
} from '@app/api-client';
import { MenusService } from '@app/api-client';

function extractErrorMessage(err: unknown): string {
  if (err instanceof HttpErrorResponse) {
    const body = err.error;
    if (body?.error?.message) return body.error.message;
    if (body?.detail) return typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
  }
  return 'An unexpected error occurred';
}

export interface MenusState {
  menus: Menu[];
  selectedMenu: Menu | null;
  total: number;
  loading: boolean;
  error: string | null;
  restaurantId: string | null;
}

const initialState: MenusState = {
  menus: [],
  selectedMenu: null,
  total: 0,
  loading: false,
  error: null,
  restaurantId: null,
};

export const MenusStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),

  withMethods((store, menusService = inject(MenusService), snackBar = inject(MatSnackBar)) => ({
    loadMenus: rxMethod<string>(
      pipe(
        switchMap((restaurantId) => {
          patchState(store, { loading: true, error: null, restaurantId });
          return menusService.list({ restaurant_id: restaurantId }).pipe(
            tapResponse({
              next: (r) => {
                const menus = r.items.map((m) => ({
                  ...m,
                  categories: m.categories.map((c) => ({ ...c, items: c.items ?? [] })),
                }));
                patchState(store, { menus, total: r.total, loading: false });
              },
              error: (err: unknown) => {
                const msg = extractErrorMessage(err);
                patchState(store, { error: msg, loading: false });
                snackBar.open(msg, 'Dismiss', { duration: 5000 });
              },
            }),
          );
        }),
      ),
    ),

    loadMenu: rxMethod<string>(
      pipe(
        switchMap((menuId) => {
          patchState(store, { loading: true, error: null });
          return menusService.get(menuId).pipe(
            tapResponse({
              next: (m) => {
                const menu = {
                  ...m,
                  categories: m.categories.map((c) => ({ ...c, items: c.items ?? [] })),
                };
                patchState(store, { selectedMenu: menu, loading: false });
              },
              error: (err: unknown) => {
                const msg = extractErrorMessage(err);
                patchState(store, { error: msg, loading: false });
                snackBar.open(msg, 'Dismiss', { duration: 5000 });
              },
            }),
          );
        }),
      ),
    ),

    createMenu: rxMethod<CreateMenuRequest>(
      pipe(
        switchMap((body) => {
          patchState(store, { loading: true, error: null });
          const requestBody: CreateMenuRequest = {
            ...body,
            restaurant_id: body.restaurant_id || store.restaurantId() || undefined,
          };
          return menusService.create(requestBody).pipe(
            tapResponse({
              next: (m) => patchState(store, { menus: [...store.menus(), m], loading: false }),
              error: (err: unknown) => {
                const msg = extractErrorMessage(err);
                patchState(store, { error: msg, loading: false });
                snackBar.open(msg, 'Dismiss', { duration: 5000 });
              },
            }),
          );
        }),
      ),
    ),

    updateMenu: rxMethod<{ id: string; body: UpdateMenuRequest }>(
      pipe(
        switchMap(({ id, body }) => {
          return menusService.update(id, body).pipe(
            tapResponse({
              next: (updated) => {
                const menus = store.menus().map((m) => (m.id === id ? updated : m));
                patchState(store, {
                  menus,
                  selectedMenu: store.selectedMenu()?.id === id ? updated : store.selectedMenu(),
                });
              },
              error: (err: unknown) => {
                const msg = extractErrorMessage(err);
                patchState(store, { error: msg });
                snackBar.open(msg, 'Dismiss', { duration: 5000 });
              },
            }),
          );
        }),
      ),
    ),

    deleteMenu: rxMethod<string>(
      pipe(
        switchMap((id) => {
          return menusService.delete(id).pipe(
            tapResponse({
              next: () =>
                patchState(store, {
                  menus: store.menus().filter((m) => m.id !== id),
                }),
              error: (err: unknown) => {
                const msg = extractErrorMessage(err);
                patchState(store, { error: msg });
                snackBar.open(msg, 'Dismiss', { duration: 5000 });
              },
            }),
          );
        }),
      ),
    ),

    activateMenu: rxMethod<string>(
      pipe(
        switchMap((id) => {
          return menusService.activate(id).pipe(
            tapResponse({
              next: () => {
                const menus = store.menus().map((m) => (m.id === id ? { ...m, is_active: true } : m));
                patchState(store, { menus });
              },
              error: (err: unknown) => {
                const msg = extractErrorMessage(err);
                patchState(store, { error: msg });
                snackBar.open(msg, 'Dismiss', { duration: 5000 });
              },
            }),
          );
        }),
      ),
    ),

    deactivateMenu: rxMethod<string>(
      pipe(
        switchMap((id) => {
          return menusService.deactivate(id).pipe(
            tapResponse({
              next: () => {
                const menus = store.menus().map((m) => (m.id === id ? { ...m, is_active: false } : m));
                patchState(store, { menus });
              },
              error: (err: unknown) => {
                const msg = extractErrorMessage(err);
                patchState(store, { error: msg });
                snackBar.open(msg, 'Dismiss', { duration: 5000 });
              },
            }),
          );
        }),
      ),
    ),

    // --- Categories ---
    addCategory: rxMethod<{ menuId: string; body: CreateCategoryRequest }>(
      pipe(
        switchMap(({ menuId, body }) => {
          return menusService.addCategory(menuId, body).pipe(
            tapResponse({
              next: (cat: Category) => {
                const menus = store
                  .menus()
                  .map((m) =>
                    m.id === menuId
                      ? { ...m, categories: [...m.categories, { ...cat, items: [] as MenuItem[] }] }
                      : m,
                  );
                patchState(store, { menus });
              },
              error: (err: unknown) => {
                const msg = extractErrorMessage(err);
                patchState(store, { error: msg });
                snackBar.open(msg, 'Dismiss', { duration: 5000 });
              },
            }),
          );
        }),
      ),
    ),

    deleteCategory: rxMethod<{ menuId: string; categoryId: string }>(
      pipe(
        switchMap(({ menuId, categoryId }) => {
          return menusService.deleteCategory(menuId, categoryId).pipe(
            tapResponse({
              next: () => {
                const menus = store
                  .menus()
                  .map((m) =>
                    m.id === menuId
                      ? { ...m, categories: m.categories.filter((c) => c.id !== categoryId) }
                      : m,
                  );
                patchState(store, { menus });
              },
              error: (err: unknown) => {
                const msg = extractErrorMessage(err);
                patchState(store, { error: msg });
                snackBar.open(msg, 'Dismiss', { duration: 5000 });
              },
            }),
          );
        }),
      ),
    ),

    // --- Items ---
    addItem: rxMethod<{ menuId: string; categoryId: string | null; body: CreateMenuItemRequest }>(
      pipe(
        switchMap(({ menuId, categoryId, body }) => {
          return menusService.addItem(menuId, body).pipe(
            tapResponse({
              next: (item: MenuItem) => {
                const menus = store.menus().map((m) => {
                  if (m.id !== menuId) return m;
                  const categories = m.categories.map((c) =>
                    c.id === categoryId ? { ...c, items: [...c.items, item] } : c,
                  );
                  return { ...m, categories };
                });
                patchState(store, { menus });
              },
              error: (err: unknown) => {
                const msg = extractErrorMessage(err);
                patchState(store, { error: msg });
                snackBar.open(msg, 'Dismiss', { duration: 5000 });
              },
            }),
          );
        }),
      ),
    ),

    deleteItem: rxMethod<{ menuId: string; itemId: string; categoryId: string }>(
      pipe(
        switchMap(({ menuId, itemId, categoryId }) => {
          return menusService.deleteItem(menuId, itemId).pipe(
            tapResponse({
              next: () => {
                const menus = store.menus().map((m) => {
                  if (m.id !== menuId) return m;
                  const categories = m.categories.map((c) =>
                    c.id === categoryId
                      ? { ...c, items: c.items.filter((i) => i.id !== itemId) }
                      : c,
                  );
                  return { ...m, categories };
                });
                patchState(store, { menus });
              },
              error: (err: unknown) => {
                const msg = extractErrorMessage(err);
                patchState(store, { error: msg });
                snackBar.open(msg, 'Dismiss', { duration: 5000 });
              },
            }),
          );
        }),
      ),
    ),

    selectMenu(menu: Menu | null): void {
      patchState(store, { selectedMenu: menu });
    },

    clearError(): void {
      patchState(store, { error: null });
    },
  })),
);

export type MenusStoreType = InstanceType<typeof MenusStore>;
