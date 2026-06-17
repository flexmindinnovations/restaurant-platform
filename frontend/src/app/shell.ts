import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    MatSidenavModule,
    MatToolbarModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <mat-sidenav-container class="shell">
      <mat-sidenav mode="side" opened class="sidenav">
        <div class="sidenav-header">
          <h2>Restaurant Platform</h2>
        </div>
        <mat-nav-list>
          @for (item of navItems; track item.path) {
            <a mat-list-item [routerLink]="item.path" routerLinkActive="active-link">
              <mat-icon matListItemIcon>{{ item.icon }}</mat-icon>
              <span matListItemTitle>{{ item.label }}</span>
            </a>
          }
        </mat-nav-list>
      </mat-sidenav>

      <mat-sidenav-content class="content">
        <mat-toolbar color="primary">
          <span>Admin Dashboard</span>
          <span class="toolbar-spacer"></span>
          <button mat-icon-button aria-label="Toggle dark mode">
            <mat-icon>dark_mode</mat-icon>
          </button>
        </mat-toolbar>
        <div class="page-content">
          <router-outlet />
        </div>
      </mat-sidenav-content>
    </mat-sidenav-container>
  `,
  styles: `
    .shell {
      height: 100vh;
    }
    .sidenav {
      width: 260px;
      border-right: 1px solid var(--mat-sys-outline-variant, #ccc);
    }
    .sidenav-header {
      padding: 16px 16px 8px;
    }
    .sidenav-header h2 {
      margin: 0;
      font-size: 1.125rem;
      font-weight: 600;
    }
    .toolbar-spacer {
      flex: 1 1 auto;
    }
    .page-content {
      padding: 24px;
    }
    .active-link {
      font-weight: 500;
    }
  `,
})
export class Shell {
  readonly navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
    { path: '/orders', label: 'Orders', icon: 'receipt_long' },
    { path: '/restaurants', label: 'Restaurants', icon: 'storefront' },
    { path: '/users', label: 'Users', icon: 'people' },
    { path: '/deliveries', label: 'Deliveries', icon: 'local_shipping' },
    { path: '/payments', label: 'Payments', icon: 'payments' },
    { path: '/promotions', label: 'Promotions', icon: 'local_offer' },
    { path: '/reviews', label: 'Reviews', icon: 'star_rate' },
    { path: '/analytics', label: 'Analytics', icon: 'bar_chart' },
    { path: '/settings', label: 'Settings', icon: 'settings' },
    { path: '/support', label: 'Support', icon: 'help' },
  ];
}
