import { ChangeDetectionStrategy, Component, effect, inject, OnInit, signal } from '@angular/core';
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
  LucideImage,
  LucideUpload,
  LucideUtensilsCrossed,
  LucideSave,
  LucideLoader2,
  LucideKey,
  LucideBuilding2,
} from '@lucide/angular';
import { MatSelectModule } from '@angular/material/select';
import { PageHeader } from '../../../shared/src/lib/page-header';
import { SettingsStore } from './settings.store';
import { PlatformSettings } from './settings.model';

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
    LucideImage,
    LucideUpload,
    LucideUtensilsCrossed,
    LucideSave,
    LucideLoader2,
    LucideKey,
    LucideBuilding2,
    MatSelectModule,
    PageHeader,
  ],
  template: `
    <app-page-header
      title="Platform Configuration"
      subtitle="Configure system parameters, fee structures, and service limits"
    >
    </app-page-header>

    @if (store.settings(); as currentSettings) {
      <div class="settings-container">
        <!-- Left Column: Form Card -->
        <mat-card class="settings-card mat-elevation-z1" appearance="outlined">
          <mat-card-header>
            <mat-card-title>System Values</mat-card-title>
          </mat-card-header>

          <mat-card-content class="form-content">
            @if (store.successMessage(); as msg) {
              <div class="alert alert--success">
                <svg lucideCircleCheck [size]="18"></svg>
                <span>{{ msg }}</span>
              </div>
            }

            @if (store.error(); as err) {
              <div class="alert alert--error">
                <svg lucideCircleAlert [size]="18"></svg>
                <span>{{ err }}</span>
              </div>
            }

            <form
              #settingsForm="ngForm"
              (ngSubmit)="onSubmit(settingsForm.value)"
              class="settings-form"
            >
              <!-- Fee Structure Section -->
              <h3 class="section-title">Fee & Commission Rates</h3>
              <div class="form-grid">
                <mat-form-field appearance="outline">
                  <mat-label>Commission Rate (%)</mat-label>
                  <input
                    matInput
                    type="number"
                    name="commission_rate"
                    [ngModel]="currentSettings.commission_rate"
                    required
                    min="0"
                    max="100"
                  />
                  <span matSuffix>%</span>
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>Base Delivery Fee (₹)</mat-label>
                  <input
                    matInput
                    type="number"
                    name="base_delivery_fee"
                    [ngModel]="currentSettings.base_delivery_fee"
                    required
                    min="0"
                    step="0.1"
                  />
                  <span matPrefix>₹</span>
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>Platform Service Fee (₹)</mat-label>
                  <input
                    matInput
                    type="number"
                    name="service_fee"
                    [ngModel]="currentSettings.service_fee"
                    required
                    min="0"
                    step="0.1"
                  />
                  <span matPrefix>₹</span>
                </mat-form-field>
              </div>

              <!-- Logistics Rules Section -->
              <h3 class="section-title mt-4">Logistics & Service Rules</h3>
              <div class="form-grid">
                <mat-form-field appearance="outline">
                  <mat-label>Max Delivery Radius (km)</mat-label>
                  <input
                    matInput
                    type="number"
                    name="delivery_radius_km"
                    [ngModel]="currentSettings.delivery_radius_km"
                    required
                    min="1"
                  />
                  <span matSuffix>km</span>
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>Minimum Order Value (₹)</mat-label>
                  <input
                    matInput
                    type="number"
                    name="min_order_value"
                    [ngModel]="currentSettings.min_order_value"
                    required
                    min="0"
                    step="0.5"
                  />
                  <span matPrefix>₹</span>
                </mat-form-field>
              </div>

              <!-- Branding Section -->
              <h3 class="section-title mt-4">Branding & Identity</h3>
              <div class="form-grid">
                <mat-form-field appearance="outline">
                  <mat-label>Brand Name</mat-label>
                  <input
                    matInput
                    name="brand_name"
                    [(ngModel)]="brandName"
                    placeholder="e.g. QuickBite"
                  />
                  <svg lucideBuilding2 [size]="18" matSuffix></svg>
                </mat-form-field>
                <div class="logo-uploader-field">
                  <mat-form-field appearance="outline" class="w-full">
                    <mat-label>Restaurant Logo URL</mat-label>
                    <input
                      matInput
                      type="url"
                      name="logo_url"
                      [(ngModel)]="logoUrl"
                      placeholder="e.g. https://example.com/logo.png"
                    />
                    <svg lucideImage [size]="18" matSuffix></svg>
                  </mat-form-field>

                  <div class="file-picker-actions">
                    <input
                      type="file"
                      #fileInput
                      (change)="onFileSelected($event)"
                      accept="image/*"
                      style="display: none;"
                    />
                    <button mat-stroked-button type="button" (click)="fileInput.click()">
                      <svg lucideUpload [size]="18"></svg>
                      Choose Local Image...
                    </button>
                    @if (logoUrl) {
                      <div class="logo-preview-box">
                        <img [src]="logoUrl" alt="Preview" />
                      </div>
                    }
                  </div>
                </div>
              </div>

              <!-- AI Service Section -->
              <h3 class="section-title mt-4">AI Assistant Settings</h3>
              <div class="form-grid">
                <mat-form-field appearance="outline">
                  <mat-label>AI Provider</mat-label>
                  <mat-select name="ai_provider" [ngModel]="currentSettings.ai_provider" required>
                    <mat-option value="Gemini">Gemini</mat-option>
                    <mat-option value="OpenAI">OpenAI</mat-option>
                  </mat-select>
                </mat-form-field>

                <mat-form-field appearance="outline" class="col-span-2">
                  <mat-label>API Key</mat-label>
                  <input
                    matInput
                    type="password"
                    name="ai_api_key"
                    [ngModel]="currentSettings.ai_api_key"
                  />
                  <svg lucideKey [size]="18" matSuffix></svg>
                </mat-form-field>
              </div>

              <div class="form-actions mt-4">
                <button
                  mat-flat-button
                  color="primary"
                  type="submit"
                  [disabled]="settingsForm.invalid || store.saving()"
                >
                  @if (store.saving()) {
                    <svg lucideLoader2 [size]="18"></svg> Saving...
                  } @else {
                    <svg lucideSave [size]="18"></svg> Save Settings
                  }
                </button>
              </div>
            </form>
          </mat-card-content>
        </mat-card>

        <!-- Right Column: Premium Live Branding Preview Card -->
        <mat-card
          class="settings-card branding-preview-card mat-elevation-z1"
          appearance="outlined"
        >
          <mat-card-header>
            <mat-card-title>Branding & Fees Preview</mat-card-title>
          </mat-card-header>
          <mat-card-content class="form-content preview-content">
            <div class="preview-logo-wrapper">
              @if (logoUrl) {
                <img [src]="logoUrl" alt="Brand Logo" class="preview-brand-logo" />
              } @else {
                <div class="preview-logo-placeholder">
                  <svg lucideUtensilsCrossed class="placeholder-icon"></svg>
                </div>
              }
            </div>
            <div class="preview-brand-name">QuickBite Admin</div>
            <div class="preview-badge">Active Identity</div>

            <div class="preview-divider"></div>

            <div class="preview-details">
              <div class="preview-detail-item">
                <span class="detail-label">Commission Fee</span>
                <span class="detail-value text-green">{{ currentSettings.commission_rate }}%</span>
              </div>
              <div class="preview-detail-item">
                <span class="detail-label">Base Delivery</span>
                <span class="detail-value">₹{{ currentSettings.base_delivery_fee }}</span>
              </div>
              <div class="preview-detail-item">
                <span class="detail-label">Service Fee</span>
                <span class="detail-value">₹{{ currentSettings.service_fee }}</span>
              </div>
              <div class="preview-detail-item">
                <span class="detail-label">Min. Order</span>
                <span class="detail-value">₹{{ currentSettings.min_order_value }}</span>
              </div>
              <div class="preview-detail-item col-span-2">
                <span class="detail-label">Max Delivery Radius</span>
                <span class="detail-value">{{ currentSettings.delivery_radius_km }} km</span>
              </div>
            </div>
          </mat-card-content>
        </mat-card>
      </div>
    }
  `,
  styles: `
    .settings-container {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 24px;
      max-width: 1200px;
    }
    .settings-card {
      border-radius: 0;
      background: var(--color-surface-1);
      height: fit-content;
    }
    .branding-preview-card {
      position: sticky;
      top: 24px;
    }
    .form-content {
      padding: 24px !important;
    }
    .preview-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      padding: 32px 24px !important;
    }
    .preview-logo-wrapper {
      width: 96px;
      height: 96px;
      border-radius: 0;
      overflow: hidden;
      border: 2px dashed var(--color-border);
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--color-surface-2);
      margin-bottom: 16px;
      transition: all 0.3s ease;
      box-shadow: var(--shadow-sm);
    }
    .preview-brand-logo {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .preview-logo-placeholder {
      color: var(--color-text-tertiary);
      display: flex;
      align-items: center;
      justify-content: center;
      .placeholder-icon {
        width: 40px;
        height: 40px;
      }
    }
    .preview-brand-name {
      font-size: 18px;
      font-weight: 700;
      color: var(--color-text-primary);
      margin-bottom: 4px;
    }
    .preview-badge {
      font-size: 11px;
      font-weight: 600;
      color: var(--color-primary);
      background: var(--color-primary-subtle);
      padding: 4px 10px;
      border-radius: 0;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 24px;
    }
    .preview-divider {
      width: 100%;
      height: 1px;
      background: var(--color-border);
      margin-bottom: 20px;
    }
    .preview-details {
      width: 100%;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      text-align: left;
    }
    .preview-detail-item {
      display: flex;
      flex-direction: column;
      gap: 4px;
      padding: 10px;
      background: var(--color-surface-2);
      border-radius: 0;
      border: 1px solid var(--color-border-light);

      &.col-span-2 {
        grid-column: span 2;
      }
    }
    .detail-label {
      font-size: 10px;
      font-weight: 500;
      color: var(--color-text-tertiary);
      text-transform: uppercase;
      letter-spacing: 0.02em;
    }
    .detail-value {
      font-size: 13px;
      font-weight: 600;
      color: var(--color-text-primary);

      &.text-green {
        color: var(--color-primary);
      }
    }
    .settings-form {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .section-title {
      font-size: 1.05rem;
      font-weight: 600;
      color: var(--color-text-primary);
      border-bottom: 1px solid var(--color-border);
      padding-bottom: 8px;
      margin-bottom: 8px;
    }
    .form-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
    }
    .logo-uploader-field {
      display: flex;
      flex-direction: column;
      gap: 12px;
      grid-column: span 2;
    }
    .file-picker-actions {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .logo-preview-box {
      width: 48px;
      height: 48px;
      border-radius: 0;
      overflow: hidden;
      border: 1px solid var(--color-border);
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--color-surface-2);

      img {
        max-width: 100%;
        max-height: 100%;
        object-fit: cover;
      }
    }
    .alert {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 16px;
      border-radius: 0;
      margin-bottom: 20px;
      font-size: 0.9rem;
      font-weight: 500;
    }
    .alert--success {
      background: var(--color-success-bg);
      color: var(--color-success);
    }
    .alert--error {
      background: var(--color-error-bg);
      color: var(--color-error);
    }
    .form-actions {
      display: flex;
      justify-content: flex-start;
      margin-top: 16px;
    }
    .w-full {
      width: 100%;
    }
    .mb-4 {
      margin-bottom: 16px;
    }
    .mt-4 {
      margin-top: 16px;
    }
  `,
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

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      const file = input.files[0];
      const reader = new FileReader();
      reader.onload = () => {
        this.logoUrl = reader.result as string;
      };
      reader.readAsDataURL(file);
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
