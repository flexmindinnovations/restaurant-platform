import { ChangeDetectionStrategy, Component, effect, inject, OnInit} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import {
  LucideCircleCheck,
  LucideCircleAlert,
  LucideUtensilsCrossed,
  LucideSave,
  LucideLoaderCircle,
  LucideKey,
  LucideBuilding2,
} from '@lucide/angular';
import { MatSelectModule } from '@angular/material/select';
import { PageHeader } from '@app/shared';
import { SettingsStore } from './settings.store';
import { PlatformSettings } from './settings.model';
import { ImagePicker } from "../../../shared/src/lib/image-picker";

@Component({
  selector: 'app-settings-dashboard',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatProgressBarModule,
    LucideCircleCheck,
    LucideCircleAlert,
    LucideUtensilsCrossed,
    LucideSave,
    LucideLoaderCircle,
    LucideKey,
    LucideBuilding2,
    MatSelectModule,
    PageHeader,
    ImagePicker,
],
  templateUrl: './settings-dashboard.component.html',
  styleUrl: './settings-dashboard.component.scss',
})
export class SettingsDashboardComponent implements OnInit {
  protected readonly store = inject(SettingsStore);
  logoUrl = '';
  brandName = '';

  constructor() {
    effect(() => {
      const s = this.store.settings();
      if (s) {
        this.logoUrl = s.logo_url || '';
        this.brandName = s.brand_name || '';
      }
    });
  }

  ngOnInit(): void {
    this.store.loadSettings();
  }

  onLogoChanged(images: string[]): void {
    if (images.length > 0) {
      this.logoUrl = images[0];
    } else {
      this.logoUrl = '';
    }
  }

  onSubmit(formValues: Partial<PlatformSettings>): void {
    const settingsPayload: PlatformSettings = {
      commission_rate: Number(formValues.commission_rate),
      delivery_radius_km: Number(formValues.delivery_radius_km),
      min_order_value: Number(formValues.min_order_value),
      base_delivery_fee: Number(formValues.base_delivery_fee),
      service_fee: Number(formValues.service_fee),
      ai_provider: (formValues.ai_provider as 'Gemini' | 'OpenAI') || 'Gemini',
      ai_api_key: formValues.ai_api_key || '',
      logo_url: this.logoUrl,
      brand_name: this.brandName,
    };
    this.store.saveSettings(settingsPayload);

    // Auto clear success alert after 4 seconds
    setTimeout(() => {
      this.store.clearMessages();
    }, 4000);
  }
}
