import { Injectable } from '@angular/core';
import { Observable, of, delay } from 'rxjs';
import { PaymentTransaction, PaymentListParams, PaymentStatus } from './payments.model';

const MOCK_PAYMENTS: PaymentTransaction[] = [
  {
    id: 'pay-501',
    order_id: 'ord-101',
    customer_name: 'John Doe',
    amount: 42.50,
    status: 'SUCCESS',
    payment_method: 'Visa (•••• 4242)',
    created_at: '2026-06-18T10:15:00Z',
  },
  {
    id: 'pay-502',
    order_id: 'ord-102',
    customer_name: 'Alice Smith',
    amount: 18.90,
    status: 'FAILED',
    payment_method: 'Mastercard (•••• 5555)',
    created_at: '2026-06-18T11:20:00Z',
  },
  {
    id: 'pay-503',
    order_id: 'ord-103',
    customer_name: 'Bob Johnson',
    amount: 65.00,
    status: 'SUCCESS',
    payment_method: 'Apple Pay',
    created_at: '2026-06-18T12:05:00Z',
  },
  {
    id: 'pay-504',
    order_id: 'ord-104',
    customer_name: 'Sarah Connor',
    amount: 112.40,
    status: 'REFUNDED',
    payment_method: 'Visa (•••• 1111)',
    created_at: '2026-06-17T15:30:00Z',
  },
  {
    id: 'pay-505',
    order_id: 'ord-105',
    customer_name: 'David Kim',
    amount: 29.99,
    status: 'SUCCESS',
    payment_method: 'Google Pay',
    created_at: '2026-06-17T18:45:00Z',
  },
];

@Injectable({ providedIn: 'root' })
export class PaymentsService {
  private payments: PaymentTransaction[] = [];

  constructor() {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('quickbite_payments');
      if (stored) {
        try {
          this.payments = JSON.parse(stored);
        } catch {
          this.resetMocks();
        }
      } else {
        this.resetMocks();
      }
    } else {
      this.payments = [...MOCK_PAYMENTS];
    }
  }

  private resetMocks(): void {
    this.payments = [...MOCK_PAYMENTS];
    this.save();
  }

  private save(): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('quickbite_payments', JSON.stringify(this.payments));
    }
  }

  list(params?: PaymentListParams): Observable<{ items: PaymentTransaction[]; total: number }> {
    let filtered = [...this.payments];

    if (params?.search) {
      const q = params.search.toLowerCase();
      filtered = filtered.filter(
        (p) =>
          p.id.toLowerCase().includes(q) ||
          p.order_id.toLowerCase().includes(q) ||
          p.customer_name.toLowerCase().includes(q) ||
          p.payment_method.toLowerCase().includes(q)
      );
    }

    if (params?.status && params.status !== 'ALL') {
      filtered = filtered.filter((p) => p.status === params.status);
    }

    const total = filtered.length;
    const skip = params?.skip ?? 0;
    const limit = params?.limit ?? 10;
    const items = filtered.slice(skip, skip + limit);

    return of({ items, total }).pipe(delay(200));
  }

  refund(paymentId: string): Observable<PaymentTransaction> {
    const tx = this.payments.find((p) => p.id === paymentId);
    if (!tx) throw new Error('Transaction not found');
    if (tx.status !== 'SUCCESS') throw new Error('Only successful transactions can be refunded');

    tx.status = 'REFUNDED';
    this.save();
    return of({ ...tx }).pipe(delay(250));
  }
}
