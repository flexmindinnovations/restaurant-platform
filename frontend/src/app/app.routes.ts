import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full',
  },
  {
    path: 'auth',
    loadChildren: () => import('@app/auth').then((m) => m.authRoutes),
  },
  {
    path: 'dashboard',
    loadChildren: () => import('@app/dashboard').then((m) => m.dashboardRoutes),
  },
  {
    path: 'users',
    loadChildren: () => import('@app/users').then((m) => m.usersRoutes),
  },
  {
    path: 'restaurants',
    loadChildren: () => import('@app/restaurants').then((m) => m.restaurantsRoutes),
  },
  {
    path: 'orders',
    loadChildren: () => import('@app/orders').then((m) => m.ordersRoutes),
  },
  {
    path: 'deliveries',
    loadChildren: () => import('@app/deliveries').then((m) => m.deliveriesRoutes),
  },
  {
    path: 'payments',
    loadChildren: () => import('@app/payments').then((m) => m.paymentsRoutes),
  },
  {
    path: 'promotions',
    loadChildren: () => import('@app/promotions').then((m) => m.promotionsRoutes),
  },
  {
    path: 'reviews',
    loadChildren: () => import('@app/reviews').then((m) => m.reviewsRoutes),
  },
  {
    path: 'analytics',
    loadChildren: () => import('@app/analytics').then((m) => m.analyticsRoutes),
  },
  {
    path: 'settings',
    loadChildren: () => import('@app/settings').then((m) => m.settingsRoutes),
  },
  {
    path: 'support',
    loadChildren: () => import('@app/support').then((m) => m.supportRoutes),
  },
  {
    path: '**',
    redirectTo: 'dashboard',
  },
];
