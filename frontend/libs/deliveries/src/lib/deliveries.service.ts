import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, forkJoin } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import { DeliveryPartner, ActiveDelivery } from './deliveries.model';

@Injectable({ providedIn: 'root' })
export class DeliveriesService {
  private readonly http = inject(HttpClient);

  getPartners(): Observable<DeliveryPartner[]> {
    return this.http
      .get<{ data: DeliveryPartner[] }>('/api/v1/partners')
      .pipe(map((res) => res.data || []));
  }

  getActiveDeliveries(): Observable<ActiveDelivery[]> {
    return this.http
      .get<{ data: ActiveDelivery[] }>('/api/v1/delivery-assignments')
      .pipe(map((res) => res.data || []));
  }

  overrideAssignment(
    deliveryId: string,
    partnerId: string | null,
  ): Observable<{ partners: DeliveryPartner[]; deliveries: ActiveDelivery[] }> {
    return this.http
      .post<any>(`/api/v1/delivery-assignments/${deliveryId}/override`, { partner_id: partnerId })
      .pipe(
        switchMap(() =>
          forkJoin({
            partners: this.getPartners(),
            deliveries: this.getActiveDeliveries(),
          })
        )
      );
  }
}
