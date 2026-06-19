import { Route } from '@angular/router';
import { UsersList } from './users-list.component';

export const usersRoutes: Route[] = [
  {
    path: '',
    component: UsersList,
    data: { title: 'Users', icon: 'people' },
  },
];
