import { Component, ChangeDetectionStrategy } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ThemeProviderComponent } from '@app/shared';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, ThemeProviderComponent],
  templateUrl: './app.html',
  styleUrl: './app.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {}
