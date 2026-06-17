import { Route } from '@angular/router';
import { Placeholder } from '@app/shared';

export const promotionsRoutes: Route[] = [
  {
    path: '',
    component: Placeholder,
    data: { title: 'Promotions', icon: 'local_offer' },
  },
];
