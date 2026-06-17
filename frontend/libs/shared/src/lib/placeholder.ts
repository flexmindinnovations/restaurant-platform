import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-placeholder',
  standalone: true,
  imports: [MatCardModule, MatIconModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <mat-card appearance="outlined">
      <mat-card-content class="placeholder">
        <mat-icon class="placeholder-icon">{{ icon() }}</mat-icon>
        <h1>{{ title() }}</h1>
        <p>This module is ready for development.</p>
      </mat-card-content>
    </mat-card>
  `,
  styles: `
    .placeholder {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 64px 24px;
      text-align: center;
    }
    .placeholder-icon {
      font-size: 48px;
      width: 48px;
      height: 48px;
      opacity: 0.5;
      margin-bottom: 16px;
    }
    h1 {
      margin: 0 0 8px;
      font-weight: 500;
    }
    p {
      margin: 0;
      opacity: 0.7;
    }
  `,
})
export class Placeholder {
  readonly title = input.required<string>();
  readonly icon = input<string>('construction');
}
