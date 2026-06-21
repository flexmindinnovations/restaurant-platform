import { Injectable } from '@angular/core';
import { Observable, of, delay } from 'rxjs';
import { PlatformSettings } from './settings.model';

const DEFAULT_SETTINGS: PlatformSettings = {
  commission_rate: 10,
  delivery_radius_km: 15,
  min_order_value: 12.0,
  base_delivery_fee: 3.5,
  service_fee: 1.5,
  ai_provider: 'Gemini',
  ai_api_key: '',
  logo_url: '',
  brand_name: '',
};

@Injectable({ providedIn: 'root' })
export class SettingsService {
  private settings: PlatformSettings = { ...DEFAULT_SETTINGS };

  constructor() {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('quickbite_settings');
      if (stored) {
        try {
          this.settings = JSON.parse(stored);
        } catch {
          this.settings = { ...DEFAULT_SETTINGS };
        }
      } else {
        localStorage.setItem('quickbite_settings', JSON.stringify(this.settings));
      }
    }
  }

  getSettings(): Observable<PlatformSettings> {
    return of({ ...this.settings }).pipe(delay(200));
  }

  saveSettings(newSettings: PlatformSettings): Observable<PlatformSettings> {
    this.settings = { ...newSettings };
    if (typeof window !== 'undefined') {
      localStorage.setItem('quickbite_settings', JSON.stringify(this.settings));
    }
    return of({ ...this.settings }).pipe(delay(300));
  }
}
