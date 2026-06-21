import { Injectable, signal } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class HeaderService {
  readonly title = signal<string>('Dashboard');
  readonly subtitle = signal<string>('');
  readonly loading = signal<boolean>(false);

  setHeader(title: string, subtitle: string): void {
    this.title.set(title);
    this.subtitle.set(subtitle || '');
  }

  setLoading(loading: boolean): void {
    this.loading.set(loading);
  }
}
