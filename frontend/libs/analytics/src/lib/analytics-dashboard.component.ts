import { ChangeDetectionStrategy, Component, inject, OnInit, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { PageHeader } from '../../../shared/src/lib/page-header';
import { AnalyticsStore } from './analytics.store';

@Component({
  selector: 'app-analytics-dashboard',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    MatCardModule,
    MatTableModule,
    MatIconModule,
    MatButtonModule,
    MatProgressBarModule,
    PageHeader,
  ],
  template: `
    <app-page-header title="Platform Analytics" subtitle="Analyze commission fee revenue, hourly order density, and partner metrics">
      <button mat-flat-button color="primary" (click)="store.loadAnalyticsData()">
        <mat-icon>refresh</mat-icon> Refresh Analytics
      </button>
    </app-page-header>

    @if (store.loading()) {
      <mat-progress-bar mode="indeterminate" class="mb-4" />
    }

    <!-- Analytics Charts Grid -->
    <div class="analytics-grid">
      <!-- Commission Trend Chart -->
      <mat-card appearance="outlined" class="chart-card">
        <mat-card-header>
          <mat-card-title>Platform Commission Trend (10%)</mat-card-title>
        </mat-card-header>
        <mat-card-content class="chart-content">
          <div class="svg-container">
            <svg viewBox="0 0 500 200" class="chart-svg">
              <!-- Grid lines -->
              <line x1="40" y1="20" x2="480" y2="20" class="grid-line" />
              <line x1="40" y1="70" x2="480" y2="70" class="grid-line" />
              <line x1="40" y1="120" x2="480" y2="120" class="grid-line" />
              <line x1="40" y1="170" x2="480" y2="170" class="grid-line" />

              <!-- Y-Axis Labels -->
              <text x="30" y="24" class="axis-label" text-anchor="end">$600</text>
              <text x="30" y="74" class="axis-label" text-anchor="end">$400</text>
              <text x="30" y="124" class="axis-label" text-anchor="end">$200</text>
              <text x="30" y="174" class="axis-label" text-anchor="end">$0</text>

              <!-- Gradient Area fill -->
              <path [attr.d]="commissionAreaPath()" fill="url(#comm-grad)" opacity="0.15" />
              <!-- Stroke Line -->
              <path [attr.d]="commissionLinePath()" fill="none" stroke="#2e7d32" stroke-width="3" stroke-linecap="round" />

              <!-- Dots -->
              @for (pt of commissionPoints(); track pt.label) {
                <g class="point-group">
                  <circle [attr.cx]="pt.cx" [attr.cy]="pt.cy" r="5" fill="#2e7d32" stroke="#fff" stroke-width="2" />
                  <text [attr.x]="pt.cx" y="190" class="axis-label" text-anchor="middle">{{ pt.label }}</text>
                  <text [attr.x]="pt.cx" [attr.y]="pt.cy - 8" class="value-popup" text-anchor="middle">\${{ pt.value }}</text>
                </g>
              }
            </svg>
          </div>
        </mat-card-content>
      </mat-card>

      <!-- Peak Hours Horizontal Bar Chart -->
      <mat-card appearance="outlined" class="chart-card">
        <mat-card-header>
          <mat-card-title>Hourly Order Density (Peak Hours)</mat-card-title>
        </mat-card-header>
        <mat-card-content class="chart-content">
          <div class="horizontal-bars-container">
            @for (bar of peakHourBars(); track bar.label) {
              <div class="horizontal-bar-row">
                <span class="bar-label">{{ bar.label }}</span>
                <div class="bar-track">
                  <div class="bar-fill" [style.width.%]="bar.widthPercentage"></div>
                </div>
                <span class="bar-value font-semibold">{{ bar.value }} orders</span>
              </div>
            }
          </div>
        </mat-card-content>
      </mat-card>
    </div>

    <!-- Restaurant Performance Table -->
    <div class="mt-6">
      <mat-card appearance="outlined">
        <mat-card-header>
          <mat-card-title>Top Bounded Restaurant Performance</mat-card-title>
        </mat-card-header>
        <mat-card-content>
          <table mat-table [dataSource]="store.restaurantPerformance()" class="full-width">
            <!-- Name -->
            <ng-container matColumnDef="name">
              <th mat-header-cell *matHeaderCellDef>Restaurant</th>
              <td mat-cell *matCellDef="let row" class="font-medium">{{ row.name }}</td>
            </ng-container>

            <!-- Orders Count -->
            <ng-container matColumnDef="orders">
              <th mat-header-cell *matHeaderCellDef>Orders Completed</th>
              <td mat-cell *matCellDef="let row">{{ row.orders_count }}</td>
            </ng-container>

            <!-- Rating -->
            <ng-container matColumnDef="rating">
              <th mat-header-cell *matHeaderCellDef>Average Rating</th>
              <td mat-cell *matCellDef="let row">
                <span class="rating-badge">
                  <mat-icon>star</mat-icon> {{ row.rating | number:'1.1-1' }}
                </span>
              </td>
            </ng-container>

            <!-- Gross Revenue -->
            <ng-container matColumnDef="revenue">
              <th mat-header-cell *matHeaderCellDef>Gross Revenue</th>
              <td mat-cell *matCellDef="let row" class="font-semibold">{{ row.revenue | currency }}</td>
            </ng-container>

            <!-- Platform Commission -->
            <ng-container matColumnDef="commission">
              <th mat-header-cell *matHeaderCellDef>Commission (10%)</th>
              <td mat-cell *matCellDef="let row" class="text-green-700 font-medium">
                {{ (row.revenue * 0.1) | currency }}
              </td>
            </ng-container>

            <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
            <tr mat-row *matRowDef="let row; columns: displayedColumns" class="table-row"></tr>
          </table>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: `
    .analytics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
      gap: 16px;
    }
    .chart-card {
      border-radius: 12px;
    }
    .chart-content {
      padding: 16px !important;
    }
    .svg-container {
      position: relative;
      width: 100%;
    }
    .chart-svg {
      width: 100%;
      height: auto;
      display: block;
      overflow: visible;
    }
    .grid-line {
      stroke: var(--mat-sys-outline-variant, #e0e0e0);
      stroke-width: 1;
      stroke-dasharray: 4 4;
    }
    .axis-label {
      font-size: 10px;
      fill: var(--mat-sys-on-surface-variant, #888);
      font-weight: 500;
    }
    .value-popup {
      font-size: 9px;
      fill: #2e7d32;
      font-weight: 600;
      opacity: 0;
      transition: opacity 0.2s;
    }
    .point-group:hover .value-popup {
      opacity: 1;
    }

    /* Horizontal Bar CSS Charts */
    .horizontal-bars-container {
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 8px 0;
    }
    .horizontal-bar-row {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .bar-label {
      width: 130px;
      font-size: 0.85rem;
      font-weight: 500;
      color: var(--mat-sys-on-surface, #333);
    }
    .bar-track {
      flex: 1;
      height: 16px;
      background: var(--mat-sys-outline-variant, #f0f0f0);
      border-radius: 8px;
      overflow: hidden;
    }
    .bar-fill {
      height: 100%;
      background: var(--mat-sys-primary, #e65100);
      border-radius: 8px;
      transition: width 0.8s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .bar-value {
      width: 80px;
      text-align: right;
      font-size: 0.82rem;
      color: var(--mat-sys-on-surface-variant, #666);
    }

    /* Restaurant Performance rating badge */
    .rating-badge {
      display: inline-flex;
      align-items: center;
      gap: 2px;
      background: #fff8e1;
      color: #f57f17;
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 600;
      font-size: 0.8rem;
    }
    .rating-badge mat-icon {
      font-size: 14px;
      width: 14px;
      height: 14px;
    }

    .full-width { width: 100%; }
    .table-row:hover { background: var(--mat-sys-surface-variant, #f5f5f5); }
    .mb-4 { margin-bottom: 16px; }
    .mt-6 { margin-top: 24px; }
  `,
})
export class AnalyticsDashboardComponent implements OnInit {
  protected readonly store = inject(AnalyticsStore);
  protected readonly displayedColumns = ['name', 'orders', 'rating', 'revenue', 'commission'];

  // Calculate SVG line points for commission trend
  protected readonly commissionPoints = computed(() => {
    const data = this.store.commissionTrend();
    if (!data.length) return [];
    const maxVal = Math.max(...data.map(d => d.value));
    const chartHeight = 150;
    const baseHeight = 170;
    const startX = 60;
    const gap = 64;

    return data.map((d, index) => {
      const height = (d.value / maxVal) * chartHeight;
      const cx = startX + index * gap;
      const cy = baseHeight - height;
      return {
        label: d.label,
        value: d.value,
        cx,
        cy,
      };
    });
  });

  protected readonly commissionLinePath = computed(() => {
    const pts = this.commissionPoints();
    if (!pts.length) return '';
    return pts.map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${p.cx} ${p.cy}`).join(' ');
  });

  protected readonly commissionAreaPath = computed(() => {
    const pts = this.commissionPoints();
    if (!pts.length) return '';
    const first = pts[0];
    const last = pts[pts.length - 1];
    return `${this.commissionLinePath()} L ${last.cx} 170 L ${first.cx} 170 Z`;
  });

  // Calculate peak hours percentage width
  protected readonly peakHourBars = computed(() => {
    const data = this.store.peakHours();
    if (!data.length) return [];
    const maxVal = Math.max(...data.map(d => d.value));
    return data.map((d) => ({
      label: d.label,
      value: d.value,
      widthPercentage: (d.value / maxVal) * 100,
    }));
  });

  ngOnInit(): void {
    this.ensureGradientsExist();
    this.store.loadAnalyticsData();
  }

  private ensureGradientsExist(): void {
    if (typeof document === 'undefined') return;
    let svgDefs = document.getElementById('analytics-defs');
    if (!svgDefs) {
      const defsContainer = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      defsContainer.setAttribute('style', 'position: absolute; width: 0; height: 0; overflow: hidden;');
      defsContainer.setAttribute('id', 'analytics-defs');
      defsContainer.innerHTML = `
        <defs>
          <linearGradient id="comm-grad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#2e7d32" stop-opacity="0.4"/>
            <stop offset="100%" stop-color="#2e7d32" stop-opacity="0.0"/>
          </linearGradient>
        </defs>
      `;
      document.body.appendChild(defsContainer);
    }
  }
}
