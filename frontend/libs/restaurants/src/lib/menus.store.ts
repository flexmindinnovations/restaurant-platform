import { inject } from '@angular/core';
import { signalStore, withState, withMethods, patchState } from '@ngrx/signals';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { tapResponse } from '@ngrx/operators';
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

  withMethods((store, menusService = inject(MenusService)) => ({
    loadMenus: rxMethod<string>(
      pipe(
        switchMap((restaurantId) => {
          patchState(store, { loading: true, error: null, restaurantId });
          return menusService.list({ restaurant_id: restaurantId }).pipe(
            tapResponse({
              next: (r) =>
                patchState(store, { menus: r.items, total: r.total, loading: false }),
              error: (err: unknown) =>
                patchState(store, { error: String(err), loading: false }),
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
              next: (m) => patchState(store, { selectedMenu: m, loading: false }),
              error: (err: unknown) =>
                patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    createMenu: rxMethod<CreateMenuRequest>(
      pipe(
        switchMap((body) => {
          patchState(store, { loading: true, error: null });
          return menusService.create(body).pipe(
            tapResponse({
              next: (m) =>
                patchState(store, { menus: [...store.menus(), m], loading: false }),
              error: (err: unknown) =>
                patchState(store, { error: String(err), loading: false }),
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
                const menus = store
                  .menus()
                  .map((m) => (m.id === id ? updated : m));
                patchState(store, {
                  menus,
                  selectedMenu:
                    store.selectedMenu()?.id === id ? updated : store.selectedMenu(),
                });
              },
              error: (err: unknown) => patchState(store, { error: String(err) }),
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
              error: (err: unknown) => patchState(store, { error: String(err) }),
            }),
          );
        }),
      ),
    ),

    publishMenu: rxMethod<string>(
      pipe(
        switchMap((id) => {
          return menusService.publish(id).pipe(
            tapResponse({
              next: (updated) => {
                const menus = store.menus().map((m) => (m.id === id ? updated : m));
                patchState(store, { menus });
              },
              error: (err: unknown) => patchState(store, { error: String(err) }),
            }),
          );
        }),
      ),
    ),

    unpublishMenu: rxMethod<string>(
      pipe(
        switchMap((id) => {
          return menusService.unpublish(id).pipe(
            tapResponse({
              next: (updated) => {
                const menus = store.menus().map((m) => (m.id === id ? updated : m));
                patchState(store, { menus });
              },
              error: (err: unknown) => patchState(store, { error: String(err) }),
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
              error: (err: unknown) => patchState(store, { error: String(err) }),
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
              error: (err: unknown) => patchState(store, { error: String(err) }),
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
              error: (err: unknown) => patchState(store, { error: String(err) }),
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
              error: (err: unknown) => patchState(store, { error: String(err) }),
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
