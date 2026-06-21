import { Route } from '@angular/router';
import { DeliveriesListComponent } from './deliveries-list.component';
import { DeliveriesDetailComponent } from './deliveries-detail.component';

export const deliveriesRoutes: Route[] = [
  {
    path: '',
    component: DeliveriesListComponent,
    data: { title: 'Deliveries', icon: 'local_shipping' },
  },
  {
    path: ':id',
    component: DeliveriesDetailComponent,
    data: { title: 'Delivery Details', icon: 'local_shipping' },
  },
];
