import { Route } from '@angular/router';
import { TablesPage } from './tables-page';
import { ReservationsPage } from './reservations-page';
import { WaitlistPage } from './waitlist-page';

export const tablesRoutes: Route[] = [
  { path: '', component: TablesPage },
  { path: 'reservations', component: ReservationsPage },
  { path: 'waitlist', component: WaitlistPage },
];
