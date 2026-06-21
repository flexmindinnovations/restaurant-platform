import {
  ChangeDetectionStrategy,
  Component,
  inject,
  OnInit,
  OnDestroy,
  effect,
  signal,
} from '@angular/core';
import { RouterLink, Router, ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { PageEvent } from '@angular/material/paginator';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { LucideSearch, LucideChevronRight, LucideCircleCheck, LucideBan } from '@lucide/angular';
import { MatChipListbox, MatChipOption } from '@angular/material/chips';

import { MatTooltipModule } from '@angular/material/tooltip';
import { HeaderService } from '@app/shared';
import { StatusBadge } from '../../../shared/src/lib/status-badge';
import { EmptyState } from '../../../shared/src/lib/empty-state';
import { DatatableComponent, DatatableCellDirective, DatatableColumn } from '@app/design-system';
import { RestaurantsStore } from './restaurants.store';

@Component({
  selector: 'app-restaurants-list',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    RouterLink,
    FormsModule,
    MatInputModule,
    MatFormFieldModule,
    MatButtonModule,
    LucideSearch,
    LucideChevronRight,
    LucideCircleCheck,
    LucideBan,
    MatChipListbox,
    MatChipOption,
    MatTooltipModule,
    StatusBadge,
    EmptyState,
    DatatableComponent,
    DatatableCellDirective,
  ],
  template: `
    <!-- Filters -->
    <div class="filters-row">
      <mat-form-field appearance="outline" class="search-field" subscriptSizing="dynamic">
        <mat-label>Search restaurants</mat-label>
        <svg lucideSearch [size]="18" matIconPrefix></svg>
        <input
          matInput
          [ngModel]="searchValue()"
          (ngModelChange)="onSearch($event)"
          placeholder="Name, city…"
          id="restaurant-search"
        />
      </mat-form-field>

      <mat-chip-listbox
        [ngModel]="verifiedFilter()"
        (ngModelChange)="onVerifiedFilter($event)"
        class="filter-chips"
        aria-label="Verification filter"
      >
        <mat-chip-option value="all">All</mat-chip-option>
        <mat-chip-option value="verified">Verified</mat-chip-option>
        <mat-chip-option value="unverified">Unverified</mat-chip-option>
      </mat-chip-listbox>
    </div>

    <!-- Table -->
    <div class="table-wrapper-container">
      @if (!store.loading() && !store.hasResults()) {
        <app-empty-state
          icon="store"
          title="No restaurants found"
          message="Try adjusting your search or filters."
        />
      } @else {
        <app-datatable
          [dataSource]="store.restaurants()"
          [columns]="columns"
          [total]="store.total()"
          [pageSize]="10"
          [loading]="store.loading()"
          (pageChange)="onPage($event)"
          (rowClick)="onRowClick($event)"
          paginatorAriaLabel="Restaurants pagination"
        >
          <!-- Name -->
          <ng-template appDatatableCell="name" let-row>
            <a [routerLink]="[row.id]" class="restaurant-link">{{ row.name }}</a>
          </ng-template>

          <!-- City -->
          <ng-template appDatatableCell="city" let-row>
            {{ row.address_city }}, {{ row.address_state }}
          </ng-template>

          <!-- Cuisine -->
          <ng-template appDatatableCell="cuisine" let-row>
            {{ row.cuisine_types.join(', ') }}
          </ng-template>

          <!-- Status -->
          <ng-template appDatatableCell="status" let-row>
            <app-status-badge [status]="row.is_active ? 'ACTIVE' : 'INACTIVE'" />
          </ng-template>

          <!-- Verified -->
          <ng-template appDatatableCell="verified" let-row>
            <app-status-badge [status]="row.is_verified ? 'VERIFIED' : 'UNVERIFIED'" />
          </ng-template>

          <!-- Actions -->
          <ng-template appDatatableCell="actions" let-row>
            <button
              mat-icon-button
              [routerLink]="[row.id]"
              matTooltip="View detail"
              aria-label="View restaurant detail"
            >
              <svg lucideChevronRight [size]="16" style="color: var(--color-text-secondary)"></svg>
            </button>
            @if (!row.is_verified) {
              <button
                mat-icon-button
                (click)="onVerify(row.id, $event)"
                matTooltip="Approve registration"
                aria-label="Approve registration"
              >
                <svg lucideCircleCheck [size]="16" style="color: var(--color-success)"></svg>
              </button>
              <button
                mat-icon-button
                (click)="onReject(row.id, $event)"
                matTooltip="Reject registration"
                aria-label="Reject registration"
              >
                <svg lucideBan [size]="16" style="color: var(--color-error)"></svg>
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
    .table-wrapper-container {
      width: 100%;
    }
    .restaurant-link {
      color: var(--color-primary);
      text-decoration: none;
      font-weight: 500;
    }
    .restaurant-link:hover {
      text-decoration: underline;
    }
  `,
})
export class RestaurantsList implements OnInit, OnDestroy {
  protected readonly store = inject(RestaurantsStore);
  private readonly headerService = inject(HeaderService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);

  constructor() {
    effect(() => {
      this.headerService.setLoading(this.store.loading());
    });
  }

  protected readonly columns: DatatableColumn[] = [
    { key: 'name', label: 'Name' },
    { key: 'city', label: 'City' },
    { key: 'cuisine', label: 'Cuisine' },
    { key: 'status', label: 'Status' },
    { key: 'verified', label: 'Verified' },
    { key: 'actions', label: 'Actions' },
  ];

  protected readonly searchValue = signal('');
  protected readonly verifiedFilter = signal<'all' | 'verified' | 'unverified'>('all');

  ngOnInit(): void {
    this.store.loadRestaurants();
  }

  ngOnDestroy(): void {
    this.headerService.setLoading(false);
  }

  onSearch(value: string): void {
    this.searchValue.set(value);
    this.store.setSearch(value);
    this.store.loadRestaurants();
  }

  onVerifiedFilter(value: 'all' | 'verified' | 'unverified'): void {
    this.verifiedFilter.set(value);
    const filterVal = value === 'verified' ? true : value === 'unverified' ? false : null;
    this.store.setFilterVerified(filterVal);
    this.store.loadRestaurants();
  }

  onPage(event: PageEvent): void {
    this.store.setPage(event.pageIndex);
    this.store.loadRestaurants();
  }

  onRowClick(row: unknown): void {
    const id = (row as { id: string }).id;
    this.router.navigate([id], { relativeTo: this.route });
  }

  onVerify(id: string, event: Event): void {
    event.stopPropagation();
    this.store.verifyRestaurant(id);
  }

  onReject(id: string, event: Event): void {
    event.stopPropagation();
    if (confirm('Are you sure you want to reject this restaurant registration?')) {
      this.store.rejectRestaurant(id);
    }
  }
}

