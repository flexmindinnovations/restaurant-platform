import {
  ChangeDetectionStrategy,
  Component,
  inject,
  OnInit,
  OnDestroy,
  effect,
  signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { PageEvent } from '@angular/material/paginator';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';
import {
  LucidePlus,
  LucideCalendar,
  LucideCheck,
  LucideX,
  LucideUserX,
  LucideArrowLeft,
} from '@lucide/angular';
import { HeaderService, StatusBadge, EmptyState, ConfirmDialog } from '@app/shared';
import { DatatableComponent, DatatableCellDirective, DatatableColumn } from '@app/design-system';
import { Reservation, RESERVATION_STATUS_LABELS, ReservationStatus } from '@app/api-client';
import { TablesStore } from './tables.store';
import { ReservationDialog, ReservationDialogData } from './reservation-dialog';

@Component({
  selector: 'app-reservations-page',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    FormsModule,
    RouterLink,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatDialogModule,
    MatTooltipModule,
    LucidePlus,
    LucideCalendar,
    LucideCheck,
    LucideX,
    LucideUserX,
    LucideArrowLeft,
    StatusBadge,
    EmptyState,
    DatatableComponent,
    DatatableCellDirective,
  ],
  template: `
    <!-- Header -->
    <div class="page-actions">
      <div class="page-actions__left">
        <a mat-icon-button routerLink="/tables" matTooltip="Back to Tables">
          <svg lucideArrowLeft [size]="20"></svg>
        </a>
        <mat-form-field appearance="outline" subscriptSizing="dynamic" class="date-field">
          <mat-label>Reservation Date</mat-label>
          <svg lucideCalendar [size]="18" matIconPrefix></svg>
          <input
            matInput
            type="date"
            [ngModel]="dateFilter()"
            (ngModelChange)="onDateFilter($event)"
          />
        </mat-form-field>
      </div>
      <button mat-flat-button color="primary" (click)="onNewReservation()">
        <svg lucidePlus [size]="18"></svg>
        New Reservation
      </button>
    </div>

    <!-- Table -->
    <div class="table-wrapper">
      @if (!store.loading() && !store.hasReservations()) {
        <app-empty-state
          icon="calendar"
          title="No reservations found"
          message="No reservations for the selected date."
        >
          <button mat-flat-button color="primary" (click)="onNewReservation()" style="margin-top: 16px">
            <svg lucidePlus [size]="18"></svg>
            Create Reservation
          </button>
        </app-empty-state>
      } @else {
        <app-datatable
          [dataSource]="store.reservations()"
          [columns]="columns"
          [total]="store.reservationsTotal()"
          [pageSize]="10"
          [loading]="store.loading()"
          (pageChange)="onPage($event)"
          paginatorAriaLabel="Reservations pagination"
        >
          <ng-template appDatatableCell="customer" let-row>
            <div class="customer-info">
              <span class="customer-name">{{ row.customer_name }}</span>
              @if (row.customer_phone) {
                <span class="customer-detail">{{ row.customer_phone }}</span>
              }
            </div>
          </ng-template>

          <ng-template appDatatableCell="time" let-row>
            {{ row.start_time }} - {{ row.end_time }}
          </ng-template>

          <ng-template appDatatableCell="party_size" let-row>
            {{ row.party_size }} guests
          </ng-template>

          <ng-template appDatatableCell="status" let-row>
            <app-status-badge [status]="row.status" />
          </ng-template>

          <ng-template appDatatableCell="source" let-row>
            {{ row.source }}
          </ng-template>

          <ng-template appDatatableCell="actions" let-row>
            @if (row.status === 'PENDING') {
              <button
                mat-icon-button
                matTooltip="Confirm reservation"
                (click)="onConfirm(row, $event)"
              >
                <svg lucideCheck [size]="16" style="color: var(--color-success)"></svg>
              </button>
            }
            @if (row.status === 'CONFIRMED') {
              <button
                mat-icon-button
                matTooltip="Seat guests"
                (click)="onSeat(row.id, $event)"
              >
                <svg lucideCheck [size]="16" style="color: var(--color-info)"></svg>
              </button>
            }
            @if (row.status === 'PENDING' || row.status === 'CONFIRMED') {
              <button
                mat-icon-button
                matTooltip="Cancel reservation"
                (click)="onCancel(row.id, $event)"
              >
                <svg lucideX [size]="16" style="color: var(--color-error)"></svg>
              </button>
              <button
                mat-icon-button
                matTooltip="Mark as no-show"
                (click)="onNoShow(row.id, $event)"
              >
                <svg lucideUserX [size]="16" style="color: var(--color-warning)"></svg>
              </button>
            }
          </ng-template>
        </app-datatable>
      }
    </div>
  `,
  styles: `
    .page-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      flex-wrap: wrap;
      gap: 12px;
    }
    .page-actions__left {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .date-field {
      width: 200px;
    }
    .table-wrapper {
      width: 100%;
    }
    .customer-info {
      display: flex;
      flex-direction: column;
    }
    .customer-name {
      font-weight: 500;
    }
    .customer-detail {
      font-size: 0.75rem;
      color: var(--color-text-secondary, #64748b);
    }
  `,
})
export class ReservationsPage implements OnInit, OnDestroy {
  protected readonly store = inject(TablesStore);
  private readonly headerService = inject(HeaderService);
  private readonly dialog = inject(MatDialog);

  protected readonly dateFilter = signal(new Date().toISOString().split('T')[0]);

  protected readonly columns: DatatableColumn[] = [
    { key: 'customer', label: 'Customer' },
    { key: 'time', label: 'Time' },
    { key: 'party_size', label: 'Party Size' },
    { key: 'status', label: 'Status' },
    { key: 'source', label: 'Source' },
    { key: 'actions', label: 'Actions' },
  ];

  constructor() {
    effect(() => {
      this.headerService.setLoading(this.store.loading());
    });
  }

  ngOnInit(): void {
    this.headerService.setHeader('Reservations', 'Manage restaurant reservations');
    const restaurantId = this.store.selectedRestaurantId();
    if (restaurantId) {
      this.store.loadReservations({
        restaurant_id: restaurantId,
        reservation_date: this.dateFilter(),
      });
    }
  }

  ngOnDestroy(): void {
    this.headerService.setLoading(false);
  }

  onDateFilter(date: string): void {
    this.dateFilter.set(date);
    const restaurantId = this.store.selectedRestaurantId();
    if (restaurantId) {
      this.store.setReservationDate(date);
      this.store.loadReservations({
        restaurant_id: restaurantId,
        reservation_date: date,
      });
    }
  }

  onPage(event: PageEvent): void {
    const restaurantId = this.store.selectedRestaurantId();
    if (restaurantId) {
      this.store.loadReservations({
        restaurant_id: restaurantId,
        reservation_date: this.dateFilter(),
        skip: event.pageIndex * event.pageSize,
        limit: event.pageSize,
      });
    }
  }

  onNewReservation(): void {
    const restaurantId = this.store.selectedRestaurantId();
    if (!restaurantId) return;
    this.dialog
      .open(ReservationDialog, {
        data: { restaurantId } as ReservationDialogData,
        width: '520px',
      })
      .afterClosed()
      .subscribe((result) => {
        if (result) {
          this.store.createReservation(result);
        }
      });
  }

  onConfirm(reservation: Reservation, event: Event): void {
    event.stopPropagation();
    // If the reservation already has a table_id assigned, use it; otherwise pick the first available
    const tableId = reservation.table_id ?? this.store.availableTables()[0]?.id;
    if (tableId) {
      this.store.confirmReservation({ id: reservation.id, tableId });
    }
  }

  onSeat(id: string, event: Event): void {
    event.stopPropagation();
    this.store.seatReservation(id);
  }

  onCancel(id: string, event: Event): void {
    event.stopPropagation();
    this.dialog
      .open(ConfirmDialog, {
        data: {
          title: 'Cancel Reservation',
          message: 'Are you sure you want to cancel this reservation?',
          confirmLabel: 'Cancel Reservation',
          variant: 'danger',
        },
        width: '400px',
      })
      .afterClosed()
      .subscribe((confirmed: boolean) => {
        if (confirmed) {
          this.store.cancelReservation({ id });
        }
      });
  }

  onNoShow(id: string, event: Event): void {
    event.stopPropagation();
    this.store.markNoShow(id);
  }
}
