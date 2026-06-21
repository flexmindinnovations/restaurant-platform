import { ChangeDetectionStrategy, Component, effect, inject, input } from '@angular/core';
import { HeaderService } from './services/header.service';

@Component({
  selector: 'app-page-header',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="page-header-actions">
      <ng-content />
    </div>
  `,
  styles: `
    :host {
      display: block;
      margin-bottom: 16px;
    }
    .page-header-actions:empty {
      display: none;
    }
    .page-header-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      justify-content: flex-end;
    }
  `,
})
export class PageHeader {
  private readonly headerService = inject(HeaderService);

  readonly title = input.required<string>();
  readonly subtitle = input<string>();

  constructor() {
    effect(() => {
      this.headerService.setHeader(this.title(), this.subtitle() || '');
    });
  }
}
