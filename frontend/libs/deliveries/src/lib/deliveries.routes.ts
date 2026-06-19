import { Route } from '@angular/router';
import { DeliveriesMapComponent } from './deliveries-map.component';

export const deliveriesRoutes: Route[] = [
  {
    path: '',
    component: DeliveriesMapComponent,
    data: { title: 'Deliveries', icon: 'local_shipping' },
  },
];
