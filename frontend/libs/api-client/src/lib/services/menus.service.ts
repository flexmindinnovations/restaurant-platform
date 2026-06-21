import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import {
  Category,
  CreateCategoryRequest,
  CreateMenuItemRequest,
  CreateMenuRequest,
  Menu,
  MenuListParams,
  MenuItem,
  UpdateCategoryRequest,
  UpdateMenuItemRequest,
  UpdateMenuRequest,
} from '../models/menu.model';
import { ApiResponse } from '../models/restaurant.model';

const BASE = '/api/v1/menus';

interface ListResponse<T> {
  data: { items: T[]; total: number };
}

@Injectable({ providedIn: 'root' })
export class MenusService {
  private readonly http = inject(HttpClient);

  list(params?: MenuListParams): Observable<{ items: Menu[]; total: number }> {
    let httpParams = new HttpParams();
    if (params?.restaurant_id) httpParams = httpParams.set('restaurant_id', params.restaurant_id);
    if (params?.skip !== undefined) httpParams = httpParams.set('skip', params.skip);
    if (params?.limit !== undefined) httpParams = httpParams.set('limit', params.limit);

    return this.http.get<ListResponse<Menu>>(BASE, { params: httpParams }).pipe(map((r) => r.data));
  }

  get(id: string): Observable<Menu> {
    return this.http.get<ApiResponse<Menu>>(`${BASE}/${id}`).pipe(map((r) => r.data));
  }

  create(body: CreateMenuRequest): Observable<Menu> {
    return this.http.post<ApiResponse<Menu>>(BASE, body).pipe(map((r) => r.data));
  }

  update(id: string, body: UpdateMenuRequest): Observable<Menu> {
    return this.http.patch<ApiResponse<Menu>>(`${BASE}/${id}`, body).pipe(map((r) => r.data));
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${BASE}/${id}`);
  }

  activate(id: string): Observable<Menu> {
    return this.update(id, { is_active: true });
  }

  deactivate(id: string): Observable<Menu> {
    return this.update(id, { is_active: false });
  }

  // Categories
  addCategory(menuId: string, body: CreateCategoryRequest): Observable<Category> {
    return this.http
      .post<ApiResponse<Category>>(`${BASE}/${menuId}/categories`, body)
      .pipe(map((r) => r.data));
  }

  updateCategory(
    _menuId: string,
    categoryId: string,
    body: UpdateCategoryRequest,
  ): Observable<Category> {
    return this.http
      .patch<ApiResponse<Category>>(`${BASE}/categories/${categoryId}`, body)
      .pipe(map((r) => r.data));
  }

  deleteCategory(_menuId: string, categoryId: string): Observable<void> {
    return this.http.delete<void>(`${BASE}/categories/${categoryId}`);
  }

  // Items
  addItem(menuId: string, body: CreateMenuItemRequest): Observable<MenuItem> {
    return this.http
      .post<ApiResponse<MenuItem>>(`${BASE}/${menuId}/items`, body)
      .pipe(map((r) => r.data));
  }

  updateItem(_menuId: string, itemId: string, body: UpdateMenuItemRequest): Observable<MenuItem> {
    return this.http
      .patch<ApiResponse<MenuItem>>(`${BASE}/items/${itemId}`, body)
      .pipe(map((r) => r.data));
  }

  deleteItem(_menuId: string, itemId: string): Observable<void> {
    return this.http.delete<void>(`${BASE}/items/${itemId}`);
  }
}
