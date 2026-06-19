import { Route } from '@angular/router';
import { ReviewsListComponent } from './reviews-list.component';

export const reviewsRoutes: Route[] = [
  {
    path: '',
    component: ReviewsListComponent,
    data: { title: 'Reviews', icon: 'star_rate' },
  },
];
