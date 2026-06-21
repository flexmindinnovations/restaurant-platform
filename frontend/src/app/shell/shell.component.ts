import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  OnDestroy,
  inject,
  ChangeDetectorRef,
} from '@angular/core';
import {
  RouterLink,
  RouterLinkActive,
  RouterOutlet,
  Router,
  NavigationEnd,
  NavigationStart,
  NavigationCancel,
  NavigationError,
} from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { HeaderService, ThemeService } from '@app/shared';
import { type Theme } from '@app/shared';
import { AuthService, DecodedToken } from '@app/auth';
import { Subscription } from 'rxjs';
import { SettingsStore } from '@app/settings';
import {
  LucideUser,
  LucideSettings,
  LucideLogOut,
  LucideDynamicIcon,
  LucideLayoutDashboard,
  LucideReceipt,
  LucideStore,
  LucideTruck,
  LucideCreditCard,
  LucideUsers,
  LucideTags,
  LucideStar,
  LucideBarChart3,
  LucideBell,
  LucideChevronDown,
  LucideUtensilsCrossed,
  LucideShieldAlert,
  LucideLogIn,
  LucideServer,
  LucidePanelLeftClose,
  LucidePanelLeftOpen,
  LucideSun,
  LucideMoon,
  LucideMonitor,
  LucideMenu,
  provideLucideIcons,
} from '@lucide/angular';

interface NavItem {
  path: string;
  label: string;
  icon: string;
}

interface NotificationItem {
  id: string;
  title: string;
  body: string;
  time: string;
  unread: boolean;
  icon: string;
  color: string;
  route?: string;
}

const NAV_LABEL_MAP: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/orders': 'Orders',
  '/restaurants': 'Restaurants',
  '/deliveries': 'Deliveries',
  '/payments': 'Payments',
  '/users': 'Users',
  '/promotions': 'Promotions',
  '/reviews': 'Reviews',
  '/analytics': 'Analytics',
  '/settings': 'Settings',
  '/support': 'Support',
};

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    MatSidenavModule,
    MatListModule,
    MatButtonModule,
    MatMenuModule,
    MatDividerModule,
    MatTooltipModule,
    MatProgressBarModule,
    LucideUser,
    LucideSettings,
    LucideLogOut,
    LucideDynamicIcon,
    LucideBell,
    LucideChevronDown,
    LucideUtensilsCrossed,
    LucideShieldAlert,
    LucideLogIn,
    LucidePanelLeftClose,
    LucidePanelLeftOpen,
    LucideSun,
    LucideMoon,
    LucideMonitor,
    LucideMenu,
  ],
  providers: [
    provideLucideIcons(
      LucideLayoutDashboard,
      LucideReceipt,
      LucideStore,
      LucideTruck,
      LucideCreditCard,
      LucideUsers,
      LucideTags,
      LucideStar,
      LucideBarChart3,
      LucideSettings,
      LucideServer,
    ),
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './shell.component.html',
  styleUrl: './shell.component.scss',
})
export class Shell implements OnInit, OnDestroy {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly cdr = inject(ChangeDetectorRef);
  protected readonly settingsStore = inject(SettingsStore);
  protected readonly headerService = inject(HeaderService);
  protected readonly themeService = inject(ThemeService);

  private routerSub?: Subscription;
  private sessionCheckInterval?: ReturnType<typeof setInterval>;

  sidebarCollapsed = false;
  mobileSidebarOpen = false;
  isNavigating = false;

  readonly mainNavItems: NavItem[] = [
    { path: '/dashboard', label: 'Dashboard', icon: 'layout-dashboard' },
    { path: '/orders', label: 'Orders', icon: 'receipt' },
    { path: '/restaurants', label: 'Restaurants', icon: 'store' },
    { path: '/deliveries', label: 'Deliveries', icon: 'truck' },
    { path: '/payments', label: 'Payments', icon: 'credit-card' },
  ];

  readonly secondaryNavItems: NavItem[] = [
    { path: '/users', label: 'Users', icon: 'users' },
    { path: '/promotions', label: 'Promotions', icon: 'tags' },
    { path: '/reviews', label: 'Reviews', icon: 'star' },
    { path: '/analytics', label: 'Analytics', icon: 'bar-chart-3' },
    { path: '/settings', label: 'Settings', icon: 'settings' },
  ];

  userEmail = '';
  userRole = '';
  showSessionExpired = false;

  notifications: NotificationItem[] = [
    {
      id: '1',
      title: 'New Order Received',
      body: 'Order #1024 has been placed at My Pasta Place.',
      time: '5 mins ago',
      unread: true,
      icon: 'receipt',
      color: 'var(--color-primary, #4caf50)',
      route: '/orders',
    },
    {
      id: '2',
      title: 'Registration Pending',
      body: 'My Gourmet 58a2 is waiting for admin verification.',
      time: '2 hours ago',
      unread: true,
      icon: 'store',
      color: 'var(--color-tertiary, #9c27b0)',
      route: '/restaurants',
    },
    {
      id: '3',
      title: 'System Update',
      body: 'Database migration to restaurant_db completed.',
      time: '1 day ago',
      unread: false,
      icon: 'server',
      color: '#757575',
      route: '/settings',
    },
  ];

  get unreadNotificationsCount(): number {
    return this.notifications.filter((n) => n.unread).length;
  }

  markAllAsRead(event: Event): void {
    event.stopPropagation();
    this.notifications = this.notifications.map((n) => ({ ...n, unread: false }));
    this.cdr.markForCheck();
  }

  onNotificationClick(item: NotificationItem): void {
    this.notifications = this.notifications.map((n) =>
      n.id === item.id ? { ...n, unread: false } : n,
    );
    this.cdr.markForCheck();
    if (item.route) {
      this.router.navigate([item.route]);
    }
  }

  clearNotification(id: string, event: Event): void {
    event.stopPropagation();
    this.notifications = this.notifications.filter((n) => n.id !== id);
    this.cdr.markForCheck();
  }

  toggleSidebar(): void {
    this.sidebarCollapsed = !this.sidebarCollapsed;
  }

  setTheme(theme: Theme): void {
    this.themeService.setTheme(theme);
  }

  ngOnInit(): void {
    this.settingsStore.loadSettings();
    this.loadUserInfo();
    this.trackCurrentPage();
    this.startSessionMonitor();
  }

  ngOnDestroy(): void {
    this.routerSub?.unsubscribe();
    if (this.sessionCheckInterval) {
      clearInterval(this.sessionCheckInterval);
    }
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/auth']);
  }

  goToLogin(): void {
    this.authService.logout();
    this.showSessionExpired = false;
    this.router.navigate(['/auth']);
  }

  private loadUserInfo(): void {
    const token: DecodedToken | null = this.authService.getDecodedToken();
    if (token) {
      const roles: string[] = token.roles || [];
      const isSuperAdmin = roles.includes('SUPER_ADMIN');
      this.userEmail = isSuperAdmin ? 'Admin' : token.sub || 'Unknown User';
      this.userRole = this.formatRole(roles[0] ?? '');
    }
  }

  private formatRole(role: string): string {
    return (
      role
        .replace(/_/g, ' ')
        .toLowerCase()
        .replace(/\b\w/g, (c) => c.toUpperCase()) || 'Staff'
    );
  }

  private trackCurrentPage(): void {
    this.routerSub = this.router.events.subscribe((e) => {
      if (e instanceof NavigationStart) {
        this.isNavigating = true;
        this.cdr.markForCheck();
      } else if (e instanceof NavigationEnd) {
        this.isNavigating = false;
        this.mobileSidebarOpen = false;
        const segment = '/' + (e.urlAfterRedirects.split('/')[1] ?? '');
        const fallbackTitle = NAV_LABEL_MAP[segment] ?? 'Overview';
        this.headerService.setHeader(fallbackTitle, '');
        this.cdr.markForCheck();
      } else if (e instanceof NavigationCancel || e instanceof NavigationError) {
        this.isNavigating = false;
        this.cdr.markForCheck();
      }
    });

    // Set immediately for current URL
    const segment = '/' + (this.router.url.split('/')[1] ?? '');
    const fallbackTitle = NAV_LABEL_MAP[segment] ?? 'Overview';
    this.headerService.setHeader(fallbackTitle, '');
  }

  private startSessionMonitor(): void {
    this.sessionCheckInterval = setInterval(() => {
      if (!this.authService.isLoggedIn() && !this.showSessionExpired) {
        this.showSessionExpired = true;
        this.cdr.markForCheck();
      }
    }, 30000); // check every 30s
  }
}
