import { Injectable, effect, inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { signal } from '@angular/core';

export type Theme = 'light' | 'dark' | 'system';

/**
 * Theme Service
 * Manages application theme (light/dark mode)
 * Respects system preferences with manual override capability
 */
@Injectable({
  providedIn: 'root',
})
export class ThemeService {
  private platformId = inject(PLATFORM_ID);
  private isBrowser = isPlatformBrowser(this.platformId);
  private theme = signal<Theme>(this.getInitialTheme());
  theme$ = this.theme.asReadonly();

  private effectInitialized = false;

  constructor() {
    // Initialize effect to apply theme changes to DOM
    if (!this.effectInitialized && this.isBrowser) {
      effect(() => {
        this.applyTheme(this.theme());
        this.effectInitialized = true;
      });
    }
  }

  /**
   * Get initial theme from localStorage or system preference
   */
  private getInitialTheme(): Theme {
    if (!this.isBrowser) return 'system';
    
    try {
      // Try to get saved preference
      const saved = localStorage?.getItem('theme') as Theme;
      if (saved && ['light', 'dark', 'system'].includes(saved)) {
        return saved;
      }
    } catch (e) {
      // localStorage may not be available
    }

    // Default to system
    return 'system';
  }

  /**
   * Set theme and persist to localStorage
   */
  setTheme(theme: Theme): void {
    this.theme.set(theme);
    if (this.isBrowser) {
      try {
        localStorage?.setItem('theme', theme);
      } catch (e) {
        // localStorage may not be available
      }
    }
  }

  /**
   * Get computed theme (resolved system preference if needed)
   */
  getComputedTheme(): 'light' | 'dark' {
    const theme = this.theme();
    if (theme === 'system' && this.isBrowser) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return theme === 'system' ? 'light' : theme;
  }

  /**
   * Toggle between light and dark (goes to manual control)
   */
  toggleTheme(): void {
    const computed = this.getComputedTheme();
    this.setTheme(computed === 'light' ? 'dark' : 'light');
  }

  /**
   * Apply theme to DOM
   */
  private applyTheme(theme: Theme): void {
    if (!this.isBrowser) return;
    
    const computed = theme === 'system' 
      ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
      : theme;

    const root = document.documentElement;
    
    if (computed === 'dark') {
      root.classList.add('dark');
      root.classList.remove('light');
    } else {
      root.classList.add('light');
      root.classList.remove('dark');
    }
  }

  /**
   * Listen to system theme changes when in 'system' mode
   */
  listenToSystemPreference(): void {
    if (!this.isBrowser) return;
    
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (this.theme() === 'system') {
        this.applyTheme('system');
      }
    });
  }
}
