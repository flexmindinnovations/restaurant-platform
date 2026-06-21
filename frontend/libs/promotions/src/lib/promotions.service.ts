import { Injectable } from '@angular/core';
import { Observable, of, delay } from 'rxjs';
import { Promotion } from './promotions.model';

const MOCK_PROMOTIONS: Promotion[] = [
  {
    id: 'promo-1',
    code: 'WELCOME50',
    discount_type: 'PERCENTAGE',
    discount_value: 50,
    min_order_value: 15.0,
    start_date: '2026-06-01',
    end_date: '2026-12-31',
    status: 'ACTIVE',
    usage_count: 342,
    max_usages: 1000,
    restaurant_id: null,
    restaurant_name: 'Platform Wide',
    total_discount_amount: 1710.0,
  },
  {
    id: 'promo-2',
    code: 'PIZZATIME',
    discount_type: 'FIXED',
    discount_value: 5.0,
    min_order_value: 20.0,
    start_date: '2026-06-10',
    end_date: '2026-07-10',
    status: 'ACTIVE',
    usage_count: 89,
    max_usages: 200,
    restaurant_id: 'rest-2',
    restaurant_name: 'Pizza Suprema',
    total_discount_amount: 445.0,
  },
  {
    id: 'promo-3',
    code: 'FREEBURGER',
    discount_type: 'PERCENTAGE',
    discount_value: 100,
    min_order_value: 30.0,
    start_date: '2026-05-01',
    end_date: '2026-06-15',
    status: 'EXPIRED',
    usage_count: 150,
    max_usages: 150,
    restaurant_id: 'rest-3',
    restaurant_name: 'Burger Palace',
    total_discount_amount: 1200.0,
  },
  {
    id: 'promo-4',
    code: 'WEEKEND10',
    discount_type: 'PERCENTAGE',
    discount_value: 10,
    min_order_value: 10.0,
    start_date: '2026-06-15',
    end_date: '2026-08-31',
    status: 'PAUSED',
    usage_count: 23,
    max_usages: null,
    restaurant_id: null,
    restaurant_name: 'Platform Wide',
    total_discount_amount: 46.5,
  },
];

@Injectable({ providedIn: 'root' })
export class PromotionsService {
  private promotions: Promotion[] = [];

  constructor() {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('quickbite_promotions');
      if (stored) {
        try {
          this.promotions = JSON.parse(stored);
        } catch {
          this.resetMocks();
        }
      } else {
        this.resetMocks();
      }
    } else {
      this.promotions = [...MOCK_PROMOTIONS];
    }
  }

  private resetMocks(): void {
    this.promotions = [...MOCK_PROMOTIONS];
    this.save();
  }

  private save(): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('quickbite_promotions', JSON.stringify(this.promotions));
    }
  }

  getPromotions(): Observable<Promotion[]> {
    return of([...this.promotions]).pipe(delay(200));
  }

  createPromotion(promo: Partial<Promotion>): Observable<Promotion[]> {
    const newPromo: Promotion = {
      id: 'promo-' + Math.random().toString(36).substr(2, 9),
      code: (promo.code || 'COUPON').toUpperCase(),
      discount_type: promo.discount_type || 'PERCENTAGE',
      discount_value: Number(promo.discount_value) || 0,
      min_order_value: Number(promo.min_order_value) || 0,
      start_date: promo.start_date || new Date().toISOString().split('T')[0],
      end_date:
        promo.end_date ||
        new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      status: promo.status || 'ACTIVE',
      usage_count: 0,
      max_usages: promo.max_usages ? Number(promo.max_usages) : null,
      restaurant_id: promo.restaurant_id || null,
      restaurant_name: promo.restaurant_id
        ? promo.restaurant_name || 'Restaurant Specific'
        : 'Platform Wide',
      total_discount_amount: 0,
    };
    this.promotions.unshift(newPromo);
    this.save();
    return of([...this.promotions]).pipe(delay(200));
  }

  updatePromotion(id: string, updated: Partial<Promotion>): Observable<Promotion[]> {
    const idx = this.promotions.findIndex((p) => p.id === id);
    if (idx !== -1) {
      this.promotions[idx] = {
        ...this.promotions[idx],
        ...updated,
        discount_value:
          updated.discount_value !== undefined
            ? Number(updated.discount_value)
            : this.promotions[idx].discount_value,
        min_order_value:
          updated.min_order_value !== undefined
            ? Number(updated.min_order_value)
            : this.promotions[idx].min_order_value,
        max_usages:
          updated.max_usages !== undefined
            ? updated.max_usages
              ? Number(updated.max_usages)
              : null
            : this.promotions[idx].max_usages,
      };
      this.save();
    }
    return of([...this.promotions]).pipe(delay(200));
  }

  deletePromotion(id: string): Observable<Promotion[]> {
    this.promotions = this.promotions.filter((p) => p.id !== id);
    this.save();
    return of([...this.promotions]).pipe(delay(200));
  }
}
