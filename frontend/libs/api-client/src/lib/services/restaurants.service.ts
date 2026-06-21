import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import {
  ApiResponse,
  CreateRestaurantRequest,
  PaginatedResponse,
  Restaurant,
  RestaurantListParams,
  UpdateRestaurantRequest,
} from '../models/restaurant.model';

const BASE = '/api/v1/restaurants';

@Injectable({ providedIn: 'root' })
export class RestaurantsService {
  private readonly http = inject(HttpClient);

  list(params?: RestaurantListParams): Observable<{ items: Restaurant[]; total: number }> {
    let httpParams = new HttpParams();
    if (params?.skip !== undefined) httpParams = httpParams.set('skip', params.skip);
    if (params?.limit !== undefined) httpParams = httpParams.set('limit', params.limit);
    if (params?.search) httpParams = httpParams.set('search', params.search);
    if (params?.is_verified !== undefined)
      httpParams = httpParams.set('is_verified', params.is_verified);

    return this.http
      .get<PaginatedResponse<Restaurant>>(BASE, { params: httpParams })
      .pipe(map((r) => r.data));
  }

  get(id: string): Observable<Restaurant> {
    return this.http.get<ApiResponse<Restaurant>>(`${BASE}/${id}`).pipe(map((r) => r.data));
  }

  create(body: CreateRestaurantRequest): Observable<Restaurant> {
    return this.http.post<ApiResponse<Restaurant>>(BASE, body).pipe(map((r) => r.data));
  }

  update(id: string, body: UpdateRestaurantRequest): Observable<Restaurant> {
    return this.http.patch<ApiResponse<Restaurant>>(`${BASE}/${id}`, body).pipe(map((r) => r.data));
  }

  verify(id: string): Observable<void> {
    return this.http.post<void>(`/api/v1/admin/restaurants/${id}/verify`, {});
  }
}
