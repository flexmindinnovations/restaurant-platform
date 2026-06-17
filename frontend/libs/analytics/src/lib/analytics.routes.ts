import { Route } from '@angular/router';
import { Placeholder } from '@app/shared';

export const analyticsRoutes: Route[] = [
  {
    path: '',
    component: Placeholder,
    data: { title: 'Analytics', icon: 'bar_chart' },
  },
];
