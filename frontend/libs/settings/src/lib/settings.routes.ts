import { Route } from '@angular/router';
import { Placeholder } from '@app/shared';

export const settingsRoutes: Route[] = [
  {
    path: '',
    component: Placeholder,
    data: { title: 'Settings', icon: 'settings' },
  },
];
