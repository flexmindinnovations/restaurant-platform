import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import {
  LucideDynamicIcon,
  LucideInbox,
  LucideReceipt,
  LucideStore,
  LucideUsers,
  LucideStar,
  LucideTag,
  LucideUtensilsCrossed,
  provideLucideIcons,
} from '@lucide/angular';

@Component({
  selector: 'app-empty-state',
  standalone: true,
  imports: [LucideDynamicIcon],
  providers: [
    provideLucideIcons(
      LucideInbox,
      LucideReceipt,
      LucideStore,
      LucideUsers,
      LucideStar,
      LucideTag,
      LucideUtensilsCrossed,
    ),
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="empty-state">
      <svg [lucideIcon]="icon()" class="empty-state__icon"></svg>
      <h3 class="empty-state__title">{{ title() }}</h3>
      @if (message()) {
        <p class="empty-state__message">{{ message() }}</p>
      }
      <ng-content />
    </div>
  `,
  styles: `
    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 64px 24px;
      text-align: center;
      color: var(--color-text-secondary);
    }
    .empty-state__icon {
      width: 56px;
      height: 56px;
      opacity: 0.4;
      margin-bottom: 16px;
    }
    .empty-state__title {
      margin: 0 0 8px;
      font-size: 1.125rem;
      font-weight: 500;
    }
    .empty-state__message {
      margin: 0;
      font-size: 0.875rem;
      opacity: 0.75;
      max-width: 360px;
    }
  `,
})
export class EmptyState {
  readonly icon = input<string>('inbox');
  readonly title = input.required<string>();
  readonly message = input<string>();
}
