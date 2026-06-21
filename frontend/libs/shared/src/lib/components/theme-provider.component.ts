import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ThemeService } from '../services/theme.service';

/**
 * Theme Provider Component
 * Initializes theme on app startup and listens to system preference changes
 * Should be placed at root level (in app component)
 */
@Component({
  selector: 'app-theme-provider',
  standalone: true,
  imports: [CommonModule],
  template: '',
  styles: [],
})
export class ThemeProviderComponent implements OnInit {
  private themeService = inject(ThemeService);

  ngOnInit(): void {
    // Initialize theme on app startup
    const theme = this.themeService.theme$;

    // Listen to system preference changes
    this.themeService.listenToSystemPreference();
  }
}
