import { Component, ChangeDetectionStrategy } from '@angular/core';

/**
 * Card Content Component
 * Container for card body content with proper spacing
 */
@Component({
  selector: 'app-card-content',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<ng-content />`,
  styles: `
    :host {
      display: block;
    }
  `,
})
export class CardContentComponent {}
