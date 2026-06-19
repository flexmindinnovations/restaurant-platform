import { Component, inject, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { ThemeService, type Theme } from '../services/theme.service';

/**
 * Theme Toggle Component
 * Displays current theme and allows user to switch between light/dark/system
 * Uses Material menu for clean UI
 */
@Component({
  selector: 'app-theme-toggle',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule, MatMenuModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <button
      mat-icon-button
      [matMenuTriggerFor]="themeMenu"
      [attr.aria-label]="'Switch theme'"
      class="theme-toggle"
    >
      <mat-icon>
        {{ currentThemeIcon() }}
      </mat-icon>
    </button>

    <mat-menu #themeMenu="matMenu" class="theme-menu">
      @for (option of themeOptions; track option.value) {
        <button
          mat-menu-item
          (click)="setTheme(option.value)"
          [class.active]="themeService.theme$() === option.value"
        >
          <mat-icon>{{ option.icon }}</mat-icon>
          <span>{{ option.label }}</span>
        </button>
      }
    </mat-menu>
  `,
  styles: `
    .theme-toggle {
      transition: var(--duration-base) ease-out;
      
      &:hover {
        background-color: var(--color-bg-secondary);
      }
    }

    .theme-menu {
      min-width: 150px;
    }

    .mat-mdc-menu-item.active {
      font-weight: var(--font-weight-semibold);
      color: var(--color-primary);
    }
  `,
})
export class ThemeToggleComponent {
  themeService = inject(ThemeService);

  themeOptions = [
    { value: 'light' as Theme, label: 'Light', icon: 'light_mode' },
    { value: 'dark' as Theme, label: 'Dark', icon: 'dark_mode' },
    { value: 'system' as Theme, label: 'System', icon: 'brightness_auto' },
  ];

  currentThemeIcon() {
    const theme = this.themeService.theme$();
    const computed = this.themeService.getComputedTheme();
    
    if (theme === 'system') {
      return 'brightness_auto';
    }
    return computed === 'dark' ? 'dark_mode' : 'light_mode';
  }

  setTheme(theme: Theme): void {
    this.themeService.setTheme(theme);
  }
}
