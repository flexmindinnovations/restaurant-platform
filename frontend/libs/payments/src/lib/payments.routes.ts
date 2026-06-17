import { Route } from '@angular/router';
import { Placeholder } from '@app/shared';

export const paymentsRoutes: Route[] = [
  {
    path: '',
    component: Placeholder,
    data: { title: 'Payments', icon: 'payments' },
  },
];
