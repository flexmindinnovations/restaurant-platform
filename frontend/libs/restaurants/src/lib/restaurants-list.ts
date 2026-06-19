import {
  ChangeDetectionStrategy,
  Component,
  inject,
  OnInit,
  signal,
} from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { PageHeader } from '../../../shared/src/lib/page-header';
import { StatusBadge } from '../../../shared/src/lib/status-badge';
import { EmptyState } from '../../../shared/src/lib/empty-state';
import { RestaurantsStore } from './restaurants.store';

@Component({
  selector: 'app-restaurants-list',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    RouterLink,
    FormsModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatInputModule,
    MatFormFieldModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatProgressBarModule,
    MatTooltipModule,
    PageHeader,
    StatusBadge,
    EmptyState,
  ],
  template: `
    <app-page-header title="Restaurants" subtitle="Manage restaurant registrations and verification">
    </app-page-header>

    <!-- Filters -->
    <div class="filters-row">
      <mat-form-field appearance="outline" class="search-field">
        <mat-label>Search restaurants</mat-label>
        <mat-icon matPrefix>search</mat-icon>
        <input matInput [ngModel]="searchValue()" (ngModelChange)="onSearch($event)"
          placeholder="Name, city…" id="restaurant-search" />
      </mat-form-field>

      <mat-chip-listbox [ngModel]="verifiedFilter()" (ngModelChange)="onVerifiedFilter($event)"
        class="filter-chips" aria-label="Verification filter">
        <mat-chip-option value="all">All</mat-chip-option>
        <mat-chip-option value="verified">Verified</mat-chip-option>
        <mat-chip-option value="unverified">Unverified</mat-chip-option>
      </mat-chip-listbox>
    </div>

    <!-- Loading bar -->
    @if (store.loading()) {
      <mat-progress-bar mode="indeterminate" />
    }

    <!-- Table -->
    <div class="table-container mat-elevation-z1">
      @if (!store.loading() && !store.hasResults()) {
        <app-empty-state icon="storefront" title="No restaurants found"
          message="Try adjusting your search or filters." />
      } @else {
        <table mat-table [dataSource]="store.restaurants()" class="full-width">
          <!-- Name -->
          <ng-container matColumnDef="name">
            <th mat-header-cell *matHeaderCellDef>Name</th>
            <td mat-cell *matCellDef="let r">
              <a [routerLink]="[r.id]" class="restaurant-link">{{ r.name }}</a>
            </td>
          </ng-container>

          <!-- City -->
          <ng-container matColumnDef="city">
            <th mat-header-cell *matHeaderCellDef>City</th>
            <td mat-cell *matCellDef="let r">{{ r.address_city }}, {{ r.address_state }}</td>
          </ng-container>

          <!-- Cuisine -->
          <ng-container matColumnDef="cuisine">
            <th mat-header-cell *matHeaderCellDef>Cuisine</th>
            <td mat-cell *matCellDef="let r">{{ r.cuisine_types.join(', ') }}</td>
          </ng-container>

          <!-- Status -->
          <ng-container matColumnDef="status">
            <th mat-header-cell *matHeaderCellDef>Status</th>
            <td mat-cell *matCellDef="let r">
              <app-status-badge [status]="r.is_active ? 'ACTIVE' : 'INACTIVE'" />
            </td>
          </ng-container>

          <!-- Verified -->
          <ng-container matColumnDef="verified">
            <th mat-header-cell *matHeaderCellDef>Verified</th>
            <td mat-cell *matCellDef="let r">
              <app-status-badge [status]="r.is_verified ? 'VERIFIED' : 'UNVERIFIED'" />
            </td>
          </ng-container>

          <!-- Actions -->
          <ng-container matColumnDef="actions">
            <th mat-header-cell *matHeaderCellDef></th>
            <td mat-cell *matCellDef="let r">
              <button mat-icon-button [routerLink]="[r.id]"
                matTooltip="View detail" aria-label="View restaurant detail">
                <mat-icon>chevron_right</mat-icon>
              </button>
              @if (!r.is_verified) {
                <button mat-icon-button color="primary"
                  (click)="onVerify(r.id, $event)"
                  matTooltip="Approve registration" aria-label="Approve registration">
                  <mat-icon>check_circle</mat-icon>
                </button>
                <button mat-icon-button color="warn"
                  (click)="onReject(r.id, $event)"
                  matTooltip="Reject registration" aria-label="Reject registration">
                  <mat-icon>cancel</mat-icon>
                </button>
              }
            </td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
          <tr mat-row *matRowDef="let row; columns: displayedColumns"
            class="table-row" [routerLink]="[row.id]"></tr>
        </table>

        <mat-paginator
          [length]="store.total()"
          [pageSize]="20"
          [pageSizeOptions]="[10, 20, 50]"
          (page)="onPage($event)"
          aria-label="Restaurants pagination">
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
    .table-row { cursor: pointer; }
    .table-row:hover { background: var(--mat-sys-surface-variant, #f5f5f5); }
    .restaurant-link {
      color: var(--mat-sys-primary, #e65100);
      text-decoration: none;
      font-weight: 500;
    }
    .restaurant-link:hover { text-decoration: underline; }
  `,
})
export class RestaurantsList implements OnInit {
  protected readonly store = inject(RestaurantsStore);
  protected readonly displayedColumns = ['name', 'city', 'cuisine', 'status', 'verified', 'actions'];

  protected readonly searchValue = signal('');
  protected readonly verifiedFilter = signal<'all' | 'verified' | 'unverified'>('all');

  ngOnInit(): void {
    this.store.loadRestaurants();
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
