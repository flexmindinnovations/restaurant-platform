import {
  ChangeDetectionStrategy,
  Component,
  inject,
  OnInit,
  OnDestroy,
  effect,
  signal,
} from '@angular/core';
import { NgTemplateOutlet } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipListbox, MatChipOption } from '@angular/material/chips';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltipModule } from '@angular/material/tooltip';
import {
  LucidePlus,
  LucideArmchair,
  LucideTrash2,
  LucideChevronDown,
} from '@lucide/angular';
import { HeaderService, ConfirmDialog, StatusBadge, EmptyState } from '@app/shared';
import { RestaurantTable, Section, TABLE_STATUS_LABELS, TableStatus } from '@app/api-client';
import { TablesStore } from './tables.store';
import { TableDialog, TableDialogResult } from './table-dialog';

@Component({
  selector: 'app-tables-page',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    NgTemplateOutlet,
    RouterLink,
    MatButtonModule,
    MatCardModule,
    MatChipListbox,
    MatChipOption,
    MatDialogModule,
    MatMenuModule,
    MatTooltipModule,
    LucidePlus,
    LucideArmchair,
    LucideTrash2,
    LucideChevronDown,
    StatusBadge,
    EmptyState,
  ],
  template: `
    <!-- Header actions -->
    <div class="page-actions">
      <div class="page-actions__left">
        <mat-chip-listbox
          [value]="selectedSection()"
          (change)="onSectionFilter($event.value)"
          aria-label="Section filter"
        >
          <mat-chip-option value="all">All Sections</mat-chip-option>
          @for (section of store.sections(); track section.id) {
            <mat-chip-option [value]="section.id">{{ section.name }}</mat-chip-option>
          }
        </mat-chip-listbox>
      </div>
      <div class="page-actions__right">
        <a mat-stroked-button routerLink="reservations">Reservations</a>
        <a mat-stroked-button routerLink="waitlist">Waitlist</a>
        <button mat-flat-button color="primary" (click)="onAddTable()">
          <svg lucidePlus [size]="18"></svg>
          Add Table
        </button>
      </div>
    </div>

    <!-- Floor plan grid -->
    @if (!store.loading() && !store.hasTables()) {
      <app-empty-state
        icon="armchair"
        title="No tables found"
        message="Add tables to start managing your floor plan."
      >
        <button mat-flat-button color="primary" (click)="onAddTable()" style="margin-top: 16px">
          <svg lucidePlus [size]="18"></svg>
          Add First Table
        </button>
      </app-empty-state>
    } @else {
      @for (section of store.sections(); track section.id) {
        @if (filteredTables(section.id).length > 0) {
          <div class="section-group">
            <h3 class="section-title">{{ section.name }}</h3>
            <div class="tables-grid">
              @for (table of filteredTables(section.id); track table.id) {
                <ng-container *ngTemplateOutlet="tableCard; context: { $implicit: table }" />
              }
            </div>
          </div>
        }
      }
      @if (unassignedTables().length > 0) {
        <div class="section-group">
          <h3 class="section-title">Unassigned</h3>
          <div class="tables-grid">
            @for (table of unassignedTables(); track table.id) {
              <ng-container *ngTemplateOutlet="tableCard; context: { $implicit: table }" />
            }
          </div>
        </div>
      }
    }

    <!-- Table card template -->
    <ng-template #tableCard let-table>
      <mat-card class="table-card" [class]="'table-card--' + statusColor(table.status)">
        <mat-card-content class="table-card__content">
          <div class="table-card__header">
            <span class="table-card__number">{{ table.number }}</span>
            <app-status-badge [status]="table.status" />
          </div>
          <div class="table-card__info">
            <span class="table-card__capacity">{{ table.capacity_min }}-{{ table.capacity_max }} seats</span>
            <span class="table-card__shape">{{ shapeLabel(table.shape) }}</span>
          </div>
          <div class="table-card__actions">
            <button mat-button [matMenuTriggerFor]="statusMenu" class="status-trigger">
              Change Status
              <svg lucideChevronDown [size]="14"></svg>
            </button>
            <mat-menu #statusMenu="matMenu">
              @for (status of allStatuses; track status) {
                <button mat-menu-item (click)="onStatusChange(table.id, status)">
                  {{ statusLabel(status) }}
                </button>
              }
            </mat-menu>
            <button
              mat-icon-button
              matTooltip="Delete table"
              (click)="onDeleteTable(table)"
              class="delete-btn"
            >
              <svg lucideTrash2 [size]="16"></svg>
            </button>
          </div>
        </mat-card-content>
      </mat-card>
    </ng-template>
  `,
  styles: `
    .page-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      flex-wrap: wrap;
      gap: 12px;
    }
    .page-actions__right {
      display: flex;
      gap: 8px;
      align-items: center;
    }
    .section-group {
      margin-bottom: 32px;
    }
    .section-title {
      font-size: 1rem;
      font-weight: 600;
      margin: 0 0 12px;
      color: var(--color-text-secondary, #64748b);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      font-size: 0.75rem;
    }
    .tables-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap: 16px;
    }
    .table-card {
      cursor: default;
      border-left: 4px solid transparent;
    }
    .table-card--success { border-left-color: var(--color-success, #16a34a); }
    .table-card--error { border-left-color: var(--color-error, #dc2626); }
    .table-card--warning { border-left-color: var(--color-warning, #d97706); }
    .table-card--info { border-left-color: var(--color-info, #2563eb); }
    .table-card--neutral { border-left-color: var(--color-text-tertiary, #94a3b8); }
    .table-card__content {
      padding: 16px;
    }
    .table-card__header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }
    .table-card__number {
      font-size: 1.125rem;
      font-weight: 600;
    }
    .table-card__info {
      display: flex;
      gap: 12px;
      font-size: 0.8125rem;
      color: var(--color-text-secondary, #64748b);
      margin-bottom: 12px;
    }
    .table-card__actions {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .status-trigger {
      font-size: 0.8125rem;
    }
    .delete-btn {
      color: var(--color-error, #dc2626);
    }
  `,
})
export class TablesPage implements OnInit, OnDestroy {
  protected readonly store = inject(TablesStore);
  private readonly headerService = inject(HeaderService);
  private readonly dialog = inject(MatDialog);

  protected readonly selectedSection = signal<string>('all');

  readonly allStatuses: TableStatus[] = ['AVAILABLE', 'OCCUPIED', 'RESERVED', 'CLEANING', 'BLOCKED'];

  private readonly STATUS_COLOR_MAP: Record<TableStatus, string> = {
    AVAILABLE: 'success',
    OCCUPIED: 'error',
    RESERVED: 'warning',
    CLEANING: 'info',
    BLOCKED: 'neutral',
  };

  private readonly SHAPE_LABELS: Record<string, string> = {
    ROUND: 'Round',
    SQUARE: 'Square',
    RECTANGULAR: 'Rectangular',
    BOOTH: 'Booth',
    BAR_SEAT: 'Bar Seat',
  };

  constructor() {
    effect(() => {
      this.headerService.setLoading(this.store.loading());
    });
  }

  ngOnInit(): void {
    this.headerService.setHeader('Tables', 'Manage floor plan and table layout');
    // TODO: get restaurant ID from route or auth context
    const restaurantId = this.store.selectedRestaurantId();
    if (restaurantId) {
      this.store.loadSections(restaurantId);
      this.store.loadTables({ restaurant_id: restaurantId });
    }
  }

  ngOnDestroy(): void {
    this.headerService.setLoading(false);
  }

  statusLabel(status: TableStatus): string {
    return TABLE_STATUS_LABELS[status];
  }

  statusColor(status: TableStatus): string {
    return this.STATUS_COLOR_MAP[status] ?? 'neutral';
  }

  shapeLabel(shape: string): string {
    return this.SHAPE_LABELS[shape] ?? shape;
  }

  filteredTables(sectionId: string): RestaurantTable[] {
    const sectionFilter = this.selectedSection();
    if (sectionFilter !== 'all' && sectionFilter !== sectionId) return [];
    return this.store.tables().filter((t) => t.section_id === sectionId);
  }

  unassignedTables(): RestaurantTable[] {
    const sectionFilter = this.selectedSection();
    if (sectionFilter !== 'all') return [];
    return this.store.tables().filter((t) => !t.section_id);
  }

  onSectionFilter(value: string): void {
    this.selectedSection.set(value ?? 'all');
  }

  onStatusChange(tableId: string, status: TableStatus): void {
    this.store.updateTableStatus({ id: tableId, status });
  }

  onAddTable(): void {
    this.dialog
      .open(TableDialog, {
        data: { sections: this.store.sections() },
        width: '520px',
      })
      .afterClosed()
      .subscribe((result: TableDialogResult | undefined) => {
        if (result) {
          this.store.createTable(result);
        }
      });
  }

  onDeleteTable(table: RestaurantTable): void {
    this.dialog
      .open(ConfirmDialog, {
        data: {
          title: 'Delete Table',
          message: `Are you sure you want to delete table "${table.number}"?`,
          confirmLabel: 'Delete',
          variant: 'danger',
        },
        width: '400px',
      })
      .afterClosed()
      .subscribe((confirmed: boolean) => {
        if (confirmed) {
          this.store.deleteTable(table.id);
        }
      });
  }
}
