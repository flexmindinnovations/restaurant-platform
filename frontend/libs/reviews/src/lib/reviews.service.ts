import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import { Review } from './reviews.model';

@Injectable({ providedIn: 'root' })
export class ReviewsService {
  private readonly http = inject(HttpClient);

  getReviews(): Observable<Review[]> {
    return this.http
      .get<{ data: { items: any[] } }>('/api/v1/reviews')
      .pipe(
        map((res) =>
          (res.data?.items || []).map((r: any) => ({
            id: r.id,
            restaurant_id: r.restaurant_id || '',
            restaurant_name: r.restaurant_name || 'Restaurant Partner',
            customer_name: r.customer_name || 'Customer',
            rating: r.rating,
            comment: r.comment,
            status: r.is_flagged ? 'FLAGGED' : 'APPROVED',
            flagged: r.is_flagged || false,
            created_at: r.created_at,
            owner_reply: r.reply || null,
            sentiment: r.sentiment || 'NEUTRAL',
            tags: [],
          }))
        )
      );
  }

  moderateReview(id: string, status: 'APPROVED' | 'REJECTED' | 'FLAGGED'): Observable<Review[]> {
    let endpoint = `/api/v1/reviews/${id}/flag`;
    let payload: any = { reason: 'Moderated by Admin' };

    if (status === 'APPROVED') {
      endpoint = `/api/v1/reviews/${id}/approve`;
      payload = {};
    } else if (status === 'REJECTED') {
      endpoint = `/api/v1/reviews/${id}/reject`;
      payload = {};
    }

    return this.http.post<any>(endpoint, payload).pipe(
      switchMap(() => this.getReviews())
    );
  }

  submitReply(id: string, reply: string): Observable<Review[]> {
    return this.http
      .post<any>(`/api/v1/reviews/${id}/reply`, { reply })
      .pipe(
        switchMap(() => this.getReviews())
      );
  }
}
