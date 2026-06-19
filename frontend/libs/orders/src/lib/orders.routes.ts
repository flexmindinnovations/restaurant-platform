import { Route } from '@angular/router';
import { OrdersList } from './orders-list';

export const ordersRoutes: Route[] = [
  {
    path: '',
    component: OrdersList,
  },
];
