import {
  ChangeDetectionStrategy,
  Component,
  inject,
  OnInit,
  OnDestroy,
  effect,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import {
  LucideRefreshCw,
  LucideCircleAlert,
  LucideShoppingBag,
  LucideIndianRupee,
  LucideStore,
  LucideUserPlus,
  LucideInbox,
  LucideTrendingUp,
  LucideTrendingDown,
} from '@lucide/angular';
import { MatButtonModule } from '@angular/material/button';

import { PageHeader, HeaderService } from '@app/shared';
import { DashboardStore } from './dashboard.store';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    RouterLink,
    MatButtonModule,
    LucideRefreshCw,
    LucideCircleAlert,
    LucideShoppingBag,
    LucideIndianRupee,
    LucideStore,
    LucideUserPlus,
    LucideInbox,
    LucideTrendingUp,
    LucideTrendingDown,
    PageHeader,
  ],
  template: `
    <app-page-header title="Dashboard" subtitle="Platform overview and key metrics">
      <button matButton="filled" (click)="refreshData()">
        <svg lucideRefreshCw [size]="18"></svg>
        <span>Refresh</span>
      </button>
    </app-page-header>

    @if (store.error()) {
      <div class="error-banner">
        <svg lucideCircleAlert [size]="18"></svg>
        <span>{{ store.error() }}</span>
      </div>
    }

    <!-- KPI Grid -->
    <section class="kpi-grid">
      <a class="kpi-card" [routerLink]="'/orders'">
        <div class="kpi-header">
          <span class="kpi-label">Total Orders</span>
          <div class="kpi-icon-box kpi-icon--blue">
            <svg lucideShoppingBag [size]="20"></svg>
          </div>
        </div>
        <div class="kpi-value">{{ store.kpis().orders.value }}</div>
        <div
          class="kpi-trend"
          [class.kpi-trend--up]="store.kpis().orders.isPositive"
          [class.kpi-trend--down]="!store.kpis().orders.isPositive"
        >
          @if (store.kpis().orders.isPositive) {
            <svg lucideTrendingUp class="trend-icon" [size]="16"></svg>
          } @else {
            <svg lucideTrendingDown class="trend-icon" [size]="16"></svg>
          }
          <span>{{ store.kpis().orders.change }}</span>
          <span class="trend-period">vs last period</span>
        </div>
      </a>

      <a class="kpi-card" [routerLink]="'/analytics'">
        <div class="kpi-header">
          <span class="kpi-label">Revenue</span>
          <div class="kpi-icon-box kpi-icon--green">
            <svg lucideIndianRupee [size]="20"></svg>
          </div>
        </div>
        <div class="kpi-value">{{ store.kpis().revenue.value }}</div>
        <div
          class="kpi-trend"
          [class.kpi-trend--up]="store.kpis().revenue.isPositive"
          [class.kpi-trend--down]="!store.kpis().revenue.isPositive"
        >
          @if (store.kpis().revenue.isPositive) {
            <svg lucideTrendingUp class="trend-icon" [size]="16"></svg>
          } @else {
            <svg lucideTrendingDown class="trend-icon" [size]="16"></svg>
          }
          <span>{{ store.kpis().revenue.change }}</span>
          <span class="trend-period">vs last period</span>
        </div>
      </a>

      <a class="kpi-card" [routerLink]="'/restaurants'">
        <div class="kpi-header">
          <span class="kpi-label">Active Partners</span>
          <div class="kpi-icon-box kpi-icon--violet">
            <svg lucideStore [size]="20"></svg>
          </div>
        </div>
        <div class="kpi-value">{{ store.kpis().partners.value }}</div>
        <div
          class="kpi-trend"
          [class.kpi-trend--up]="store.kpis().partners.isPositive"
          [class.kpi-trend--down]="!store.kpis().partners.isPositive"
        >
          @if (store.kpis().partners.isPositive) {
            <svg lucideTrendingUp class="trend-icon" [size]="16"></svg>
          } @else {
            <svg lucideTrendingDown class="trend-icon" [size]="16"></svg>
          }
          <span>{{ store.kpis().partners.change }}</span>
          <span class="trend-period">vs last period</span>
        </div>
      </a>

      <a class="kpi-card" [routerLink]="'/users'">
        <div class="kpi-header">
          <span class="kpi-label">New Users</span>
          <div class="kpi-icon-box kpi-icon--amber">
            <svg lucideUserPlus [size]="20"></svg>
          </div>
        </div>
        <div class="kpi-value">{{ store.kpis().users.value }}</div>
        <div
          class="kpi-trend"
          [class.kpi-trend--up]="store.kpis().users.isPositive"
          [class.kpi-trend--down]="!store.kpis().users.isPositive"
        >
          @if (store.kpis().users.isPositive) {
            <svg lucideTrendingUp class="trend-icon" [size]="16"></svg>
          } @else {
            <svg lucideTrendingDown class="trend-icon" [size]="16"></svg>
          }
          <span>{{ store.kpis().users.change }}</span>
          <span class="trend-period">vs last period</span>
        </div>
      </a>
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
                <stop offset="0%" stop-color="var(--color-primary)" stop-opacity="0.15" />
                <stop offset="100%" stop-color="var(--color-primary)" stop-opacity="0" />
              </linearGradient>
            </defs>
            <path
              d="M0,60 L50,45 L100,30 L150,40 L200,15 L250,0 L300,8 L300,80 L0,80Z"
              fill="url(#sparkGrad)"
            />
            <polyline
              points="0,60 50,45 100,30 150,40 200,15 250,0 300,8"
              fill="none"
              stroke="var(--color-primary)"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
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
                <stop offset="0%" stop-color="var(--color-accent)" stop-opacity="0.15" />
                <stop offset="100%" stop-color="var(--color-accent)" stop-opacity="0" />
              </linearGradient>
            </defs>
            <path
              d="M0,65 L50,48 L100,35 L150,45 L200,18 L250,0 L300,6 L300,80 L0,80Z"
              fill="url(#revGrad)"
            />
            <polyline
              points="0,65 50,48 100,35 150,45 200,18 250,0 300,6"
              fill="none"
              stroke="var(--color-accent)"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
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
                  <td>
                    <code class="order-id">#{{ order.id }}</code>
                  </td>
                  <td class="cell-name">{{ order.customer }}</td>
                  <td class="cell-amount">₹{{ order.amount }}</td>
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
            <svg lucideInbox [size]="40"></svg>
            <p>No recent orders</p>
          </div>
        }
      </div>
    </section>
  `,
  styles: `
    :host {
      display: block;
    }

    .loading-bar {
      margin-bottom: 16px;
      border-radius: 0;
    }

    .error-banner {
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--color-error-bg);
      border: 1px solid var(--color-error);
      border-radius: 0;
      padding: 10px 12px;
      color: var(--color-error);
      font-size: 13px;
      margin-bottom: 20px;
      line-height: 1.4;

      svg {
        flex-shrink: 0;
      }
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
      border-radius: 0;
      padding: 16px;
      cursor: pointer;
      text-decoration: none;
      display: block;
      transition:
        box-shadow 150ms ease,
        transform 150ms ease;

      &:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
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
      border-radius: 0;
      display: flex;
      align-items: center;
      justify-content: center;

      &.kpi-icon--blue {
        background: var(--color-info-bg);
        color: var(--color-info);
      }
      &.kpi-icon--green {
        background: var(--color-success-bg);
        color: var(--color-success);
      }
      &.kpi-icon--violet {
        background: var(--color-accent-subtle);
        color: var(--color-accent);
      }
      &.kpi-icon--amber {
        background: var(--color-warning-bg);
        color: var(--color-warning);
      }
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
    .kpi-trend--up {
      color: var(--color-success);
    }
    .kpi-trend--down {
      color: var(--color-error);
    }

    .trend-icon {
      width: 16px;
      height: 16px;
      vertical-align: middle;
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
      border-radius: 0;
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
      border-radius: 0;
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

        &:last-child {
          border-bottom: none;
        }
        &:hover {
          background: var(--color-surface-2);
        }

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
      border-radius: 0;
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
      border-radius: 0;
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

      svg {
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
export class DashboardComponent implements OnInit, OnDestroy {
  protected store = inject(DashboardStore);
  private readonly headerService = inject(HeaderService);

  constructor() {
    effect(() => {
      this.headerService.setLoading(this.store.loading());
    });
  }

  ngOnInit(): void {
    this.store.loadDashboardData();
  }

  ngOnDestroy(): void {
    this.headerService.setLoading(false);
  }

  refreshData(): void {
    this.store.loadDashboardData();
  }
}
