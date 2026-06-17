import { Route } from '@angular/router';
import { Placeholder } from '@app/shared';

export const restaurantsRoutes: Route[] = [
  {
    path: '',
    component: Placeholder,
    data: { title: 'Restaurants', icon: 'storefront' },
  },
];
