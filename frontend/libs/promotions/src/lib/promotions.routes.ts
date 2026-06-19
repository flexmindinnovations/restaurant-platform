import { Route } from '@angular/router';
import { PromotionsDashboardComponent } from './promotions-dashboard.component';

export const promotionsRoutes: Route[] = [
  {
    path: '',
    component: PromotionsDashboardComponent,
    data: { title: 'Promotions', icon: 'local_offer' },
  },
];
