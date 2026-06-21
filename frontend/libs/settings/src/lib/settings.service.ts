import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { PlatformSettings } from './settings.model';

@Injectable({ providedIn: 'root' })
export class SettingsService {
  private readonly http = inject(HttpClient);

  getSettings(): Observable<PlatformSettings> {
    return this.http
      .get<{ data: PlatformSettings }>('/api/v1/settings')
      .pipe(map((res) => res.data));
  }

  saveSettings(newSettings: PlatformSettings): Observable<PlatformSettings> {
    return this.http
      .put<{ data: PlatformSettings }>('/api/v1/settings', newSettings)
      .pipe(map((res) => res.data));
  }
}
