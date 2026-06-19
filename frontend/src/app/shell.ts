import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import { MatDividerModule } from '@angular/material/divider';
import { ThemeToggleComponent } from '@app/shared';

interface NavItem {
  path: string;
  label: string;
  icon: string;
}

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    MatSidenavModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatMenuModule,
    MatDividerModule,
    ThemeToggleComponent,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="shell">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <div class="logo">
            <div class="logo-mark">
              <mat-icon>restaurant</mat-icon>
            </div>
            <div class="logo-text">
              <span class="logo-name">Restaurant</span>
              <span class="logo-label">Admin</span>
            </div>
          </div>
        </div>

        <nav class="nav-section">
          @for (item of mainNavItems; track item.path) {
            <a
              [routerLink]="item.path"
              routerLinkActive="nav-active"
              [routerLinkActiveOptions]="{ exact: false }"
              class="nav-item"
            >
              <mat-icon class="nav-icon">{{ item.icon }}</mat-icon>
              <span class="nav-label">{{ item.label }}</span>
            </a>
          }
        </nav>

        <div class="nav-divider"></div>

        <nav class="nav-section">
          @for (item of secondaryNavItems; track item.path) {
            <a
              [routerLink]="item.path"
              routerLinkActive="nav-active"
              [routerLinkActiveOptions]="{ exact: false }"
              class="nav-item"
            >
              <mat-icon class="nav-icon">{{ item.icon }}</mat-icon>
              <span class="nav-label">{{ item.label }}</span>
            </a>
          }
        </nav>

        <div class="sidebar-footer">
          <app-theme-toggle />
        </div>
      </aside>

      <!-- Main area -->
      <div class="main-area">
        <!-- Top bar -->
        <header class="topbar">
          <div class="topbar-left">
            <span class="topbar-title">Overview</span>
          </div>
          <div class="topbar-right">
            <button mat-icon-button class="topbar-btn" aria-label="Notifications">
              <mat-icon>notifications_none</mat-icon>
              <span class="notif-dot"></span>
            </button>
            <button mat-icon-button [matMenuTriggerFor]="userMenu" class="topbar-btn" aria-label="User menu">
              <mat-icon>account_circle</mat-icon>
            </button>
          </div>
        </header>

        <!-- Page content -->
        <main class="page-content">
          <router-outlet />
        </main>
      </div>
    </div>

    <mat-menu #userMenu="matMenu">
      <button mat-menu-item>
        <mat-icon>person</mat-icon>
        <span>Profile</span>
      </button>
      <button mat-menu-item>
        <mat-icon>settings</mat-icon>
        <span>Settings</span>
      </button>
      <mat-divider />
      <button mat-menu-item>
        <mat-icon>logout</mat-icon>
        <span>Logout</span>
      </button>
    </mat-menu>
  `,
  styles: `
    .shell {
      display: flex;
      height: 100vh;
      background: var(--color-surface-0);
    }

    /* ── Sidebar ─────────────────────────────── */
    .sidebar {
      width: 240px;
      flex-shrink: 0;
      display: flex;
      flex-direction: column;
      background: var(--color-surface-1);
      border-right: 1px solid var(--color-border);
      overflow-y: auto;
    }

    .sidebar-header {
      padding: 16px;
      border-bottom: 1px solid var(--color-border);
    }

    .logo {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .logo-mark {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      background: var(--color-primary);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;

      mat-icon {
        font-size: 18px;
        width: 18px;
        height: 18px;
      }
    }

    .logo-name {
      font-size: 15px;
      font-weight: 700;
      color: var(--color-text-primary);
      line-height: 1.2;
    }

    .logo-label {
      font-size: 11px;
      font-weight: 500;
      color: var(--color-text-tertiary);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      line-height: 1;
      display: block;
    }

    /* Navigation */
    .nav-section {
      padding: 8px;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 12px;
      border-radius: 8px;
      text-decoration: none;
      color: var(--color-text-secondary);
      font-size: 13px;
      font-weight: 500;
      transition: all 150ms ease;
      position: relative;

      &:hover {
        background: var(--color-surface-2);
        color: var(--color-text-primary);
      }

      &.nav-active {
        background: var(--color-primary-subtle);
        color: var(--color-primary);

        &::before {
          content: '';
          position: absolute;
          left: 0;
          top: 8px;
          bottom: 8px;
          width: 3px;
          border-radius: 0 3px 3px 0;
          background: var(--color-primary);
        }

        .nav-icon {
          color: var(--color-primary);
        }
      }
    }

    .nav-icon {
      font-size: 20px;
      width: 20px;
      height: 20px;
      color: var(--color-text-tertiary);
      transition: color 150ms ease;
    }

    .nav-label {
      flex: 1;
    }

    .nav-divider {
      height: 1px;
      background: var(--color-border);
      margin: 4px 16px;
    }

    .sidebar-footer {
      margin-top: auto;
      padding: 12px 16px;
      border-top: 1px solid var(--color-border);
    }

    /* ── Main area ───────────────────────────── */
    .main-area {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-width: 0;
      overflow: hidden;
    }

    .topbar {
      height: 48px;
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
      background: var(--color-surface-1);
      border-bottom: 1px solid var(--color-border);
    }

    .topbar-title {
      font-size: 13px;
      font-weight: 500;
      color: var(--color-text-secondary);
    }

    .topbar-right {
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .topbar-btn {
      color: var(--color-text-tertiary);
      position: relative;

      &:hover {
        color: var(--color-text-primary);
      }
    }

    .notif-dot {
      position: absolute;
      top: 10px;
      right: 10px;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--color-error);
      border: 2px solid var(--color-surface-1);
    }

    .page-content {
      flex: 1;
      overflow-y: auto;
      padding: 24px;
    }

    /* ── Responsive ──────────────────────────── */
    @media (max-width: 1024px) {
      .sidebar {
        width: 200px;
      }
    }

    @media (max-width: 768px) {
      .sidebar {
        display: none;
      }

      .page-content {
        padding: 16px;
      }
    }
  `,
})
export class Shell {
  mainNavItems: NavItem[] = [
    { path: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
    { path: '/orders', label: 'Orders', icon: 'receipt_long' },
    { path: '/restaurants', label: 'Restaurants', icon: 'storefront' },
    { path: '/deliveries', label: 'Deliveries', icon: 'local_shipping' },
    { path: '/payments', label: 'Payments', icon: 'payments' },
  ];

  secondaryNavItems: NavItem[] = [
    { path: '/users', label: 'Users', icon: 'people' },
    { path: '/promotions', label: 'Promotions', icon: 'local_offer' },
    { path: '/reviews', label: 'Reviews', icon: 'star_rate' },
    { path: '/analytics', label: 'Analytics', icon: 'bar_chart' },
    { path: '/settings', label: 'Settings', icon: 'settings' },
  ];
}
