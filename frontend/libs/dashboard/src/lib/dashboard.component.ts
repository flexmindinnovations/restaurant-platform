import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressBarModule } from '@angular/material/progress-bar';

import { PageHeader } from '@app/shared';
import { DashboardStore } from './dashboard.store';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    MatIconModule,
    MatButtonModule,
    MatProgressBarModule,
    PageHeader,
  ],
  template: `
    <app-page-header
      title="Dashboard"
      subtitle="Platform overview and key metrics"
    >
      <button mat-stroked-button (click)="refreshData()" class="refresh-btn">
        <mat-icon>refresh</mat-icon>
        Refresh
      </button>
    </app-page-header>

    @if (store.loading()) {
      <mat-progress-bar mode="indeterminate" class="loading-bar" />
    }

    <!-- KPI Grid -->
    <section class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-label">Total Orders</span>
          <div class="kpi-icon-box kpi-icon--blue">
            <mat-icon>shopping_bag</mat-icon>
          </div>
        </div>
        <div class="kpi-value">{{ store.kpis().orders.value }}</div>
        <div class="kpi-trend" [class.kpi-trend--up]="store.kpis().orders.isPositive"
             [class.kpi-trend--down]="!store.kpis().orders.isPositive">
          <mat-icon class="trend-icon">{{ store.kpis().orders.isPositive ? 'trending_up' : 'trending_down' }}</mat-icon>
          <span>{{ store.kpis().orders.change }}</span>
          <span class="trend-period">vs last period</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-label">Revenue</span>
          <div class="kpi-icon-box kpi-icon--green">
            <mat-icon>attach_money</mat-icon>
          </div>
        </div>
        <div class="kpi-value">{{ store.kpis().revenue.value }}</div>
        <div class="kpi-trend" [class.kpi-trend--up]="store.kpis().revenue.isPositive"
             [class.kpi-trend--down]="!store.kpis().revenue.isPositive">
          <mat-icon class="trend-icon">{{ store.kpis().revenue.isPositive ? 'trending_up' : 'trending_down' }}</mat-icon>
          <span>{{ store.kpis().revenue.change }}</span>
          <span class="trend-period">vs last period</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-label">Active Partners</span>
          <div class="kpi-icon-box kpi-icon--violet">
            <mat-icon>storefront</mat-icon>
          </div>
        </div>
        <div class="kpi-value">{{ store.kpis().partners.value }}</div>
        <div class="kpi-trend" [class.kpi-trend--up]="store.kpis().partners.isPositive"
             [class.kpi-trend--down]="!store.kpis().partners.isPositive">
          <mat-icon class="trend-icon">{{ store.kpis().partners.isPositive ? 'trending_up' : 'trending_down' }}</mat-icon>
          <span>{{ store.kpis().partners.change }}</span>
          <span class="trend-period">vs last period</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-label">New Users</span>
          <div class="kpi-icon-box kpi-icon--amber">
            <mat-icon>person_add</mat-icon>
          </div>
        </div>
        <div class="kpi-value">{{ store.kpis().users.value }}</div>
        <div class="kpi-trend" [class.kpi-trend--up]="store.kpis().users.isPositive"
             [class.kpi-trend--down]="!store.kpis().users.isPositive">
          <mat-icon class="trend-icon">{{ store.kpis().users.isPositive ? 'trending_up' : 'trending_down' }}</mat-icon>
          <span>{{ store.kpis().users.change }}</span>
          <span class="trend-period">vs last period</span>
        </div>
      </div>
    </section>

    <!-- Charts row -->
    <section class="charts-grid">
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">Orders Trend</h3>
          <span class="chart-period">Last 7 days</span>
        </div>
        <div class="chart-body">
          <svg viewBox="0 0 300 80" class="sparkline" preserveAspectRatio="none">
            <defs>
              <linearGradient id="sparkGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="var(--color-primary)" stop-opacity="0.15"/>
                <stop offset="100%" stop-color="var(--color-primary)" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <path d="M0,60 L50,45 L100,30 L150,40 L200,15 L250,0 L300,8 L300,80 L0,80Z" fill="url(#sparkGrad)"/>
            <polyline points="0,60 50,45 100,30 150,40 200,15 250,0 300,8"
              fill="none" stroke="var(--color-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <div class="chart-labels">
            @for (pt of store.ordersTrend(); track pt.label) {
              <span>{{ pt.label }}</span>
            }
          </div>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">Revenue Trend</h3>
          <span class="chart-period">Last 7 days</span>
        </div>
        <div class="chart-body">
          <svg viewBox="0 0 300 80" class="sparkline" preserveAspectRatio="none">
            <defs>
              <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="var(--color-accent)" stop-opacity="0.15"/>
                <stop offset="100%" stop-color="var(--color-accent)" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <path d="M0,65 L50,48 L100,35 L150,45 L200,18 L250,0 L300,6 L300,80 L0,80Z" fill="url(#revGrad)"/>
            <polyline points="0,65 50,48 100,35 150,45 200,18 250,0 300,6"
              fill="none" stroke="var(--color-accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <div class="chart-labels">
            @for (pt of store.revenueTrend(); track pt.label) {
              <span>{{ pt.label }}</span>
            }
          </div>
        </div>
      </div>
    </section>

    <!-- Recent orders -->
    <section class="recent-section">
      <div class="section-card">
        <div class="section-header">
          <h3 class="section-title">Recent Orders</h3>
          <span class="section-subtitle">Latest 5</span>
        </div>
        @if (store.recentOrders().length > 0) {
          <table class="data-table">
            <thead>
              <tr>
                <th>Order</th>
                <th>Customer</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              @for (order of store.recentOrders(); track order.id) {
                <tr>
                  <td><code class="order-id">#{{ order.id }}</code></td>
                  <td class="cell-name">{{ order.customer }}</td>
                  <td class="cell-amount">\${{ order.amount }}</td>
                  <td>
                    <span class="status-pill" [class]="'status--' + order.status.toLowerCase()">
                      {{ order.status }}
                    </span>
                  </td>
                  <td class="cell-time">{{ order.time }}</td>
                </tr>
              }
            </tbody>
          </table>
        } @else {
          <div class="empty-state">
            <mat-icon>inbox</mat-icon>
            <p>No recent orders</p>
          </div>
        }
      </div>
    </section>
  `,
  styles: `
    :host { display: block; }

    .refresh-btn {
      font-size: 13px;
      mat-icon { font-size: 18px; width: 18px; height: 18px; }
    }

    .loading-bar {
      margin-bottom: 16px;
      border-radius: 2px;
    }

    /* ── KPI Grid ───────────────────────────── */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-bottom: 24px;
    }

    .kpi-card {
      background: var(--color-surface-1);
      border: 1px solid var(--color-border);
      border-radius: 12px;
      padding: 16px;
      transition: box-shadow 150ms ease;

      &:hover {
        box-shadow: var(--shadow-md);
      }
    }

    .kpi-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }

    .kpi-label {
      font-size: 13px;
      font-weight: 500;
      color: var(--color-text-secondary);
    }

    .kpi-icon-box {
      width: 36px;
      height: 36px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;

      mat-icon {
        font-size: 20px;
        width: 20px;
        height: 20px;
      }

      &.kpi-icon--blue {
        background: #eff6ff;
        color: #2563eb;
      }
      &.kpi-icon--green {
        background: #f0fdf4;
        color: #16a34a;
      }
      &.kpi-icon--violet {
        background: #f5f3ff;
        color: #7c3aed;
      }
      &.kpi-icon--amber {
        background: #fffbeb;
        color: #d97706;
      }
    }

    :host-context(.dark) {
      .kpi-icon--blue  { background: rgba(37, 99, 235, 0.12); }
      .kpi-icon--green { background: rgba(22, 163, 74, 0.12); }
      .kpi-icon--violet { background: rgba(124, 58, 237, 0.12); }
      .kpi-icon--amber { background: rgba(217, 119, 6, 0.12); }
    }

    .kpi-value {
      font-size: 28px;
      font-weight: 700;
      color: var(--color-text-primary);
      line-height: 1;
      margin-bottom: 8px;
      font-variant-numeric: tabular-nums;
      letter-spacing: -0.02em;
    }

    .kpi-trend {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 12px;
      font-weight: 500;
    }
    .kpi-trend--up { color: var(--color-success); }
    .kpi-trend--down { color: var(--color-error); }

    .trend-icon {
      font-size: 16px;
      width: 16px;
      height: 16px;
    }

    .trend-period {
      color: var(--color-text-tertiary);
      font-weight: 400;
      margin-left: 2px;
    }

    /* ── Charts ──────────────────────────────── */
    .charts-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
      margin-bottom: 24px;
    }

    .chart-card {
      background: var(--color-surface-1);
      border: 1px solid var(--color-border);
      border-radius: 12px;
      padding: 16px;
    }

    .chart-header {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      margin-bottom: 16px;
    }

    .chart-title {
      margin: 0;
      font-size: 14px;
      font-weight: 600;
      color: var(--color-text-primary);
    }

    .chart-period {
      font-size: 12px;
      color: var(--color-text-tertiary);
    }

    .chart-body {
      position: relative;
    }

    .sparkline {
      width: 100%;
      height: 100px;
      display: block;
    }

    .chart-labels {
      display: flex;
      justify-content: space-between;
      margin-top: 8px;
      font-size: 11px;
      color: var(--color-text-tertiary);
    }

    /* ── Recent orders ───────────────────────── */
    .section-card {
      background: var(--color-surface-1);
      border: 1px solid var(--color-border);
      border-radius: 12px;
      overflow: hidden;
    }

    .section-header {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      padding: 16px;
      border-bottom: 1px solid var(--color-border);
    }

    .section-title {
      margin: 0;
      font-size: 14px;
      font-weight: 600;
      color: var(--color-text-primary);
    }

    .section-subtitle {
      font-size: 12px;
      color: var(--color-text-tertiary);
    }

    .data-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;

      thead {
        background: var(--color-surface-2);

        th {
          padding: 10px 16px;
          text-align: left;
          font-size: 11px;
          font-weight: 600;
          color: var(--color-text-tertiary);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
      }

      tbody tr {
        border-bottom: 1px solid var(--color-border-light);
        transition: background 100ms ease;

        &:last-child { border-bottom: none; }
        &:hover { background: var(--color-surface-2); }

        td {
          padding: 12px 16px;
          color: var(--color-text-primary);
        }
      }
    }

    .order-id {
      font-family: var(--font-mono, monospace);
      font-size: 12px;
      color: var(--color-text-secondary);
      background: var(--color-surface-2);
      padding: 2px 8px;
      border-radius: 4px;
    }

    .cell-name {
      font-weight: 500;
    }

    .cell-amount {
      font-weight: 600;
      font-variant-numeric: tabular-nums;
    }

    .cell-time {
      color: var(--color-text-tertiary);
      font-size: 12px;
    }

    .status-pill {
      display: inline-flex;
      align-items: center;
      padding: 2px 10px;
      border-radius: 9999px;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.3px;

      &.status--completed {
        background: var(--color-success-bg);
        color: var(--color-success);
      }
      &.status--pending {
        background: var(--color-warning-bg);
        color: var(--color-warning);
      }
      &.status--cancelled {
        background: var(--color-error-bg);
        color: var(--color-error);
      }
    }

    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 48px 16px;
      color: var(--color-text-tertiary);

      mat-icon {
        font-size: 40px;
        width: 40px;
        height: 40px;
        margin-bottom: 12px;
        opacity: 0.4;
      }

      p {
        margin: 0;
        font-size: 13px;
      }
    }

    /* ── Responsive ──────────────────────────── */
    @media (max-width: 1280px) {
      .kpi-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }

    @media (max-width: 768px) {
      .kpi-grid {
        grid-template-columns: 1fr;
      }
      .charts-grid {
        grid-template-columns: 1fr;
      }
    }
  `,
})
export class DashboardComponent {
  protected store = inject(DashboardStore);

  refreshData(): void {
    this.store.loadDashboardData();
  }
}
