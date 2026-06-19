import { Route } from '@angular/router';
import { AnalyticsDashboardComponent } from './analytics-dashboard.component';

export const analyticsRoutes: Route[] = [
  {
    path: '',
    component: AnalyticsDashboardComponent,
    data: { title: 'Analytics', icon: 'analytics' },
  },
];
