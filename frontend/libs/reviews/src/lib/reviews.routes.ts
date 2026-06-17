import { Route } from '@angular/router';
import { Placeholder } from '@app/shared';

export const reviewsRoutes: Route[] = [
  {
    path: '',
    component: Placeholder,
    data: { title: 'Reviews', icon: 'star_rate' },
  },
];
