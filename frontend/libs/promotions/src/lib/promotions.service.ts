import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import { Promotion } from './promotions.model';

@Injectable({ providedIn: 'root' })
export class PromotionsService {
  private readonly http = inject(HttpClient);

  private mapPromotion(p: any): Promotion {
    return {
      id: p.id,
      code: p.code,
      discount_type: p.promotion_type === 'FIXED_AMOUNT' ? 'FIXED' : 'PERCENTAGE',
      discount_value: Number(p.value),
      min_order_value: p.min_order_amount ? Number(p.min_order_amount) : 0,
      start_date: p.valid_from ? new Date(p.valid_from).toISOString().split('T')[0] : '',
      end_date: p.valid_until ? new Date(p.valid_until).toISOString().split('T')[0] : '',
      status: p.status as 'ACTIVE' | 'EXPIRED' | 'PAUSED',
      usage_count: p.total_uses || 0,
      max_usages: p.max_total_uses || null,
      restaurant_id: p.restaurant_id || null,
      restaurant_name: p.restaurant_id ? 'Restaurant Specific' : 'Platform Wide',
      total_discount_amount: 0,
    };
  }

  private mapToRequest(promo: Partial<Promotion>): any {
    return {
      code: promo.code,
      description: '',
      promotion_type: promo.discount_type === 'FIXED' ? 'FIXED_AMOUNT' : 'PERCENTAGE',
      value: promo.discount_value,
      valid_from: promo.start_date ? `${promo.start_date}T00:00:00Z` : new Date().toISOString(),
      valid_until: promo.end_date ? `${promo.end_date}T23:59:59Z` : new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      min_order_amount: promo.min_order_value || 0,
      max_discount_amount: null,
      currency: 'INR',
      max_total_uses: promo.max_usages || null,
      max_uses_per_customer: 1,
      restaurant_id: promo.restaurant_id || null,
    };
  }

  getPromotions(): Observable<Promotion[]> {
    return this.http
      .get<{ data: { items: any[]; total: number } }>('/api/v1/promotions')
      .pipe(map((res) => (res.data.items || []).map((p) => this.mapPromotion(p))));
  }

  createPromotion(promo: Partial<Promotion>): Observable<Promotion[]> {
    const payload = this.mapToRequest(promo);
    return this.http.post<any>('/api/v1/promotions', payload).pipe(
      switchMap(() => this.getPromotions())
    );
  }

  updatePromotion(id: string, updated: Partial<Promotion>): Observable<Promotion[]> {
    return this.getPromotions();
  }

  deletePromotion(id: string): Observable<Promotion[]> {
    return this.http.post<any>(`/api/v1/promotions/${id}/deactivate`, {}).pipe(
      switchMap(() => this.getPromotions())
    );
  }
}
