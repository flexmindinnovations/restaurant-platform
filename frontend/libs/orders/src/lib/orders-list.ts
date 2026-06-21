import {
  ChangeDetectionStrategy,
  Component,
  inject,
  OnInit,
  OnDestroy,
  effect,
} from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PageEvent } from '@angular/material/paginator';
import { MatButtonModule } from '@angular/material/button';
import { LucideCircleCheck, LucideBan } from '@lucide/angular';
import { MatChipsModule } from '@angular/material/chips';

import { MatTooltipModule } from '@angular/material/tooltip';
import { MatBadgeModule } from '@angular/material/badge';
import { PageHeader } from '../../../shared/src/lib/page-header';
import { HeaderService } from '@app/shared';
import { StatusBadge } from '../../../shared/src/lib/status-badge';
import { EmptyState } from '../../../shared/src/lib/empty-state';
import { OrderStatus } from '@app/api-client';
import { DatatableComponent, DatatableCellDirective, DatatableColumn } from '@app/design-system';
import { OrdersStore } from './orders.store';
import { OrderDetail } from './order-detail';

const STATUS_TABS: Array<{ label: string; value: OrderStatus | 'ALL' }> = [
  { label: 'All', value: 'ALL' },
  { label: 'Pending', value: 'PENDING' },
  { label: 'Confirmed', value: 'CONFIRMED' },
  { label: 'Preparing', value: 'PREPARING' },
  { label: 'Ready', value: 'READY' },
  { label: 'Out for Delivery', value: 'OUT_FOR_DELIVERY' },
  { label: 'Delivered', value: 'DELIVERED' },
  { label: 'Completed', value: 'COMPLETED' },
  { label: 'Cancelled', value: 'CANCELLED' },
];

@Component({
  selector: 'app-orders-list',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    DatePipe,
    FormsModule,
    MatButtonModule,
    MatChipsModule,
    MatTooltipModule,
    MatBadgeModule,
    LucideCircleCheck,
    LucideBan,
    PageHeader,
    StatusBadge,
    EmptyState,
    OrderDetail,
    DatatableComponent,
    DatatableCellDirective,
  ],
  template: `
    <app-page-header title="Orders" subtitle="View and manage all customer orders">
    </app-page-header>

    <!-- Status filter tabs -->
    <mat-chip-listbox
      [ngModel]="store.statusFilter()"
      (ngModelChange)="onStatusFilter($event)"
      class="status-tabs"
      aria-label="Filter orders by status"
    >
      @for (tab of statusTabs; track tab.value) {
        <mat-chip-option [value]="tab.value" class="status-tab">{{ tab.label }}</mat-chip-option>
      }
    </mat-chip-listbox>

    <div class="layout-wrapper" [class.with-panel]="store.selectedOrder()">
      <!-- Table -->
      <div class="table-wrapper-container">
        @if (!store.loading() && !store.hasResults()) {
          <app-empty-state
            icon="receipt"
            title="No orders found"
            message="There are no orders matching this filter."
          />
        } @else {
          <app-datatable
            [dataSource]="store.orders()"
            [columns]="columns"
            [total]="store.total()"
            [pageSize]="10"
            [selectedRowId]="store.selectedOrder()?.id"
            [loading]="store.loading()"
            selectedRowClass="selected-row"
            (pageChange)="onPage($event)"
            (rowClick)="onRowClick($event)"
            paginatorAriaLabel="Orders pagination"
          >
            <!-- Order # -->
            <ng-template appDatatableCell="order_number" let-row>
              <span class="order-number">{{ row.order_number }}</span>
            </ng-template>

            <!-- Status -->
            <ng-template appDatatableCell="status" let-row>
              <app-status-badge [status]="row.status" />
            </ng-template>



            <!-- Total -->
            <ng-template appDatatableCell="total" let-row>
              <strong>{{ row.total_currency }} {{ row.total_amount }}</strong>
            </ng-template>

            <!-- Date -->
            <ng-template appDatatableCell="placed_at" let-row>
              {{ row.placed_at | date: 'short' }}
            </ng-template>

            <!-- Actions -->
            <ng-template appDatatableCell="actions" let-row>
              @if (row.status === 'PENDING') {
                <button
                  mat-icon-button
                  (click)="onConfirm(row.id)"
                  matTooltip="Confirm order"
                  aria-label="Confirm order"
                >
                  <svg lucideCircleCheck [size]="16" style="color: var(--color-success)"></svg>
                </button>
              }
              @if (row.status !== 'CANCELLED' && row.status !== 'COMPLETED') {
                <button
                  mat-icon-button
                  (click)="onCancel(row.id)"
                  matTooltip="Cancel order"
                  aria-label="Cancel order"
                >
                  <svg lucideBan [size]="16" style="color: var(--color-error)"></svg>
                </button>
              }
            </ng-template>
          </app-datatable>
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
    .table-wrapper-container {
      flex: 1;
      min-width: 0;
    }
    .selected-row {
      background: var(--color-orange-bg) !important;
    }
    .order-number {
      font-family: monospace;
      font-weight: 600;
    }
    .detail-panel {
      border-radius: 0;
      background: var(--color-surface-1);
      height: fit-content;
      max-height: calc(100vh - 160px);
      overflow-y: auto;
      position: sticky;
      top: 24px;
    }
  `,
})
export class OrdersList implements OnInit, OnDestroy {
  protected readonly store = inject(OrdersStore);
  private readonly headerService = inject(HeaderService);
  protected readonly statusTabs = STATUS_TABS;

  constructor() {
    effect(() => {
      this.headerService.setLoading(this.store.loading());
    });
  }

  protected readonly columns: DatatableColumn[] = [
    { key: 'order_number', label: 'Order #' },
    { key: 'status', label: 'Status' },
    { key: 'total', label: 'Total' },
    { key: 'placed_at', label: 'Placed' },
    { key: 'actions', label: 'Actions' },
  ];

  ngOnInit(): void {
    this.store.loadOrders();
  }

  ngOnDestroy(): void {
    this.headerService.setLoading(false);
  }

  onStatusFilter(status: OrderStatus | 'ALL'): void {
    this.store.setStatusFilter(status);
    this.store.loadOrders();
  }

  onPage(event: PageEvent): void {
    this.store.setPage(event.pageIndex);
    this.store.loadOrders();
  }

  onRowClick(row: unknown): void {
    const id = (row as { id: string }).id;
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

