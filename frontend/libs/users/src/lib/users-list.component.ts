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
import { MatSelectModule } from '@angular/material/select';
import { MatCardModule } from '@angular/material/card';
import { PageHeader } from '../../../shared/src/lib/page-header';
import { StatusBadge } from '../../../shared/src/lib/status-badge';
import { EmptyState } from '../../../shared/src/lib/empty-state';
import { UsersStore } from './users.store';
import { User, UserRole } from './users.model';

@Component({
  selector: 'app-users-list',
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
    MatSelectModule,
    MatCardModule,
    PageHeader,
    StatusBadge,
    EmptyState,
  ],
  template: `
    <app-page-header title="Users Management" subtitle="Manage user accounts, roles, and access settings">
    </app-page-header>

    <!-- Filters -->
    <div class="filters-row">
      <mat-form-field appearance="outline" class="search-field">
        <mat-label>Search users</mat-label>
        <mat-icon matPrefix>search</mat-icon>
        <input matInput [ngModel]="searchValue()" (ngModelChange)="onSearch($event)"
          placeholder="Name, email, phone…" id="user-search" />
      </mat-form-field>

      <mat-chip-listbox [ngModel]="roleFilter()" (ngModelChange)="onRoleFilter($event)"
        class="filter-chips" aria-label="Role filter">
        <mat-chip-option value="ALL">All Roles</mat-chip-option>
        <mat-chip-option value="SUPER_ADMIN">Admin</mat-chip-option>
        <mat-chip-option value="RESTAURANT_OWNER">Owner</mat-chip-option>
        <mat-chip-option value="DELIVERY_PARTNER">Delivery</mat-chip-option>
        <mat-chip-option value="CUSTOMER">Customer</mat-chip-option>
      </mat-chip-listbox>
    </div>

    <!-- Loading bar -->
    @if (store.loading()) {
      <mat-progress-bar mode="indeterminate" />
    }

    <div class="workspace-layout">
      <!-- Table Container -->
      <div class="table-container mat-elevation-z1" [class.table-container--shrunk]="store.selectedUser()">
        @if (!store.loading() && !store.hasResults()) {
          <app-empty-state icon="people" title="No users found"
            message="Try adjusting your search or filters." />
        } @else {
          <table mat-table [dataSource]="store.users()" class="full-width">
            <!-- Avatar/Name -->
            <ng-container matColumnDef="name">
              <th mat-header-cell *matHeaderCellDef>User</th>
              <td mat-cell *matCellDef="let u">
                <div class="user-info-cell">
                  <img [src]="u.avatar_url || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=80'" 
                       alt="avatar" class="user-avatar" />
                  <div class="user-meta">
                    <span class="user-name">{{ u.display_name }}</span>
                    <span class="user-email">{{ u.email }}</span>
                  </div>
                </div>
              </td>
            </ng-container>

            <!-- Roles -->
            <ng-container matColumnDef="roles">
              <th mat-header-cell *matHeaderCellDef>Roles</th>
              <td mat-cell *matCellDef="let u">
                <div class="role-chips-container">
                  @for (r of u.roles; track r) {
                    <span class="role-badge" [class]="'role-badge--' + r.toLowerCase()">{{ r }}</span>
                  }
                </div>
              </td>
            </ng-container>

            <!-- Status -->
            <ng-container matColumnDef="status">
              <th mat-header-cell *matHeaderCellDef>Status</th>
              <td mat-cell *matCellDef="let u">
                <app-status-badge [status]="u.is_active ? 'ACTIVE' : 'INACTIVE'" />
              </td>
            </ng-container>

            <!-- Date Registered -->
            <ng-container matColumnDef="created_at">
              <th mat-header-cell *matHeaderCellDef>Joined</th>
              <td mat-cell *matCellDef="let u">
                {{ u.created_at | date: 'mediumDate' }}
              </td>
            </ng-container>

            <!-- Actions -->
            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef></th>
              <td mat-cell *matCellDef="let u">
                <button mat-icon-button (click)="onSelectUser(u, $event)"
                  matTooltip="View detail" aria-label="View user detail">
                  <mat-icon>chevron_right</mat-icon>
                </button>
              </td>
            </ng-container>

            <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
            <tr mat-row *matRowDef="let row; columns: displayedColumns"
              class="table-row" [class.table-row--selected]="store.selectedUser()?.id === row.id"
              (click)="onSelectUser(row, $event)"></tr>
          </table>

          <mat-paginator
            [length]="store.total()"
            [pageSize]="store.limit()"
            [pageSizeOptions]="[5, 10, 20]"
            (page)="onPage($event)"
            aria-label="Users pagination">
          </mat-paginator>
        }
      </div>

      <!-- Detail Sidenav Panel -->
      @if (store.selectedUser(); as selected) {
        <mat-card class="detail-panel mat-elevation-z3">
          <mat-card-header class="detail-header">
            <mat-card-title>User Details</mat-card-title>
            <button mat-icon-button (click)="store.clearSelected()" aria-label="Close detail panel">
              <mat-icon>close</mat-icon>
            </button>
          </mat-card-header>
          
          <mat-card-content class="detail-content">
            <div class="profile-section">
              <img [src]="selected.avatar_url || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150'" 
                   alt="Avatar" class="detail-avatar" />
              <h3>{{ selected.display_name }}</h3>
              <p class="joined-date">Member since {{ selected.created_at | date:'longDate' }}</p>
            </div>

            <div class="info-block">
              <label>Email</label>
              <span>{{ selected.email }}</span>
            </div>

            <div class="info-block">
              <label>Phone Number</label>
              <span>{{ selected.phone_number }}</span>
            </div>

            <div class="info-block">
              <label>Account Status</label>
              <div class="status-toggle-container">
                <app-status-badge [status]="selected.is_active ? 'ACTIVE' : 'INACTIVE'" />
                <button mat-stroked-button [color]="selected.is_active ? 'warn' : 'primary'"
                  (click)="onToggleStatus(selected.id)">
                  {{ selected.is_active ? 'Deactivate' : 'Activate' }}
                </button>
              </div>
            </div>

            <div class="info-block">
              <label>Primary Role</label>
              <mat-form-field appearance="outline" class="full-width">
                <mat-select [value]="selected.roles[0]" (selectionChange)="onChangeRole(selected.id, $event.value)">
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
    .filter-chips { display: flex; gap: 8px; }
    
    .workspace-layout {
      display: flex;
      gap: 16px;
      align-items: flex-start;
      position: relative;
    }

    .table-container {
      flex: 1;
      border-radius: 8px;
      overflow: hidden;
      background: var(--mat-sys-surface, #fff);
      transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .table-container--shrunk {
      max-width: calc(100% - 380px);
    }
    .full-width { width: 100%; }
    .table-row { cursor: pointer; }
    .table-row:hover { background: var(--mat-sys-surface-variant, #f5f5f5); }
    .table-row--selected { background: var(--mat-sys-surface-container-high, #e0f2f1) !important; }

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
      color: var(--mat-sys-on-surface, #333);
    }
    .user-email {
      font-size: 0.8rem;
      color: var(--mat-sys-on-surface-variant, #666);
    }

    .role-chips-container {
      display: flex;
      gap: 4px;
    }
    .role-badge {
      font-size: 0.7rem;
      font-weight: 600;
      padding: 2px 6px;
      border-radius: 4px;
      text-transform: uppercase;
    }
    .role-badge--super_admin { background: #ede7f6; color: #5e35b1; }
    .role-badge--restaurant_owner { background: #e8f5e9; color: #2e7d32; }
    .role-badge--delivery_partner { background: #fff8e1; color: #f57f17; }
    .role-badge--customer { background: #eceff1; color: #37474f; }

    .detail-panel {
      width: 360px;
      flex-shrink: 0;
      border-radius: 8px;
      background: var(--mat-sys-surface, #fff);
      animation: slideIn 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .detail-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--mat-sys-outline-variant, #e0e0e0);
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
      border-bottom: 1px solid var(--mat-sys-outline-variant, #f0f0f0);
    }
    .detail-avatar {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      object-fit: cover;
      margin-bottom: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .profile-section h3 {
      margin: 4px 0;
      font-size: 1.15rem;
      font-weight: 600;
    }
    .joined-date {
      font-size: 0.75rem;
      color: #888;
      margin: 0;
    }

    .info-block {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .info-block label {
      font-size: 0.75rem;
      font-weight: 500;
      color: #888;
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
      from { transform: translateX(20px); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  `,
})
export class UsersList implements OnInit {
  protected readonly store = inject(UsersStore);
  protected readonly displayedColumns = ['name', 'roles', 'status', 'created_at', 'actions'];

  protected readonly searchValue = signal('');
  protected readonly roleFilter = signal<UserRole | 'ALL'>('ALL');

  ngOnInit(): void {
    this.store.loadUsers();
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

  onSelectUser(user: User, event: Event): void {
    event.stopPropagation();
    this.store.selectUser(user);
  }

  onToggleStatus(id: string): void {
    this.store.toggleUserStatus(id);
  }

  onChangeRole(id: string, newRole: UserRole): void {
    this.store.updateUserRole({ id, roles: [newRole] });
  }
}
