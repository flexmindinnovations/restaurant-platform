import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  LucideDynamicIcon,
  provideLucideIcons,
  LucideLayoutDashboard,
  LucideReceipt,
  LucideStore,
  LucideTruck,
  LucideCreditCard,
  LucideUsers,
  LucideTags,
  LucideStar,
  LucideBarChart3,
  LucideSettings,
} from '@lucide/angular';

@Component({
  selector: 'app-card-header',
  standalone: true,
  imports: [CommonModule, LucideDynamicIcon],
  providers: [
    provideLucideIcons(
      LucideLayoutDashboard,
      LucideReceipt,
      LucideStore,
      LucideTruck,
      LucideCreditCard,
      LucideUsers,
      LucideTags,
      LucideStar,
      LucideBarChart3,
      LucideSettings,
    ),
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="card-header">
      @if (icon) {
        <div class="header-icon">
          <svg [lucideIcon]="icon" class="header-icon-svg"></svg>
        </div>
      }
      <div class="header-text">
        <h3 class="header-title">{{ title }}</h3>
        @if (subtitle) {
          <p class="header-subtitle">{{ subtitle }}</p>
        }
      </div>
      <div class="header-actions">
        <ng-content />
      </div>
    </div>
  `,
  styles: `
    .card-header {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 12px;
    }

    .header-icon {
      width: 32px;
      height: 32px;
      border-radius: 0;
      background: var(--color-primary-subtle);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;

      .header-icon-svg {
        width: 18px;
        height: 18px;
        color: var(--color-primary);
      }
    }

    .header-text {
      flex: 1;
      min-width: 0;
    }

    .header-title {
      margin: 0;
      font-size: 14px;
      font-weight: 600;
      color: var(--color-text-primary);
      line-height: 1.3;
    }

    .header-subtitle {
      margin: 2px 0 0;
      font-size: 12px;
      color: var(--color-text-tertiary);
      line-height: 1.3;
    }

    .header-actions {
      margin-left: auto;
      display: flex;
      align-items: center;
      gap: 4px;
    }
  `,
})
export class CardHeaderComponent {
  @Input() title!: string;
  @Input() subtitle?: string;
  @Input() icon?: string;
}
