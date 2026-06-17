import { Route } from '@angular/router';
import { Placeholder } from '@app/shared';

export const usersRoutes: Route[] = [
  {
    path: '',
    component: Placeholder,
    data: { title: 'Users', icon: 'people' },
  },
];
