import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import {
  CancelOrderRequest,
  Order,
  OrderListParams,
  OrderListResponse,
  OrderStatus,
  UpdateOrderStatusRequest,
} from '../models/order.model';
import { ApiResponse } from '../models/restaurant.model';

const BASE = '/api/v1/orders';

interface ListApiResponse {
  data: OrderListResponse;
}

@Injectable({ providedIn: 'root' })
export class OrdersService {
  private readonly http = inject(HttpClient);

  list(params?: OrderListParams): Observable<OrderListResponse> {
    let httpParams = new HttpParams();
    if (params?.status) httpParams = httpParams.set('status', params.status);
    if (params?.restaurant_id) httpParams = httpParams.set('restaurant_id', params.restaurant_id);
    if (params?.skip !== undefined) httpParams = httpParams.set('skip', params.skip);
    if (params?.limit !== undefined) httpParams = httpParams.set('limit', params.limit);

    return this.http.get<ListApiResponse>(BASE, { params: httpParams }).pipe(map((r) => r.data));
  }

  get(id: string): Observable<Order> {
    return this.http.get<ApiResponse<Order>>(`${BASE}/${id}`).pipe(map((r) => r.data));
  }

  confirm(id: string): Observable<void> {
    return this.http.post<void>(`${BASE}/${id}/confirm`, {});
  }

  updateStatus(id: string, status: OrderStatus): Observable<void> {
    const body: UpdateOrderStatusRequest = { status };
    return this.http.post<void>(`${BASE}/${id}/status`, body);
  }

  cancel(id: string, reason: string): Observable<void> {
    const body: CancelOrderRequest = { reason };
    return this.http.post<void>(`${BASE}/${id}/cancel`, body);
  }
}
