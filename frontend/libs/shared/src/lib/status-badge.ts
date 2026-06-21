import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

type StatusVariant = 'success' | 'warning' | 'error' | 'info' | 'neutral';

const STATUS_MAP: Record<string, { label: string; variant: StatusVariant }> = {
  PENDING: { label: 'Pending', variant: 'warning' },
  CONFIRMED: { label: 'Confirmed', variant: 'info' },
  PREPARING: { label: 'Preparing', variant: 'info' },
  READY: { label: 'Ready', variant: 'success' },
  OUT_FOR_DELIVERY: { label: 'Out for Delivery', variant: 'info' },
  DELIVERED: { label: 'Delivered', variant: 'success' },
  COMPLETED: { label: 'Completed', variant: 'success' },
  CANCELLED: { label: 'Cancelled', variant: 'error' },
  VERIFIED: { label: 'Verified', variant: 'success' },
  UNVERIFIED: { label: 'Unverified', variant: 'warning' },
  ACTIVE: { label: 'Active', variant: 'success' },
  INACTIVE: { label: 'Inactive', variant: 'neutral' },
};

@Component({
  selector: 'app-status-badge',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <span class="badge" [class]="'badge--' + variant()">
      {{ label() }}
    </span>
  `,
  styles: `
    .badge {
      display: inline-flex;
      align-items: center;
      padding: 2px 10px;
      border-radius: 0;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.3px;
      line-height: 18px;
      white-space: nowrap;
    }
    .badge--success {
      background: var(--color-success-bg, #f0fdf4);
      color: var(--color-success, #16a34a);
    }
    .badge--warning {
      background: var(--color-warning-bg, #fffbeb);
      color: var(--color-warning, #d97706);
    }
    .badge--error {
      background: var(--color-error-bg, #fef2f2);
      color: var(--color-error, #dc2626);
    }
    .badge--info {
      background: var(--color-info-bg, #eff6ff);
      color: var(--color-info, #2563eb);
    }
    .badge--neutral {
      background: var(--color-surface-2, #f1f5f9);
      color: var(--color-text-tertiary, #94a3b8);
    }
  `,
})
export class StatusBadge {
  readonly status = input.required<string>();

  readonly label = computed(() => STATUS_MAP[this.status()]?.label ?? this.status());
  readonly variant = computed(() => STATUS_MAP[this.status()]?.variant ?? 'neutral');
}
