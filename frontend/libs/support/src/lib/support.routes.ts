import { Route } from '@angular/router';
import { Placeholder } from '@app/shared';

export const supportRoutes: Route[] = [
  {
    path: '',
    component: Placeholder,
    data: { title: 'Support', icon: 'help' },
  },
];
