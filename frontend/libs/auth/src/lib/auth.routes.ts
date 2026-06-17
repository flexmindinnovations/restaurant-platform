import { Route } from '@angular/router';
import { Placeholder } from '@app/shared';

export const authRoutes: Route[] = [
  {
    path: '',
    component: Placeholder,
    data: { title: 'Authentication', icon: 'lock' },
  },
];
