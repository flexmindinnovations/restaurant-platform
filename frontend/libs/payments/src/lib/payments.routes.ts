import { Route } from '@angular/router';
import { PaymentsListComponent } from './payments-list.component';

export const paymentsRoutes: Route[] = [
  {
    path: '',
    component: PaymentsListComponent,
    data: { title: 'Payments', icon: 'payment' },
  },
];
