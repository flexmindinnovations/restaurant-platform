import { Route } from '@angular/router';
import { RestaurantsList } from './restaurants-list';
import { RestaurantDetail } from './restaurant-detail';
import { MenusPage } from './menus-page.component';

export const restaurantsRoutes: Route[] = [
  {
    path: '',
    component: RestaurantsList,
  },
  {
    path: ':id',
    component: RestaurantDetail,
  },
  {
    path: ':id/menus',
    component: MenusPage,
  },
];
