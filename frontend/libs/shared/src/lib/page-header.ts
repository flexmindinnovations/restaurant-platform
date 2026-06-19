import { ChangeDetectionStrategy, Component, input } from '@angular/core';

@Component({
  selector: 'app-page-header',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="page-header">
      <div class="page-header-text">
        <h1 class="page-title">{{ title() }}</h1>
        @if (subtitle()) {
          <p class="page-subtitle">{{ subtitle() }}</p>
        }
      </div>
      <div class="page-header-actions">
        <ng-content />
      </div>
    </div>
  `,
  styles: `
    .page-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 24px;
    }

    .page-title {
      margin: 0;
      font-size: 22px;
      font-weight: 700;
      color: var(--color-text-primary);
      line-height: 1.2;
      letter-spacing: -0.02em;
    }

    .page-subtitle {
      margin: 4px 0 0;
      font-size: 13px;
      color: var(--color-text-tertiary);
      line-height: 1.4;
    }

    .page-header-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
    }
  `,
})
export class PageHeader {
  readonly title = input.required<string>();
  readonly subtitle = input<string>();
}
