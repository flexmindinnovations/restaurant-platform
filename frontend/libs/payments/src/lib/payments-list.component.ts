import {
  ChangeDetectionStrategy,
  Component,
  inject,
  OnInit,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { PageHeader } from '../../../shared/src/lib/page-header';
import { EmptyState } from '../../../shared/src/lib/empty-state';
import { PaymentsStore } from './payments.store';
import { PaymentStatus } from './payments.model';

@Component({
  selector: 'app-payments-list',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatPaginatorModule,
    MatInputModule,
    MatFormFieldModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatProgressBarModule,
    MatTooltipModule,
    PageHeader,
    EmptyState,
  ],
  template: `
    <app-page-header title="Payments Ledger" subtitle="View transaction history, payment methods, and handle refunds">
    </app-page-header>

    <!-- Filters -->
    <div class="filters-row">
      <mat-form-field appearance="outline" class="search-field">
        <mat-label>Search transactions</mat-label>
        <mat-icon matPrefix>search</mat-icon>
        <input matInput [ngModel]="searchValue()" (ngModelChange)="onSearch($event)"
          placeholder="Tx ID, Order ID, Customer…" id="payment-search" />
      </mat-form-field>

      <mat-chip-listbox [ngModel]="statusFilter()" (ngModelChange)="onStatusFilter($event)"
        class="filter-chips" aria-label="Status filter">
        <mat-chip-option value="ALL">All Transactions</mat-chip-option>
        <mat-chip-option value="SUCCESS">Success</mat-chip-option>
        <mat-chip-option value="REFUNDED">Refunded</mat-chip-option>
        <mat-chip-option value="FAILED">Failed</mat-chip-option>
      </mat-chip-listbox>
    </div>

    <!-- Loading bar -->
    @if (store.loading()) {
      <mat-progress-bar mode="indeterminate" />
    }

    <!-- Table -->
    <div class="table-container mat-elevation-z1">
      @if (!store.loading() && !store.hasResults()) {
        <app-empty-state icon="receipt_long" title="No transactions found"
          message="Try adjusting your search or filters." />
      } @else {
        <table mat-table [dataSource]="store.payments()" class="full-width">
          <!-- TX ID -->
          <ng-container matColumnDef="id">
            <th mat-header-cell *matHeaderCellDef>Transaction ID</th>
            <td mat-cell *matCellDef="let tx" class="font-mono text-sm">{{ tx.id }}</td>
          </ng-container>

          <!-- Order ID -->
          <ng-container matColumnDef="order_id">
            <th mat-header-cell *matHeaderCellDef>Order ID</th>
            <td mat-cell *matCellDef="let tx" class="font-mono text-sm">{{ tx.order_id }}</td>
          </ng-container>

          <!-- Customer -->
          <ng-container matColumnDef="customer">
            <th mat-header-cell *matHeaderCellDef>Customer</th>
            <td mat-cell *matCellDef="let tx">{{ tx.customer_name }}</td>
          </ng-container>

          <!-- Amount -->
          <ng-container matColumnDef="amount">
            <th mat-header-cell *matHeaderCellDef>Amount</th>
            <td mat-cell *matCellDef="let tx" class="font-semibold">
              {{ tx.amount | currency }}
            </td>
          </ng-container>

          <!-- Payment Method -->
          <ng-container matColumnDef="method">
            <th mat-header-cell *matHeaderCellDef>Payment Method</th>
            <td mat-cell *matCellDef="let tx" class="text-sm opacity-80">{{ tx.payment_method }}</td>
          </ng-container>

          <!-- Status -->
          <ng-container matColumnDef="status">
            <th mat-header-cell *matHeaderCellDef>Status</th>
            <td mat-cell *matCellDef="let tx">
              <!-- status-badge mapping expects custom statuses -->
              <span class="custom-badge" [class]="'badge--' + tx.status.toLowerCase()">{{ tx.status }}</span>
            </td>
          </ng-container>

          <!-- Created At -->
          <ng-container matColumnDef="created_at">
            <th mat-header-cell *matHeaderCellDef>Date & Time</th>
            <td mat-cell *matCellDef="let tx" class="text-sm opacity-85">
              {{ tx.created_at | date: 'medium' }}
            </td>
          </ng-container>

          <!-- Actions -->
          <ng-container matColumnDef="actions">
            <th mat-header-cell *matHeaderCellDef></th>
            <td mat-cell *matCellDef="let tx">
              @if (tx.status === 'SUCCESS') {
                <button mat-flat-button color="warn" class="refund-button"
                  (click)="onRefund(tx.id)">
                  <mat-icon>undo</mat-icon> Refund
                </button>
              }
            </td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
          <tr mat-row *matRowDef="let row; columns: displayedColumns" class="table-row"></tr>
        </table>

        <mat-paginator
          [length]="store.total()"
          [pageSize]="store.limit()"
          [pageSizeOptions]="[5, 10, 20]"
          (page)="onPage($event)"
          aria-label="Payments pagination">
        </mat-paginator>
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
    .filter-chips { display: flex; gap: 8px; }
    .table-container {
      border-radius: 8px;
      overflow: hidden;
      background: var(--mat-sys-surface, #fff);
    }
    .full-width { width: 100%; }
    .table-row:hover { background: var(--mat-sys-surface-variant, #f5f5f5); }
    
    .custom-badge {
      font-size: 0.72rem;
      font-weight: 600;
      padding: 3px 8px;
      border-radius: 4px;
      text-transform: uppercase;
    }
    .badge--success { background: #e8f5e9; color: #2e7d32; }
    .badge--refunded { background: #fff3e0; color: #e65100; }
    .badge--failed { background: #ffebee; color: #c62828; }

    .refund-button {
      font-size: 0.78rem !important;
      height: 28px !important;
      padding: 0 10px !important;
      line-height: 28px !important;
    }
    .refund-button mat-icon {
      font-size: 16px !important;
      width: 16px !important;
      height: 16px !important;
      margin-right: 2px !important;
    }
  `,
})
export class PaymentsListComponent implements OnInit {
  protected readonly store = inject(PaymentsStore);
  protected readonly displayedColumns = [
    'id',
    'order_id',
    'customer',
    'amount',
    'method',
    'status',
    'created_at',
    'actions',
  ];

  protected readonly searchValue = signal('');
  protected readonly statusFilter = signal<PaymentStatus | 'ALL'>('ALL');

  ngOnInit(): void {
    this.store.loadPayments();
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
    if (confirm('Are you sure you want to refund this payment? This action is irreversible.')) {
      this.store.refundTransaction(id);
    }
  }
}
