import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ApiResponse } from '../models/restaurant.model';
import {
  PlatformDashboardResponse,
  RestaurantDashboardResponse,
  RevenueBreakdownResponse,
} from '../models/analytics.model';

const BASE = '/api/v1/analytics';

@Injectable({ providedIn: 'root' })
export class AnalyticsService {
  private readonly http = inject(HttpClient);

  getPlatformDashboard(
    startDate?: string,
    endDate?: string,
  ): Observable<PlatformDashboardResponse> {
    let httpParams = new HttpParams();
    if (startDate) httpParams = httpParams.set('start_date', startDate);
    if (endDate) httpParams = httpParams.set('end_date', endDate);

    return this.http
      .get<ApiResponse<PlatformDashboardResponse>>(`${BASE}/platform`, { params: httpParams })
      .pipe(map((r) => r.data));
  }

  getRestaurantDashboard(
    restaurantId: string,
    startDate?: string,
    endDate?: string,
  ): Observable<RestaurantDashboardResponse> {
    let httpParams = new HttpParams();
    if (startDate) httpParams = httpParams.set('start_date', startDate);
    if (endDate) httpParams = httpParams.set('end_date', endDate);

    return this.http
      .get<
        ApiResponse<RestaurantDashboardResponse>
      >(`${BASE}/restaurant/${restaurantId}/dashboard`, { params: httpParams })
      .pipe(map((r) => r.data));
  }

  getRevenueBreakdown(startDate?: string, endDate?: string): Observable<RevenueBreakdownResponse> {
    let httpParams = new HttpParams();
    if (startDate) httpParams = httpParams.set('start_date', startDate);
    if (endDate) httpParams = httpParams.set('end_date', endDate);

    return this.http
      .get<
        ApiResponse<RevenueBreakdownResponse>
      >(`${BASE}/revenue-breakdown`, { params: httpParams })
      .pipe(map((r) => r.data));
  }
}
