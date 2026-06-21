import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ApiResponse, PaginatedResponse } from '../models/restaurant.model';
import {
  Section,
  CreateSectionRequest,
  UpdateSectionRequest,
  RestaurantTable,
  CreateTableRequest,
  UpdateTableRequest,
  Reservation,
  CreateReservationRequest,
  CancelReservationRequest,
  WaitlistEntry,
  JoinWaitlistRequest,
  FloorPlan,
  AvailableSlot,
  TableListParams,
  ReservationListParams,
  WaitlistListParams,
} from '../models/table.model';

const BASE = '/api/v1/tables';

@Injectable({ providedIn: 'root' })
export class TablesService {
  private readonly http = inject(HttpClient);

  // Sections
  listSections(restaurantId: string, activeOnly = false): Observable<{ items: Section[]; total: number }> {
    const params = new HttpParams()
      .set('restaurant_id', restaurantId)
      .set('active_only', activeOnly);
    return this.http
      .get<ApiResponse<{ items: Section[]; total: number }>>(`${BASE}/sections`, { params })
      .pipe(map((r) => r.data));
  }

  createSection(body: CreateSectionRequest): Observable<Section> {
    return this.http.post<ApiResponse<Section>>(`${BASE}/sections`, body).pipe(map((r) => r.data));
  }

  updateSection(id: string, body: UpdateSectionRequest): Observable<void> {
    return this.http.patch<void>(`${BASE}/sections/${id}`, body);
  }

  deleteSection(id: string): Observable<void> {
    return this.http.delete<void>(`${BASE}/sections/${id}`);
  }

  // Tables
  listTables(params: TableListParams): Observable<{ items: RestaurantTable[]; total: number }> {
    let httpParams = new HttpParams().set('restaurant_id', params.restaurant_id);
    if (params.section_id) httpParams = httpParams.set('section_id', params.section_id);
    if (params.active_only) httpParams = httpParams.set('active_only', params.active_only);
    if (params.skip !== undefined) httpParams = httpParams.set('skip', params.skip);
    if (params.limit !== undefined) httpParams = httpParams.set('limit', params.limit);
    return this.http
      .get<ApiResponse<{ items: RestaurantTable[]; total: number }>>(BASE, { params: httpParams })
      .pipe(map((r) => r.data));
  }

  createTable(body: CreateTableRequest): Observable<RestaurantTable> {
    return this.http.post<ApiResponse<RestaurantTable>>(BASE, body).pipe(map((r) => r.data));
  }

  updateTable(id: string, body: UpdateTableRequest): Observable<void> {
    return this.http.patch<void>(`${BASE}/${id}`, body);
  }

  updateTableStatus(id: string, status: string): Observable<void> {
    return this.http.patch<void>(`${BASE}/${id}/status`, { status });
  }

  deleteTable(id: string): Observable<void> {
    return this.http.delete<void>(`${BASE}/${id}`);
  }

  // Reservations
  listReservations(params: ReservationListParams): Observable<{ items: Reservation[]; total: number }> {
    let httpParams = new HttpParams().set('restaurant_id', params.restaurant_id);
    if (params.reservation_date) httpParams = httpParams.set('reservation_date', params.reservation_date);
    if (params.skip !== undefined) httpParams = httpParams.set('skip', params.skip);
    if (params.limit !== undefined) httpParams = httpParams.set('limit', params.limit);
    return this.http
      .get<ApiResponse<{ items: Reservation[]; total: number }>>(`${BASE}/reservations`, { params: httpParams })
      .pipe(map((r) => r.data));
  }

  getReservation(id: string): Observable<Reservation> {
    return this.http.get<ApiResponse<Reservation>>(`${BASE}/reservations/${id}`).pipe(map((r) => r.data));
  }

  createReservation(body: CreateReservationRequest): Observable<{ id: string }> {
    return this.http.post<ApiResponse<{ id: string }>>(`${BASE}/reservations`, body).pipe(map((r) => r.data));
  }

  confirmReservation(id: string, tableId: string): Observable<void> {
    return this.http.post<void>(`${BASE}/reservations/${id}/confirm`, { table_id: tableId });
  }

  seatReservation(id: string): Observable<void> {
    return this.http.post<void>(`${BASE}/reservations/${id}/seat`, {});
  }

  cancelReservation(id: string, body?: CancelReservationRequest): Observable<void> {
    return this.http.post<void>(`${BASE}/reservations/${id}/cancel`, body || {});
  }

  markNoShow(id: string): Observable<void> {
    return this.http.post<void>(`${BASE}/reservations/${id}/no-show`, {});
  }

  // Waitlist
  listWaitlist(params: WaitlistListParams): Observable<{ items: WaitlistEntry[]; total: number }> {
    let httpParams = new HttpParams().set('restaurant_id', params.restaurant_id);
    if (params.skip !== undefined) httpParams = httpParams.set('skip', params.skip);
    if (params.limit !== undefined) httpParams = httpParams.set('limit', params.limit);
    return this.http
      .get<ApiResponse<{ items: WaitlistEntry[]; total: number }>>(`${BASE}/waitlist`, { params: httpParams })
      .pipe(map((r) => r.data));
  }

  joinWaitlist(body: JoinWaitlistRequest): Observable<{ id: string }> {
    return this.http.post<ApiResponse<{ id: string }>>(`${BASE}/waitlist`, body).pipe(map((r) => r.data));
  }

  notifyWaitlist(entryId: string): Observable<void> {
    return this.http.post<void>(`${BASE}/waitlist/${entryId}/notify`, {});
  }

  seatFromWaitlist(entryId: string, tableId: string): Observable<void> {
    return this.http.post<void>(`${BASE}/waitlist/${entryId}/seat?table_id=${tableId}`, {});
  }

  removeFromWaitlist(entryId: string): Observable<void> {
    return this.http.delete<void>(`${BASE}/waitlist/${entryId}`);
  }
}
