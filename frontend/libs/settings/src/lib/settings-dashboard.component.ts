import { ChangeDetectionStrategy, Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
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
    MatIconModule,
    MatProgressBarModule,
    MatSelectModule,
    PageHeader,
  ],
  template: `
    <app-page-header title="Platform Configuration" subtitle="Configure system parameters, fee structures, and service limits">
    </app-page-header>

    @if (store.loading()) {
      <mat-progress-bar mode="indeterminate" class="mb-4" />
    }

    <div class="settings-container">
      <mat-card class="settings-card mat-elevation-z1" appearance="outlined">
        <mat-card-header>
          <mat-card-title>System Values</mat-card-title>
        </mat-card-header>
        
        <mat-card-content class="form-content">
          @if (store.successMessage(); as msg) {
            <div class="alert alert--success">
              <mat-icon>check_circle</mat-icon>
              <span>{{ msg }}</span>
            </div>
          }

          @if (store.error(); as err) {
            <div class="alert alert--error">
              <mat-icon>error</mat-icon>
              <span>{{ err }}</span>
            </div>
          }

          @if (store.settings(); as currentSettings) {
            <form #settingsForm="ngForm" (ngSubmit)="onSubmit(settingsForm.value)" class="settings-form">
              <!-- Fee Structure Section -->
              <h3 class="section-title">Fee & Commission Rates</h3>
              <div class="form-grid">
                <mat-form-field appearance="outline">
                  <mat-label>Commission Rate (%)</mat-label>
                  <input matInput type="number" name="commission_rate" 
                    [ngModel]="currentSettings.commission_rate" required min="0" max="100" />
                  <span matSuffix>%</span>
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>Base Delivery Fee ($)</mat-label>
                  <input matInput type="number" name="base_delivery_fee" 
                    [ngModel]="currentSettings.base_delivery_fee" required min="0" step="0.1" />
                  <span matPrefix>$</span>
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>Platform Service Fee ($)</mat-label>
                  <input matInput type="number" name="service_fee" 
                    [ngModel]="currentSettings.service_fee" required min="0" step="0.1" />
                  <span matPrefix>$</span>
                </mat-form-field>
              </div>

              <!-- Logistics Rules Section -->
              <h3 class="section-title mt-4">Logistics & Service Rules</h3>
              <div class="form-grid">
                <mat-form-field appearance="outline">
                  <mat-label>Max Delivery Radius (km)</mat-label>
                  <input matInput type="number" name="delivery_radius_km" 
                    [ngModel]="currentSettings.delivery_radius_km" required min="1" />
                  <span matSuffix>km</span>
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>Minimum Order Value ($)</mat-label>
                  <input matInput type="number" name="min_order_value" 
                    [ngModel]="currentSettings.min_order_value" required min="0" step="0.5" />
                  <span matPrefix>$</span>
                </mat-form-field>
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
                  <input matInput type="password" name="ai_api_key" 
                    [ngModel]="currentSettings.ai_api_key" />
                  <mat-icon matSuffix>vpn_key</mat-icon>
                </mat-form-field>
              </div>

              <div class="form-actions mt-4">
                <button mat-flat-button color="primary" type="submit" 
                  [disabled]="settingsForm.invalid || store.saving()">
                  <mat-icon>{{ store.saving() ? 'hourglass_empty' : 'save' }}</mat-icon>
                  {{ store.saving() ? 'Saving...' : 'Save Settings' }}
                </button>
              </div>
            </form>
          }
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: `
    .settings-container {
      max-width: 800px;
    }
    .settings-card {
      border-radius: 12px;
      background: var(--mat-sys-surface, #fff);
    }
    .form-content {
      padding: 24px !important;
    }
    .settings-form {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .section-title {
      font-size: 1.05rem;
      font-weight: 600;
      color: var(--mat-sys-on-surface, #333);
      border-bottom: 1px solid var(--mat-sys-outline-variant, #e0e0e0);
      padding-bottom: 8px;
      margin-bottom: 8px;
    }
    .form-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
    }

    .alert {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 16px;
      border-radius: 8px;
      margin-bottom: 20px;
      font-size: 0.9rem;
      font-weight: 500;
    }
    .alert--success {
      background: #e8f5e9;
      color: #2e7d32;
    }
    .alert--error {
      background: #ffebee;
      color: #c62828;
    }

    .form-actions {
      display: flex;
      justify-content: flex-start;
      margin-top: 16px;
    }

    .mb-4 { margin-bottom: 16px; }
    .mt-4 { margin-top: 16px; }
  `,
})
export class SettingsDashboardComponent implements OnInit {
  protected readonly store = inject(SettingsStore);

  ngOnInit(): void {
    this.store.loadSettings();
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
    };
    this.store.saveSettings(settingsPayload);

    // Auto clear success alert after 4 seconds
    setTimeout(() => {
      this.store.clearMessages();
    }, 4000);
  }
}
