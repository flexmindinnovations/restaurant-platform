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
import { LucideSearch, LucideChevronRight, LucideX } from '@lucide/angular';

import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSelectModule } from '@angular/material/select';
import { MatCardModule } from '@angular/material/card';
import { PageHeader } from '../../../shared/src/lib/page-header';
import { HeaderService } from '@app/shared';
import { StatusBadge } from '../../../shared/src/lib/status-badge';
import { EmptyState } from '../../../shared/src/lib/empty-state';
import { DatatableComponent, DatatableCellDirective, DatatableColumn } from '@app/design-system';
import { UsersStore } from './users.store';
import { User, UserRole } from './users.model';

@Component({
  selector: 'app-users-list',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    FormsModule,
    MatInputModule,
    MatFormFieldModule,
    MatButtonModule,
    MatChipsModule,
    LucideSearch,
    LucideChevronRight,
    LucideX,
    MatTooltipModule,
    MatSelectModule,
    MatCardModule,
    PageHeader,
    StatusBadge,
    EmptyState,
    DatatableComponent,
    DatatableCellDirective,
  ],
  template: `
    <app-page-header
      title="Users Management"
      subtitle="Manage user accounts, roles, and access settings"
    >
    </app-page-header>

    <!-- Filters -->
    <div class="filters-row">
      <mat-form-field appearance="outline" class="search-field" subscriptSizing="dynamic">
        <mat-label>Search users</mat-label>
        <svg lucideSearch [size]="18" matIconPrefix></svg>
        <input
          matInput
          [ngModel]="searchValue()"
          (ngModelChange)="onSearch($event)"
          placeholder="Name, email, phone…"
          id="user-search"
        />
      </mat-form-field>

      <mat-chip-listbox
        [ngModel]="roleFilter()"
        (ngModelChange)="onRoleFilter($event)"
        class="filter-chips"
        aria-label="Role filter"
      >
        <mat-chip-option value="ALL">All Roles</mat-chip-option>
        <mat-chip-option value="SUPER_ADMIN">Admin</mat-chip-option>
        <mat-chip-option value="RESTAURANT_OWNER">Owner</mat-chip-option>
        <mat-chip-option value="DELIVERY_PARTNER">Delivery</mat-chip-option>
        <mat-chip-option value="CUSTOMER">Customer</mat-chip-option>
      </mat-chip-listbox>
    </div>

    <div class="workspace-layout">
      <!-- Table Container -->
      <div
        class="table-wrapper-container"
        [class.table-wrapper-container--shrunk]="store.selectedUser()"
      >
        @if (!store.loading() && !store.hasResults()) {
          <app-empty-state
            icon="users"
            title="No users found"
            message="Try adjusting your search or filters."
          />
        } @else {
          <app-datatable
            [dataSource]="store.users()"
            [columns]="columns"
            [total]="store.total()"
            [pageSize]="store.limit()"
            [selectedRowId]="store.selectedUser()?.id"
            selectedRowClass="table-row--selected"
            (pageChange)="onPage($event)"
            (rowClick)="onSelectUser($event)"
            paginatorAriaLabel="Users pagination"
          >
            <!-- Avatar/Name -->
            <ng-template appDatatableCell="name" let-row>
              <div class="user-info-cell">
                <img
                  [src]="
                    row.avatar_url ||
                    'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=80'
                  "
                  alt="avatar"
                  class="user-avatar"
                />
                <div class="user-meta">
                  <span class="user-name">{{ row.display_name }}</span>
                  <span class="user-email">{{ row.email }}</span>
                </div>
              </div>
            </ng-template>

            <!-- Roles -->
            <ng-template appDatatableCell="roles" let-row>
              <div class="role-chips-container">
                @for (r of row.roles; track r) {
                  <span class="role-badge" [class]="'role-badge--' + r.toLowerCase()">{{
                    r
                  }}</span>
                }
              </div>
            </ng-template>

            <!-- Status -->
            <ng-template appDatatableCell="status" let-row>
              <app-status-badge [status]="row.is_active ? 'ACTIVE' : 'INACTIVE'" />
            </ng-template>

            <!-- Date Registered -->
            <ng-template appDatatableCell="created_at" let-row>
              {{ row.created_at | date: 'mediumDate' }}
            </ng-template>

            <!-- Actions -->
            <ng-template appDatatableCell="actions" let-row>
              <button
                mat-icon-button
                (click)="onSelectUser(row, $event)"
                matTooltip="View detail"
                aria-label="View user detail"
              >
                <svg lucideChevronRight [size]="16" style="color: var(--color-text-secondary)"></svg>
              </button>
            </ng-template>
          </app-datatable>
        }
      </div>

      <!-- Detail Sidenav Panel -->
      @if (store.selectedUser(); as selected) {
        <mat-card class="detail-panel mat-elevation-z3">
          <mat-card-header class="detail-header">
            <mat-card-title>User Details</mat-card-title>
            <button mat-icon-button (click)="store.clearSelected()" aria-label="Close detail panel">
              <svg lucideX [size]="18"></svg>
            </button>
          </mat-card-header>

          <mat-card-content class="detail-content">
            <div class="profile-section">
              <img
                [src]="
                  selected.avatar_url ||
                  'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150'
                "
                alt="Avatar"
                class="detail-avatar"
              />
              <h3>{{ selected.display_name }}</h3>
              <p class="joined-date">Member since {{ selected.created_at | date: 'longDate' }}</p>
            </div>

            <div class="info-block">
              <span class="info-label">Email</span>
              <span>{{ selected.email }}</span>
            </div>

            <div class="info-block">
              <span class="info-label">Phone Number</span>
              <span>{{ selected.phone_number }}</span>
            </div>

            <div class="info-block">
              <span class="info-label">Account Status</span>
              <div class="status-toggle-container">
                <app-status-badge [status]="selected.is_active ? 'ACTIVE' : 'INACTIVE'" />
                <button
                  mat-stroked-button
                  [color]="selected.is_active ? 'warn' : 'primary'"
                  (click)="onToggleStatus(selected.id)"
                >
                  {{ selected.is_active ? 'Deactivate' : 'Activate' }}
                </button>
              </div>
            </div>

            <div class="info-block">
              <label for="role-select" class="info-label">Primary Role</label>
              <mat-form-field appearance="outline" class="full-width">
                <mat-select
                  id="role-select"
                  [value]="selected.roles[0]"
                  (selectionChange)="onChangeRole(selected.id, $event.value)"
                >
                  <mat-option value="CUSTOMER">Customer</mat-option>
                  <mat-option value="DELIVERY_PARTNER">Delivery Partner</mat-option>
                  <mat-option value="RESTAURANT_OWNER">Restaurant Owner</mat-option>
                  <mat-option value="SUPER_ADMIN">Super Admin</mat-option>
                </mat-select>
              </mat-form-field>
            </div>
          </mat-card-content>
        </mat-card>
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

    .workspace-layout {
      display: flex;
      gap: 16px;
      align-items: flex-start;
      position: relative;
    }

    .table-wrapper-container {
      flex: 1;
      min-width: 0;
      transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .table-wrapper-container--shrunk {
      max-width: calc(100% - 380px);
    }
    .table-row--selected {
      background: var(--color-teal-bg) !important;
    }

    .user-info-cell {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 6px 0;
    }
    .user-avatar {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      object-fit: cover;
    }
    .user-meta {
      display: flex;
      flex-direction: column;
    }
    .user-name {
      font-weight: 500;
      color: var(--color-text-primary);
    }
    .user-email {
      font-size: 0.8rem;
      color: var(--color-text-secondary);
    }

    .role-chips-container {
      display: flex;
      gap: 4px;
    }
    .role-badge {
      font-size: 0.7rem;
      font-weight: 600;
      padding: 2px 6px;
      border-radius: 0;
      text-transform: uppercase;
    }
    .role-badge--super_admin {
      background: var(--color-accent-subtle);
      color: var(--color-accent);
    }
    .role-badge--restaurant_owner {
      background: var(--color-success-bg);
      color: var(--color-success);
    }
    .role-badge--delivery_partner {
      background: var(--color-amber-bg);
      color: var(--color-amber-text);
    }
    .role-badge--customer {
      background: var(--color-grey-bg);
      color: var(--color-grey-text);
    }

    .detail-panel {
      width: 360px;
      flex-shrink: 0;
      border-radius: 0;
      background: var(--color-surface-1);
      animation: slideIn 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .detail-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--color-border);
      padding: 12px 16px;
    }
    .detail-content {
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .profile-section {
      text-align: center;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--color-border);
    }
    .detail-avatar {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      object-fit: cover;
      margin-bottom: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    .profile-section h3 {
      margin: 4px 0;
      font-size: 1.15rem;
      font-weight: 600;
    }
    .joined-date {
      font-size: 0.75rem;
      color: var(--color-text-tertiary);
      margin: 0;
    }

    .info-block {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .info-block label,
    .info-block .info-label {
      font-size: 0.75rem;
      font-weight: 500;
      color: var(--color-text-tertiary);
      text-transform: uppercase;
    }
    .info-block span {
      font-size: 0.95rem;
      word-break: break-all;
    }

    .status-toggle-container {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    @keyframes slideIn {
      from {
        transform: translateX(20px);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
  `,

})
export class UsersList implements OnInit, OnDestroy {
  protected readonly store = inject(UsersStore);
  private readonly headerService = inject(HeaderService);

  constructor() {
    effect(() => {
      this.headerService.setLoading(this.store.loading());
    });
  }
  protected readonly columns: DatatableColumn[] = [
    { key: 'name', label: 'User' },
    { key: 'roles', label: 'Roles' },
    { key: 'status', label: 'Status' },
    { key: 'created_at', label: 'Joined' },
    { key: 'actions', label: 'Actions' },
  ];

  protected readonly searchValue = signal('');
  protected readonly roleFilter = signal<UserRole | 'ALL'>('ALL');

  ngOnInit(): void {
    this.store.loadUsers();
  }

  ngOnDestroy(): void {
    this.headerService.setLoading(false);
  }

  onSearch(value: string): void {
    this.searchValue.set(value);
    this.store.setSearch(value);
    this.store.loadUsers();
  }

  onRoleFilter(value: UserRole | 'ALL'): void {
    this.roleFilter.set(value);
    this.store.setRoleFilter(value);
    this.store.loadUsers();
  }

  onPage(event: PageEvent): void {
    this.store.setPage(event.pageIndex);
    this.store.loadUsers();
  }

  onSelectUser(user: unknown, event?: Event): void {
    if (event) {
      event.stopPropagation();
    }
    this.store.selectUser(user as User);
  }

  onToggleStatus(id: string): void {
    this.store.toggleUserStatus(id);
  }

  onChangeRole(id: string, newRole: UserRole): void {
    this.store.updateUserRole({ id, roles: [newRole] });
  }
}
