import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { PaymentTransaction, PaymentListParams } from './payments.model';

@Injectable({ providedIn: 'root' })
export class PaymentsService {
  private readonly http = inject(HttpClient);

  list(params?: PaymentListParams): Observable<{ items: PaymentTransaction[]; total: number }> {
    let httpParams = new HttpParams();
    if (params?.skip !== undefined) httpParams = httpParams.set('skip', params.skip);
    if (params?.limit !== undefined) httpParams = httpParams.set('limit', params.limit);
    if (params?.search) httpParams = httpParams.set('search', params.search);
    if (params?.status && params.status !== 'ALL') httpParams = httpParams.set('status', params.status);

    return this.http
      .get<{ data: { items: PaymentTransaction[]; total: number } }>('/api/v1/admin/payments', { params: httpParams })
      .pipe(map((res) => res.data || { items: [], total: 0 }));
  }

  refund(paymentId: string): Observable<PaymentTransaction> {
    return this.http
      .post<{ data: any }>(`/api/v1/admin/payments/${paymentId}/refund`, { amount: 0 })
      .pipe(
        map(() => ({
          id: paymentId,
          order_id: '',
          customer_name: '',
          amount: 0,
          status: 'REFUNDED',
          payment_method: '',
          created_at: '',
        }))
      );
  }
}
