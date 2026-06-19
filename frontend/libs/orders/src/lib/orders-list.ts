import {
  ChangeDetectionStrategy,
  Component,
  inject,
  OnInit,
} from '@angular/core';
import { DatePipe, SlicePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatBadgeModule } from '@angular/material/badge';
import { PageHeader } from '../../../shared/src/lib/page-header';
import { StatusBadge } from '../../../shared/src/lib/status-badge';
import { EmptyState } from '../../../shared/src/lib/empty-state';
import { OrderStatus } from '@app/api-client';
import { OrdersStore } from './orders.store';
import { OrderDetail } from './order-detail';

const STATUS_TABS: Array<{ label: string; value: OrderStatus | 'ALL' }> = [
  { label: 'All', value: 'ALL' },
  { label: 'Pending',      value: 'PENDING' },
  { label: 'Confirmed',    value: 'CONFIRMED' },
  { label: 'Preparing',    value: 'PREPARING' },
  { label: 'Ready',        value: 'READY' },
  { label: 'Out for Delivery', value: 'OUT_FOR_DELIVERY' },
  { label: 'Delivered',    value: 'DELIVERED' },
  { label: 'Completed',    value: 'COMPLETED' },
  { label: 'Cancelled',    value: 'CANCELLED' },
];

@Component({
  selector: 'app-orders-list',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    // RouterLink,
    DatePipe,
    // CurrencyPipe,
    SlicePipe,
    FormsModule,
    MatTableModule,
    MatPaginatorModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatProgressBarModule,
    MatTooltipModule,
    MatBadgeModule,
    PageHeader,
    StatusBadge,
    EmptyState,
    OrderDetail,
  ],
  template: `
    <app-page-header title="Orders" subtitle="View and manage all customer orders">
    </app-page-header>

    <!-- Status filter tabs -->
    <mat-chip-listbox [ngModel]="store.statusFilter()" (ngModelChange)="onStatusFilter($event)"
      class="status-tabs" aria-label="Filter orders by status">
      @for (tab of statusTabs; track tab.value) {
        <mat-chip-option [value]="tab.value" class="status-tab">{{ tab.label }}</mat-chip-option>
      }
    </mat-chip-listbox>

    @if (store.loading()) {
      <mat-progress-bar mode="indeterminate" style="margin-top:8px" />
    }

    <div class="layout-wrapper" [class.with-panel]="store.selectedOrder()">
      <!-- Table -->
      <div class="table-container mat-elevation-z1">
        @if (!store.loading() && !store.hasResults()) {
          <app-empty-state icon="receipt_long" title="No orders found"
            message="There are no orders matching this filter." />
        } @else {
          <table mat-table [dataSource]="store.orders()" class="full-width">
            <!-- Order # -->
            <ng-container matColumnDef="order_number">
              <th mat-header-cell *matHeaderCellDef>Order #</th>
              <td mat-cell *matCellDef="let o">
                <span class="order-number">{{ o.order_number }}</span>
              </td>
            </ng-container>

            <!-- Status -->
            <ng-container matColumnDef="status">
              <th mat-header-cell *matHeaderCellDef>Status</th>
              <td mat-cell *matCellDef="let o">
                <app-status-badge [status]="o.status" />
              </td>
            </ng-container>

            <!-- Restaurant -->
            <ng-container matColumnDef="restaurant">
              <th mat-header-cell *matHeaderCellDef>Restaurant</th>
              <td mat-cell *matCellDef="let o">{{ o.restaurant_id | slice:0:8 }}…</td>
            </ng-container>

            <!-- Total -->
            <ng-container matColumnDef="total">
              <th mat-header-cell *matHeaderCellDef>Total</th>
              <td mat-cell *matCellDef="let o">
                <strong>{{ o.total_currency }} {{ o.total_amount }}</strong>
              </td>
            </ng-container>

            <!-- Date -->
            <ng-container matColumnDef="placed_at">
              <th mat-header-cell *matHeaderCellDef>Placed</th>
              <td mat-cell *matCellDef="let o">{{ o.placed_at | date:'short' }}</td>
            </ng-container>

            <!-- Actions -->
            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef></th>
              <td mat-cell *matCellDef="let o" (click)="$event.stopPropagation()">
                @if (o.status === 'PENDING') {
                  <button mat-icon-button color="primary"
                    (click)="onConfirm(o.id)" matTooltip="Confirm order">
                    <mat-icon>check_circle</mat-icon>
                  </button>
                }
                @if (o.status !== 'CANCELLED' && o.status !== 'COMPLETED') {
                  <button mat-icon-button color="warn"
                    (click)="onCancel(o.id)" matTooltip="Cancel order">
                    <mat-icon>cancel</mat-icon>
                  </button>
                }
              </td>
            </ng-container>

            <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
            <tr mat-row *matRowDef="let row; columns: displayedColumns"
              class="table-row"
              [class.selected-row]="store.selectedOrder()?.id === row.id"
              (click)="onRowClick(row.id)">
            </tr>
          </table>

          <mat-paginator
            [length]="store.total()"
            [pageSize]="20"
            [pageSizeOptions]="[10, 20, 50]"
            (page)="onPage($event)"
            aria-label="Orders pagination">
          </mat-paginator>
        }
      </div>

      <!-- Detail panel -->
      @if (store.selectedOrder()) {
        <div class="detail-panel mat-elevation-z2">
          <app-order-detail (closed)="store.selectOrder(null)" />
        </div>
      }
    </div>
  `,
  styles: `
    .status-tabs {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 16px;
    }
    .layout-wrapper {
      display: grid;
      grid-template-columns: 1fr;
      gap: 16px;
      transition: grid-template-columns 0.3s ease;
    }
    .layout-wrapper.with-panel {
      grid-template-columns: 1fr 400px;
    }
    .table-container {
      border-radius: 8px;
      overflow: hidden;
      background: var(--mat-sys-surface, #fff);
    }
    .full-width { width: 100%; }
    .table-row { cursor: pointer; transition: background 0.15s; }
    .table-row:hover { background: var(--mat-sys-surface-variant, #f5f5f5); }
    .selected-row { background: var(--mat-sys-primary-container, #fff3e0) !important; }
    .order-number { font-family: monospace; font-weight: 600; }
    .detail-panel {
      border-radius: 8px;
      background: var(--mat-sys-surface, #fff);
      height: fit-content;
      max-height: calc(100vh - 160px);
      overflow-y: auto;
      position: sticky;
      top: 24px;
    }
  `,
})
export class OrdersList implements OnInit {
  protected readonly store = inject(OrdersStore);
  protected readonly statusTabs = STATUS_TABS;
  protected readonly displayedColumns = ['order_number', 'status', 'restaurant', 'total', 'placed_at', 'actions'];

  ngOnInit(): void {
    this.store.loadOrders();
  }

  onStatusFilter(status: OrderStatus | 'ALL'): void {
    this.store.setStatusFilter(status);
    this.store.loadOrders();
  }

  onPage(event: PageEvent): void {
    this.store.setPage(event.pageIndex);
    this.store.loadOrders();
  }

  onRowClick(id: string): void {
    if (this.store.selectedOrder()?.id === id) {
      this.store.selectOrder(null);
    } else {
      this.store.loadOrder(id);
    }
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
