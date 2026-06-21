import {
  ChangeDetectionStrategy,
  Component,
  inject,
  OnInit,
  OnDestroy,
  effect,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PageEvent } from '@angular/material/paginator';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { LucideSearch, LucideUndo2 } from '@lucide/angular';

import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { PageHeader } from '../../../shared/src/lib/page-header';
import { HeaderService, ConfirmDialog } from '@app/shared';
import { EmptyState } from '../../../shared/src/lib/empty-state';
import { DatatableComponent, DatatableCellDirective, DatatableColumn } from '@app/design-system';
import { PaymentsStore } from './payments.store';
import { PaymentStatus } from './payments.model';

@Component({
  selector: 'app-payments-list',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    FormsModule,
    MatInputModule,
    MatFormFieldModule,
    MatButtonModule,
    MatChipsModule,
    MatDialogModule,
    LucideSearch,
    LucideUndo2,
    MatTooltipModule,
    PageHeader,
    EmptyState,
    DatatableComponent,
    DatatableCellDirective,
  ],
  template: `
    <app-page-header
      title="Payments Ledger"
      subtitle="View transaction history, payment methods, and handle refunds"
    >
    </app-page-header>

    <!-- Filters -->
    <div class="filters-row">
      <mat-form-field appearance="outline" class="search-field" subscriptSizing="dynamic">
        <mat-label>Search transactions</mat-label>
        <svg lucideSearch [size]="18" matIconPrefix></svg>
        <input
          matInput
          [ngModel]="searchValue()"
          (ngModelChange)="onSearch($event)"
          placeholder="Tx ID, Order ID, Customer…"
          id="payment-search"
        />
      </mat-form-field>

      <mat-chip-listbox
        [ngModel]="statusFilter()"
        (ngModelChange)="onStatusFilter($event)"
        class="filter-chips"
        aria-label="Status filter"
      >
        <mat-chip-option value="ALL">All Transactions</mat-chip-option>
        <mat-chip-option value="SUCCESS">Success</mat-chip-option>
        <mat-chip-option value="REFUNDED">Refunded</mat-chip-option>
        <mat-chip-option value="FAILED">Failed</mat-chip-option>
      </mat-chip-listbox>
    </div>

    <!-- Table -->
    <div class="table-container mat-elevation-z1">
      @if (!store.loading() && !store.hasResults()) {
        <app-empty-state
          icon="receipt"
          title="No transactions found"
          message="Try adjusting your search or filters."
        />
      } @else {
        <app-datatable
          [dataSource]="store.payments()"
          [columns]="columns"
          [total]="store.total()"
          [pageSize]="store.limit()"
          [loading]="store.loading()"
          (pageChange)="onPage($event)"
          paginatorAriaLabel="Payments pagination"
        >
          <!-- Customer Template -->
          <ng-template appDatatableCell="customer" let-row>
            {{ row.customer_name }}
          </ng-template>

          <!-- Amount Template -->
          <ng-template appDatatableCell="amount" let-row>
            <span class="font-semibold">
              {{ row.amount | currency: 'INR' : 'symbol' : '1.0-2' }}
            </span>
          </ng-template>

          <!-- Payment Method Template -->
          <ng-template appDatatableCell="method" let-row>
            <span class="text-sm opacity-80">{{ row.payment_method }}</span>
          </ng-template>

          <!-- Status Template -->
          <ng-template appDatatableCell="status" let-row>
            <span class="custom-badge" [class]="'badge--' + row.status.toLowerCase()">
              {{ row.status }}
            </span>
          </ng-template>

          <!-- Created At Template -->
          <ng-template appDatatableCell="created_at" let-row>
            <span class="text-sm opacity-85">{{ row.created_at | date: 'medium' }}</span>
          </ng-template>

          <!-- Actions Template -->
          <ng-template appDatatableCell="actions" let-row>
            @if (row.status === 'SUCCESS') {
              <button
                mat-flat-button
                color="warn"
                class="refund-button"
                (click)="onRefund(row.id)"
              >
                <svg lucideUndo2 [size]="16"></svg> Refund
              </button>
            }
          </ng-template>
        </app-datatable>
      }
    </div>
  `,
  styles: `
    .filters-row {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 16px;
      flex-wrap: wrap;
    }
    .search-field { flex: 1; min-width: 240px; }
    .filter-chips {
      display: flex;
      gap: 8px;
      align-items: center;

      &::ng-deep .mat-mdc-chip {
        height: 40px;
        font-size: 13px;
      }
    }
    .table-container {
      border-radius: 0;
      overflow: hidden;
      background: var(--color-surface-1);
    }
    .full-width {
      width: 100%;
    }
    .table-row:hover {
      background: var(--color-surface-2);
    }

    .custom-badge {
      font-size: 0.72rem;
      font-weight: 600;
      padding: 3px 8px;
      border-radius: 0;
      text-transform: uppercase;
    }
    .badge--success {
      background: var(--color-success-bg);
      color: var(--color-success);
    }
    .badge--refunded {
      background: var(--color-orange-bg);
      color: var(--color-orange-text);
    }
    .badge--failed {
      background: var(--color-error-bg);
      color: var(--color-error);
    }

    .refund-button {
      font-size: 0.78rem !important;
      height: 28px !important;
      padding: 0 10px !important;
      line-height: 28px !important;
    }
    .refund-button svg {
      width: 16px;
      height: 16px;
      margin-right: 2px;
      vertical-align: middle;
    }
  `,
})
export class PaymentsListComponent implements OnInit, OnDestroy {
  protected readonly store = inject(PaymentsStore);
  private readonly headerService = inject(HeaderService);
  private readonly dialog = inject(MatDialog);

  constructor() {
    effect(() => {
      this.headerService.setLoading(this.store.loading());
    });
  }
  protected readonly columns: DatatableColumn[] = [
    { key: 'customer', label: 'Customer' },
    { key: 'amount', label: 'Amount' },
    { key: 'method', label: 'Payment Method' },
    { key: 'status', label: 'Status' },
    { key: 'created_at', label: 'Date & Time' },
    { key: 'actions', label: 'Actions' },
  ];

  protected readonly searchValue = signal('');
  protected readonly statusFilter = signal<PaymentStatus | 'ALL'>('ALL');

  ngOnInit(): void {
    this.store.loadPayments();
  }

  ngOnDestroy(): void {
    this.headerService.setLoading(false);
  }

  onSearch(value: string): void {
    this.searchValue.set(value);
    this.store.setSearch(value);
    this.store.loadPayments();
  }

  onStatusFilter(value: PaymentStatus | 'ALL'): void {
    this.statusFilter.set(value);
    this.store.setStatusFilter(value);
    this.store.loadPayments();
  }

  onPage(event: PageEvent): void {
    this.store.setPage(event.pageIndex);
    this.store.loadPayments();
  }

  onRefund(id: string): void {
    this.dialog
      .open(ConfirmDialog, {
        data: {
          title: 'Refund Payment',
          message: 'Are you sure you want to refund this payment? This action is irreversible.',
          confirmLabel: 'Refund',
          variant: 'danger',
        },
        width: '400px',
      })
      .afterClosed()
      .subscribe((confirmed) => {
        if (confirmed) {
          this.store.refundTransaction(id);
        }
      });
  }
}
