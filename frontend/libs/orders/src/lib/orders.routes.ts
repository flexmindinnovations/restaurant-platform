import { Route } from '@angular/router';
import { Placeholder } from '@app/shared';

export const ordersRoutes: Route[] = [
  {
    path: '',
    component: Placeholder,
    data: { title: 'Orders', icon: 'receipt_long' },
  },
];
