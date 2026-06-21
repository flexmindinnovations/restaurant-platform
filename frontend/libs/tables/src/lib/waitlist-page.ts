import {
  ChangeDetectionStrategy,
  Component,
  inject,
  OnInit,
  OnDestroy,
  effect,
  signal,
} from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltipModule } from '@angular/material/tooltip';
import {
  LucideBell,
  LucideArmchair,
  LucideX,
  LucideClock,
  LucideUsers,
  LucideArrowLeft,
} from '@lucide/angular';
import { HeaderService, StatusBadge, EmptyState, ConfirmDialog } from '@app/shared';
import { WaitlistEntry, RestaurantTable } from '@app/api-client';
import { TablesStore } from './tables.store';

@Component({
  selector: 'app-waitlist-page',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    RouterLink,
    MatButtonModule,
    MatCardModule,
    MatDialogModule,
    MatMenuModule,
    MatTooltipModule,
    LucideBell,
    LucideArmchair,
    LucideX,
    LucideClock,
    LucideUsers,
    LucideArrowLeft,
    StatusBadge,
    EmptyState,
  ],
  template: `
    <!-- Header -->
    <div class="page-actions">
      <a mat-icon-button routerLink="/tables" matTooltip="Back to Tables">
        <svg lucideArrowLeft [size]="20"></svg>
      </a>
      <h3 class="page-title">Active Waitlist</h3>
    </div>

    @if (!store.loading() && !store.hasWaitlist()) {
      <app-empty-state
        icon="users"
        title="Waitlist is empty"
        message="No one is currently waiting."
      />
    } @else {
      <div class="waitlist-grid">
        @for (entry of store.waitlistEntries(); track entry.id) {
          <mat-card class="waitlist-card">
            <mat-card-content class="waitlist-card__content">
              <div class="waitlist-card__header">
                <div class="waitlist-card__position">#{{ entry.queue_position }}</div>
                <app-status-badge [status]="entry.status" />
              </div>
              <div class="waitlist-card__name">{{ entry.customer_name }}</div>
              <div class="waitlist-card__details">
                <span class="waitlist-card__detail">
                  <svg lucideUsers [size]="14"></svg>
                  {{ entry.party_size }} guests
                </span>
                <span class="waitlist-card__detail">
                  <svg lucideClock [size]="14"></svg>
                  ~{{ entry.estimated_wait_minutes }} min
                </span>
              </div>
              @if (entry.customer_phone) {
                <div class="waitlist-card__phone">{{ entry.customer_phone }}</div>
              }
              @if (entry.special_requests) {
                <div class="waitlist-card__note">{{ entry.special_requests }}</div>
              }
              <div class="waitlist-card__actions">
                @if (entry.status === 'WAITING') {
                  <button
                    mat-stroked-button
                    matTooltip="Notify customer"
                    (click)="onNotify(entry.id)"
                  >
                    <svg lucideBell [size]="16"></svg>
                    Notify
                  </button>
                }
                @if (entry.status === 'WAITING' || entry.status === 'NOTIFIED') {
                  <button
                    mat-stroked-button
                    [matMenuTriggerFor]="seatMenu"
                    matTooltip="Seat at a table"
                  >
                    <svg lucideArmchair [size]="16"></svg>
                    Seat
                  </button>
                  <mat-menu #seatMenu="matMenu">
                    @for (table of store.availableTables(); track table.id) {
                      <button mat-menu-item (click)="onSeat(entry.id, table.id)">
                        {{ table.number }} ({{ table.capacity_max }} seats)
                      </button>
                    }
                    @if (store.availableTables().length === 0) {
                      <button mat-menu-item disabled>No available tables</button>
                    }
                  </mat-menu>
                }
                @if (entry.status === 'WAITING' || entry.status === 'NOTIFIED') {
                  <button
                    mat-icon-button
                    matTooltip="Remove from waitlist"
                    (click)="onRemove(entry)"
                  >
                    <svg lucideX [size]="16" style="color: var(--color-error)"></svg>
                  </button>
                }
              </div>
            </mat-card-content>
          </mat-card>
        }
      </div>
    }
  `,
  styles: `
    .page-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 24px;
    }
    .page-title {
      margin: 0;
      font-size: 1rem;
      font-weight: 600;
    }
    .waitlist-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px;
    }
    .waitlist-card__content {
      padding: 16px;
    }
    .waitlist-card__header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }
    .waitlist-card__position {
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--color-primary, #4f46e5);
    }
    .waitlist-card__name {
      font-size: 1rem;
      font-weight: 600;
      margin-bottom: 8px;
    }
    .waitlist-card__details {
      display: flex;
      gap: 16px;
      font-size: 0.8125rem;
      color: var(--color-text-secondary, #64748b);
      margin-bottom: 8px;
    }
    .waitlist-card__detail {
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .waitlist-card__phone {
      font-size: 0.8125rem;
      color: var(--color-text-secondary, #64748b);
      margin-bottom: 4px;
    }
    .waitlist-card__note {
      font-size: 0.8125rem;
      color: var(--color-text-tertiary, #94a3b8);
      font-style: italic;
      margin-bottom: 12px;
    }
    .waitlist-card__actions {
      display: flex;
      gap: 8px;
      align-items: center;
      padding-top: 8px;
      border-top: 1px solid var(--color-border, #e2e8f0);
    }
  `,
})
export class WaitlistPage implements OnInit, OnDestroy {
  protected readonly store = inject(TablesStore);
  private readonly headerService = inject(HeaderService);
  private readonly dialog = inject(MatDialog);

  constructor() {
    effect(() => {
      this.headerService.setLoading(this.store.loading());
    });
  }

  ngOnInit(): void {
    this.headerService.setHeader('Waitlist', 'Manage the restaurant waitlist');
    const restaurantId = this.store.selectedRestaurantId();
    if (restaurantId) {
      this.store.loadWaitlist({ restaurant_id: restaurantId });
      // Also load tables so we can show available ones for seating
      this.store.loadTables({ restaurant_id: restaurantId });
    }
  }

  ngOnDestroy(): void {
    this.headerService.setLoading(false);
  }

  onNotify(entryId: string): void {
    this.store.notifyWaitlist(entryId);
  }

  onSeat(entryId: string, tableId: string): void {
    this.store.seatFromWaitlist({ entryId, tableId });
  }

  onRemove(entry: WaitlistEntry): void {
    this.dialog
      .open(ConfirmDialog, {
        data: {
          title: 'Remove from Waitlist',
          message: `Remove "${entry.customer_name}" from the waitlist?`,
          confirmLabel: 'Remove',
          variant: 'danger',
        },
        width: '400px',
      })
      .afterClosed()
      .subscribe((confirmed: boolean) => {
        if (confirmed) {
          this.store.removeFromWaitlist(entry.id);
        }
      });
  }
}
