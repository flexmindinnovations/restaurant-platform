import { Route } from '@angular/router';
import { Placeholder } from '@app/shared';

export const deliveriesRoutes: Route[] = [
  {
    path: '',
    component: Placeholder,
    data: { title: 'Deliveries', icon: 'local_shipping' },
  },
];
