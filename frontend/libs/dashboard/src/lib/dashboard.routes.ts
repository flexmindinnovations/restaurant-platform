import { Route } from '@angular/router';
import { Placeholder } from '@app/shared';

export const dashboardRoutes: Route[] = [
  {
    path: '',
    component: Placeholder,
    data: { title: 'Dashboard', icon: 'dashboard' },
  },
];
