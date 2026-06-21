import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';

export type CardVariant = 'elevated' | 'outlined' | 'flat';
export type CardSize = 'sm' | 'md' | 'lg';

@Component({
  selector: 'app-glass-card',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div [ngClass]="cardClasses">
      <ng-content />
    </div>
  `,
  styles: `
    :host {
      display: block;
    }

    .card {
      border-radius: 0;
      transition:
        box-shadow 150ms ease,
        border-color 150ms ease;

      /* Elevated — primary card style */
      &.variant-elevated {
        background: var(--color-surface-1);
        border: 1px solid var(--color-border);

        &:hover {
          border-color: var(--color-border);
          box-shadow: var(--shadow-md);
        }
      }

      /* Outlined — subtle border, transparent bg */
      &.variant-outlined {
        background: transparent;
        border: 1px solid var(--color-border);

        &:hover {
          background: var(--color-surface-1);
        }
      }

      /* Flat — no border, blends into background */
      &.variant-flat {
        background: var(--color-surface-2);
        border: 1px solid transparent;
      }

      /* Sizing */
      &.size-sm {
        padding: 12px;
      }
      &.size-md {
        padding: 16px;
      }
      &.size-lg {
        padding: 24px;
      }
    }
  `,
})
export class GlassCardComponent {
  @Input() variant: CardVariant | 'glass' | 'solid' | 'outline' = 'elevated';
  @Input() size: CardSize = 'md';
  @Input() class: string = '';

  get cardClasses(): Record<string, boolean> {
    const v = this.mapVariant(this.variant);
    return {
      card: true,
      [`variant-${v}`]: true,
      [`size-${this.size}`]: true,
      ...this.parseClasses(),
    };
  }

  private mapVariant(v: string): string {
    if (v === 'glass' || v === 'solid') return 'elevated';
    if (v === 'outline') return 'outlined';
    return v;
  }

  private parseClasses(): Record<string, boolean> {
    return this.class.split(' ').reduce(
      (acc, cls) => {
        if (cls) acc[cls] = true;
        return acc;
      },
      {} as Record<string, boolean>,
    );
  }
}
