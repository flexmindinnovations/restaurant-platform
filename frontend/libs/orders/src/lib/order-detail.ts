import { ChangeDetectionStrategy, Component, inject, output } from '@angular/core';
import { DatePipe } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import {
  LucideX,
  LucideCheck,
  LucideBan,
  LucideCircleCheck,
  LucideCircle,
  LucideInfo,
} from '@lucide/angular';
import { MatDividerModule } from '@angular/material/divider';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatListModule } from '@angular/material/list';
import { MatChipsModule } from '@angular/material/chips';
import { StatusBadge } from '../../../shared/src/lib/status-badge';
import { OrdersStore } from './orders.store';
import { Order, OrderStatus } from '@app/api-client';

interface StatusStep {
  status: OrderStatus;
  label: string;
  timestampKey: keyof Order;
}

const STATUS_TIMELINE: StatusStep[] = [
  { status: 'PENDING', label: 'Placed', timestampKey: 'placed_at' },
  { status: 'CONFIRMED', label: 'Confirmed', timestampKey: 'confirmed_at' },
  { status: 'PREPARING', label: 'Preparing', timestampKey: 'preparing_at' },
  { status: 'READY', label: 'Ready for pickup', timestampKey: 'ready_at' },
  { status: 'OUT_FOR_DELIVERY', label: 'Picked up', timestampKey: 'picked_up_at' },
  { status: 'DELIVERED', label: 'Delivered', timestampKey: 'delivered_at' },
];

const STATUS_ORDER: OrderStatus[] = [
  'PENDING',
  'CONFIRMED',
  'PREPARING',
  'READY',
  'OUT_FOR_DELIVERY',
  'DELIVERED',
  'COMPLETED',
];

@Component({
  selector: 'app-order-detail',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    DatePipe,
    MatButtonModule,
    LucideX,
    LucideCheck,
    LucideBan,
    LucideCircleCheck,
    LucideCircle,
    LucideInfo,
    MatDividerModule,
    MatProgressSpinnerModule,
    MatListModule,
    MatChipsModule,
    StatusBadge,
  ],
  template: `
    @if (store.detailLoading()) {
      <div class="center-spinner"><mat-spinner diameter="40" /></div>
    } @else if (store.selectedOrder(); as order) {
      <div class="detail-wrapper">
        <!-- Header -->
        <div class="detail-header">
          <div>
            <h3 class="order-num">Order {{ order.order_number }}</h3>
            <app-status-badge [status]="order.status" />
          </div>
          <button mat-icon-button (click)="closed.emit()" aria-label="Close panel">
            <svg lucideX [size]="18"></svg>
          </button>
        </div>

        <mat-divider />

        <!-- Actions -->
        <div class="actions-bar">
          @if (order.status === 'PENDING') {
            <button mat-flat-button color="primary" (click)="onConfirm(order.id)">
              <svg lucideCheck [size]="18"></svg> Confirm
            </button>
          }
          @if (
            order.status !== 'CANCELLED' &&
            order.status !== 'COMPLETED' &&
            order.status !== 'DELIVERED'
          ) {
            <button mat-stroked-button color="warn" (click)="onCancel(order.id)">
              <svg lucideBan [size]="18"></svg> Cancel
            </button>
          }
        </div>

        <!-- Timeline -->
        <div class="section">
          <h4 class="section-title">Timeline</h4>
          <div class="timeline">
            @for (step of timeline; track step.status) {
              @let ts = getTimestamp(order, step.timestampKey);
              @let isDone = isStatusReached(order.status, step.status);
              <div class="timeline-item" [class.done]="isDone">
                <div class="timeline-dot" [class.done]="isDone">
                  @if (isDone) {
                    <svg lucideCircleCheck class="dot-icon" [size]="16"></svg>
                  } @else {
                    <svg lucideCircle class="dot-icon" [size]="16"></svg>
                  }
                </div>
                <div class="timeline-content">
                  <span class="tl-label">{{ step.label }}</span>
                  @if (ts) {
                    <span class="tl-time">{{ ts | date: 'short' }}</span>
                  }
                </div>
              </div>
            }
            @if (order.status === 'CANCELLED') {
              <div class="timeline-item cancelled">
                <div class="timeline-dot cancelled">
                  <svg lucideBan class="dot-icon" [size]="16"></svg>
                </div>
                <div class="timeline-content">
                  <span class="tl-label">Cancelled</span>
                  @if (order.cancelled_at) {
                    <span class="tl-time">{{ order.cancelled_at | date: 'short' }}</span>
                  }
                  @if (order.cancellation_reason) {
                    <span class="tl-reason">{{ order.cancellation_reason }}</span>
                  }
                </div>
              </div>
            }
          </div>
        </div>

        <mat-divider />

        <!-- Items -->
        <div class="section">
          <h4 class="section-title">Items ({{ order.items.length }})</h4>
          @for (item of order.items; track item.id) {
            <div class="order-item-row">
              <span class="item-qty">×{{ item.quantity }}</span>
              <span class="item-name-col">{{ item.name }}</span>
              <span class="item-price-col"
                >{{ order.subtotal_currency }} {{ item.subtotal_amount }}</span
              >
            </div>
          }
          <mat-divider class="items-divider" />
          <div class="totals">
            <div class="total-row">
              <span>Subtotal</span>
              <span>{{ order.subtotal_currency }} {{ order.subtotal_amount }}</span>
            </div>
            <div class="total-row">
              <span>Delivery fee</span>
              <span>{{ order.delivery_fee_currency }} {{ order.delivery_fee_amount }}</span>
            </div>
            <div class="total-row">
              <span>Tax</span>
              <span>{{ order.tax_currency }} {{ order.tax_amount }}</span>
            </div>
            <div class="total-row total-grand">
              <strong>Total</strong>
              <strong>{{ order.total_currency }} {{ order.total_amount }}</strong>
            </div>
          </div>
        </div>

        <mat-divider />

        <!-- Delivery address -->
        <div class="section">
          <h4 class="section-title">Delivery address</h4>
          <address class="delivery-addr">
            {{ order.delivery_address_street }}<br />
            {{ order.delivery_address_city }}, {{ order.delivery_address_state }}
            {{ order.delivery_address_postal_code }}<br />
            {{ order.delivery_address_country }}
          </address>
          @if (order.delivery_notes) {
            <p class="delivery-notes">
              <svg lucideInfo class="notes-icon" [size]="16"></svg>
              {{ order.delivery_notes }}
            </p>
          }
        </div>
      </div>
    }
  `,
  styles: `
    .center-spinner {
      display: flex;
      justify-content: center;
      padding: 40px;
    }
    .detail-wrapper {
      padding: 16px;
    }
    .detail-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      margin-bottom: 12px;
    }
    .order-num {
      margin: 0 0 6px;
      font-size: 1rem;
      font-weight: 600;
      font-family: monospace;
    }
    .actions-bar {
      display: flex;
      gap: 8px;
      padding: 12px 0;
    }
    .section {
      padding: 12px 0;
    }
    .section-title {
      margin: 0 0 10px;
      font-size: 0.85rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      opacity: 0.6;
    }
    /* Timeline */
    .timeline {
      display: flex;
      flex-direction: column;
      gap: 0;
    }
    .timeline-item {
      display: flex;
      gap: 12px;
      position: relative;
    }
    .timeline-item:not(:last-child)::after {
      content: '';
      position: absolute;
      left: 10px;
      top: 24px;
      bottom: -4px;
      width: 2px;
      background: var(--color-border);
    }
    .timeline-item.done::after {
      background: var(--color-primary);
      opacity: 0.4;
    }
    .timeline-dot {
      width: 24px;
      height: 24px;
      display: flex;
      align-items: flex-start;
      padding-top: 4px;
    }
    .dot-icon {
      font-size: 16px;
      width: 16px;
      height: 16px;
      color: var(--color-border);
    }
    .timeline-dot.done .dot-icon {
      color: var(--color-primary);
    }
    .timeline-dot.cancelled .dot-icon {
      color: var(--color-error);
    }
    .timeline-content {
      padding-bottom: 12px;
    }
    .tl-label {
      display: block;
      font-size: 0.875rem;
      font-weight: 500;
    }
    .tl-time {
      display: block;
      font-size: 0.75rem;
      opacity: 0.6;
    }
    .tl-reason {
      display: block;
      font-size: 0.75rem;
      color: var(--color-error);
      margin-top: 2px;
    }
    /* Items */
    .order-item-row {
      display: grid;
      grid-template-columns: 32px 1fr auto;
      gap: 8px;
      align-items: center;
      padding: 4px 0;
      font-size: 0.875rem;
    }
    .item-qty {
      font-weight: 700;
      opacity: 0.5;
    }
    .item-name-col {
      font-weight: 500;
    }
    .item-price-col {
      font-weight: 600;
    }
    .items-divider {
      margin: 8px 0;
    }
    .totals {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .total-row {
      display: flex;
      justify-content: space-between;
      font-size: 0.875rem;
      opacity: 0.8;
    }
    .total-grand {
      opacity: 1;
      font-size: 1rem;
      margin-top: 4px;
    }
    /* Address */
    address {
      font-style: normal;
      line-height: 1.8;
      font-size: 0.875rem;
    }
    .delivery-notes {
      display: flex;
      align-items: flex-start;
      gap: 6px;
      font-size: 0.8rem;
      opacity: 0.75;
      margin-top: 8px;
    }
    .notes-icon {
      font-size: 16px;
      width: 16px;
      height: 16px;
      margin-top: 2px;
    }
    svg[class*='lucide'] {
      vertical-align: middle;
    }
  `,
})
export class OrderDetail {
  readonly closed = output<void>();

  protected readonly store = inject(OrdersStore);
  protected readonly timeline = STATUS_TIMELINE;

  getTimestamp(order: Order, key: keyof Order): string | null {
    return order[key] as string | null;
  }

  isStatusReached(currentStatus: OrderStatus, checkStatus: OrderStatus): boolean {
    const currentIdx = STATUS_ORDER.indexOf(currentStatus);
    const checkIdx = STATUS_ORDER.indexOf(checkStatus);
    if (currentIdx === -1 || checkIdx === -1) return false;
    return currentIdx >= checkIdx;
  }

  onConfirm(id: string): void {
    this.store.confirmOrder(id);
  }

  onCancel(id: string): void {
    const reason = window.prompt('Cancellation reason:');
    if (reason?.trim()) {
      this.store.cancelOrder({ id, reason: reason.trim() });
    }
  }
}
