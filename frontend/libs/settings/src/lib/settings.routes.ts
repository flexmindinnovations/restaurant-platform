import { Route } from '@angular/router';
import { SettingsDashboardComponent } from './settings-dashboard.component';

export const settingsRoutes: Route[] = [
  {
    path: '',
    component: SettingsDashboardComponent,
    data: { title: 'Settings', icon: 'settings' },
  },
];
