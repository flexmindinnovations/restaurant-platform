import { Component, inject, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import {
  LucideDynamicIcon,
  LucideSun,
  LucideMoon,
  LucideMonitor,
  provideLucideIcons,
} from '@lucide/angular';
import { ThemeService, type Theme } from '../services/theme.service';

@Component({
  selector: 'app-theme-toggle',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatMenuModule, LucideDynamicIcon],
  providers: [provideLucideIcons(LucideSun, LucideMoon, LucideMonitor)],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <button
      mat-icon-button
      [matMenuTriggerFor]="themeMenu"
      [attr.aria-label]="'Switch theme'"
      class="theme-toggle"
    >
      <svg [lucideIcon]="currentThemeIcon()" class="toggle-icon"></svg>
    </button>

    <mat-menu #themeMenu="matMenu" class="theme-menu">
      @for (option of themeOptions; track option.value) {
        <button
          mat-menu-item
          (click)="setTheme(option.value)"
          [class.active]="themeService.theme$() === option.value"
        >
          <svg [lucideIcon]="option.icon" class="menu-icon"></svg>
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

    .toggle-icon,
    .menu-icon {
      width: 20px;
      height: 20px;
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
    { value: 'light' as Theme, label: 'Light', icon: 'sun' },
    { value: 'dark' as Theme, label: 'Dark', icon: 'moon' },
    { value: 'system' as Theme, label: 'System', icon: 'monitor' },
  ];

  currentThemeIcon() {
    const theme = this.themeService.theme$();
    const computed = this.themeService.getComputedTheme();

    if (theme === 'system') {
      return 'monitor';
    }
    return computed === 'dark' ? 'moon' : 'sun';
  }

  setTheme(theme: Theme): void {
    this.themeService.setTheme(theme);
  }
}
