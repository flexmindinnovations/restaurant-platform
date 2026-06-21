import {
  ChangeDetectionStrategy,
  Component,
  inject,
  OnInit,
  OnDestroy,
  effect,
  signal,
  computed,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import {
  LucidePlus,
  LucideTag,
  LucideCircleCheck,
  LucideGift,
  LucideIndianRupee,
  LucidePencil,
  LucideTrash2,
  LucideX,
} from '@lucide/angular';

import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { PageHeader } from '../../../shared/src/lib/page-header';
import { HeaderService } from '@app/shared';
import { EmptyState } from '../../../shared/src/lib/empty-state';
import { PromotionsStore } from './promotions.store';
import { Promotion } from './promotions.model';

@Component({
  selector: 'app-promotions-dashboard',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatTableModule,
    MatButtonModule,
    LucidePlus,
    LucideTag,
    LucideCircleCheck,
    LucideGift,
    LucideIndianRupee,
    LucidePencil,
    LucideTrash2,
    LucideX,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatChipsModule,
    MatTooltipModule,
    PageHeader,
    EmptyState,
  ],
  template: `
    <app-page-header
      title="Promotions & Coupons"
      subtitle="Manage discount coupons, platform campaigns, and view usage metrics"
    >
      <button mat-flat-button color="primary" (click)="onOpenCreateModal()">
        <svg lucidePlus [size]="18"></svg> Generate Coupon
      </button>
    </app-page-header>

    <!-- Statistics Dashboard -->
    <div class="stats-grid mb-6">
      <mat-card appearance="outlined" class="stat-card">
        <mat-card-header>
          <div class="stat-icon bg-blue-100 text-blue-700">
            <svg lucideTag [size]="24"></svg>
          </div>
          <div class="stat-info">
            <p class="stat-label">Total Coupons</p>
            <p class="stat-value">{{ totalCoupons() }}</p>
          </div>
        </mat-card-header>
      </mat-card>

      <mat-card appearance="outlined" class="stat-card">
        <mat-card-header>
          <div class="stat-icon bg-green-100 text-green-700">
            <svg lucideCircleCheck [size]="24"></svg>
          </div>
          <div class="stat-info">
            <p class="stat-label">Active Campaigns</p>
            <p class="stat-value">{{ activeCoupons() }}</p>
          </div>
        </mat-card-header>
      </mat-card>

      <mat-card appearance="outlined" class="stat-card">
        <mat-card-header>
          <div class="stat-icon bg-purple-100 text-purple-700">
            <svg lucideGift [size]="24"></svg>
          </div>
          <div class="stat-info">
            <p class="stat-label">Total Redeemed</p>
            <p class="stat-value">{{ totalRedeemed() }}</p>
          </div>
        </mat-card-header>
      </mat-card>

      <mat-card appearance="outlined" class="stat-card">
        <mat-card-header>
          <div class="stat-icon bg-amber-100 text-amber-700">
            <svg lucideIndianRupee [size]="24"></svg>
          </div>
          <div class="stat-info">
            <p class="stat-label">Total Saved by Users</p>
            <p class="stat-value">{{ totalSavings() | currency: 'INR' : 'symbol' : '1.0-0' }}</p>
          </div>
        </mat-card-header>
      </mat-card>
    </div>

    <!-- Main Section -->
    <div class="table-container mat-elevation-z1">
      @if (store.promotions().length === 0) {
        <app-empty-state
          icon="tag"
          title="No promotions found"
          message="Create your first discount campaign to boost user engagement."
        />
      } @else {
        <table mat-table [dataSource]="store.promotions()" class="full-width">
          <!-- Code -->
          <ng-container matColumnDef="code">
            <th mat-header-cell *matHeaderCellDef>Code</th>
            <td mat-cell *matCellDef="let promo" class="font-mono font-bold text-blue-700">
              {{ promo.code }}
            </td>
          </ng-container>

          <!-- Type & Value -->
          <ng-container matColumnDef="discount">
            <th mat-header-cell *matHeaderCellDef>Discount</th>
            <td mat-cell *matCellDef="let promo">
              @if (promo.discount_type === 'PERCENTAGE') {
                {{ promo.discount_value }}% OFF
              } @else {
                {{ promo.discount_value | currency: 'INR' : 'symbol' : '1.0-0' }} OFF
              }
            </td>
          </ng-container>

          <!-- Scope -->
          <ng-container matColumnDef="scope">
            <th mat-header-cell *matHeaderCellDef>Scope</th>
            <td mat-cell *matCellDef="let promo" class="text-sm opacity-90">
              {{ promo.restaurant_name }}
            </td>
          </ng-container>

          <!-- Min Order -->
          <ng-container matColumnDef="min_order">
            <th mat-header-cell *matHeaderCellDef>Min Order</th>
            <td mat-cell *matCellDef="let promo" class="text-sm">
              {{ promo.min_order_value | currency: 'INR' : 'symbol' : '1.0-0' }}
            </td>
          </ng-container>

          <!-- Usage -->
          <ng-container matColumnDef="usage">
            <th mat-header-cell *matHeaderCellDef>Usage Limit</th>
            <td mat-cell *matCellDef="let promo" class="text-sm">
              <span class="font-semibold">{{ promo.usage_count }}</span> /
              <span>{{ promo.max_usages || '∞' }}</span>
              <div class="usage-progress-bar mt-1">
                <div class="usage-progress-fill" [style.width.%]="getUsagePercentage(promo)"></div>
              </div>
            </td>
          </ng-container>

          <!-- Status -->
          <ng-container matColumnDef="status">
            <th mat-header-cell *matHeaderCellDef>Status</th>
            <td mat-cell *matCellDef="let promo">
              <span class="custom-badge" [class]="'badge-status--' + promo.status.toLowerCase()">
                {{ promo.status }}
              </span>
            </td>
          </ng-container>

          <!-- Dates -->
          <ng-container matColumnDef="dates">
            <th mat-header-cell *matHeaderCellDef>Validity</th>
            <td mat-cell *matCellDef="let promo" class="text-xs opacity-75">
              {{ promo.start_date }} to {{ promo.end_date }}
            </td>
          </ng-container>

          <!-- Actions -->
          <ng-container matColumnDef="actions">
            <th mat-header-cell *matHeaderCellDef>Actions</th>
            <td mat-cell *matCellDef="let promo">
              <div class="actions-cell">
                <button mat-icon-button (click)="onOpenEditModal(promo); $event.stopPropagation()" matTooltip="Edit coupon">
                  <svg lucidePencil [size]="16" style="color: var(--color-info)"></svg>
                </button>
                <button
                  mat-icon-button
                  (click)="onDelete(promo.id); $event.stopPropagation()"
                  matTooltip="Delete coupon"
                >
                  <svg lucideTrash2 [size]="16" style="color: var(--color-error)"></svg>
                </button>
              </div>
            </td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
          <tr mat-row *matRowDef="let row; columns: displayedColumns" class="table-row"></tr>
        </table>
      }
    </div>

    <!-- Create/Edit Coupon Modal -->
    @if (isModalOpen()) {
      <div class="modal-backdrop" (click)="onCloseModal()">
        <div class="modal-card" (click)="$event.stopPropagation()">
          <div class="modal-header">
            <h3>{{ editingPromo() ? 'Edit Campaign' : 'Generate New Coupon' }}</h3>
            <button mat-icon-button (click)="onCloseModal()">
              <svg lucideX [size]="18"></svg>
            </button>
          </div>

          <form #promoForm="ngForm" (ngSubmit)="onSubmit(promoForm.value)" class="modal-form">
            <div class="modal-body">
              <div class="form-grid">
                <mat-form-field appearance="outline">
                  <mat-label>Coupon Code</mat-label>
                  <input
                    matInput
                    name="code"
                    [ngModel]="formData().code"
                    required
                    placeholder="e.g. SUMMER25"
                  />
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>Discount Type</mat-label>
                  <mat-select name="discount_type" [ngModel]="formData().discount_type" required>
                    <mat-option value="PERCENTAGE">Percentage (%)</mat-option>
                    <mat-option value="FIXED">Fixed Amount ($)</mat-option>
                  </mat-select>
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>Discount Value</mat-label>
                  <input
                    matInput
                    type="number"
                    name="discount_value"
                    [ngModel]="formData().discount_value"
                    required
                    min="0"
                  />
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>Min Order Value ($)</mat-label>
                  <input
                    matInput
                    type="number"
                    name="min_order_value"
                    [ngModel]="formData().min_order_value"
                    min="0"
                    step="0.5"
                  />
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>Max Usages (Limit)</mat-label>
                  <input
                    matInput
                    type="number"
                    name="max_usages"
                    [ngModel]="formData().max_usages"
                    min="1"
                    placeholder="Unlimited if empty"
                  />
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>Scope (Restaurant ID)</mat-label>
                  <input
                    matInput
                    name="restaurant_id"
                    [ngModel]="formData().restaurant_id"
                    placeholder="Leave empty for Platform-wide"
                  />
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>Start Date</mat-label>
                  <input
                    matInput
                    type="date"
                    name="start_date"
                    [ngModel]="formData().start_date"
                    required
                  />
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>End Date</mat-label>
                  <input
                    matInput
                    type="date"
                    name="end_date"
                    [ngModel]="formData().end_date"
                    required
                  />
                </mat-form-field>

                <mat-form-field appearance="outline" class="col-span-2">
                  <mat-label>Status</mat-label>
                  <mat-select name="status" [ngModel]="formData().status" required>
                    <mat-option value="ACTIVE">ACTIVE</mat-option>
                    <mat-option value="PAUSED">PAUSED</mat-option>
                    <mat-option value="EXPIRED">EXPIRED</mat-option>
                  </mat-select>
                </mat-form-field>
              </div>
            </div>

            <div class="modal-footer justify-end">
              <button mat-button type="button" (click)="onCloseModal()">Cancel</button>
              <button mat-flat-button color="primary" type="submit" [disabled]="promoForm.invalid">
                {{ editingPromo() ? 'Save Changes' : 'Generate' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    }
  `,
  styles: `
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
    }
    .stat-card {
      border-radius: 0;
    }
    .stat-card mat-card-header {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 16px !important;
    }
    .stat-icon {
      width: 48px;
      height: 48px;
      border-radius: 0;
      display: flex;
      justify-content: center;
      align-items: center;
    }
    .stat-icon svg {
      width: 24px;
      height: 24px;
    }
    .stat-info {
      display: flex;
      flex-direction: column;
    }
    .stat-label {
      font-size: 0.8rem;
      color: var(--color-text-tertiary);
      margin: 0;
      text-transform: uppercase;
      font-weight: 500;
    }
    .stat-value {
      font-size: 1.5rem;
      font-weight: 700;
      margin: 0;
      color: var(--color-text-primary);
    }

    .table-container {
      border-radius: 0;
      overflow: hidden;
      background: var(--color-surface-1);
    }
    .full-width {
      width: 100%;
    }
    .table-row:hover {
      background: var(--color-surface-2);
    }

    .custom-badge {
      font-size: 0.72rem;
      font-weight: 600;
      padding: 3px 8px;
      border-radius: 0;
      text-transform: uppercase;
      display: inline-block;
    }
    .badge-status--active {
      background: var(--color-success-bg);
      color: var(--color-success);
    }
    .badge-status--paused {
      background: var(--color-orange-bg);
      color: var(--color-orange-text);
    }
    .badge-status--expired {
      background: var(--color-error-bg);
      color: var(--color-error);
    }

    .usage-progress-bar {
      width: 100%;
      height: 6px;
      background: var(--color-surface-2);
      border-radius: 0;
      overflow: hidden;
    }
    .usage-progress-fill {
      height: 100%;
      background: var(--color-success);
      border-radius: 0;
    }

    .actions-cell {
      display: flex;
      gap: 4px;
      justify-content: flex-end;
    }

    .modal-backdrop {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0, 0, 0, 0.42);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 1000;
    }
    .modal-card {
      background: var(--color-surface-1);
      border: 1px solid var(--color-border);
      border-radius: 0;
      width: 90%;
      max-width: 600px;
      display: flex;
      flex-direction: column;
      max-height: 90vh;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
      overflow: hidden;
    }
    .modal-header {
      padding: 16px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--color-border);
    }
    .modal-header h3 {
      margin: 0;
      font-size: 1.2rem;
      font-weight: 600;
    }
    .modal-body {
      padding: 20px;
      overflow-y: auto;
    }
    .modal-form {
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .form-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
    }
    .modal-footer {
      padding: 16px 20px;
      border-top: 1px solid var(--color-border);
      background: var(--color-surface-2);
      display: flex;
      gap: 12px;
    }
    .justify-end {
      justify-content: flex-end;
    }
    .col-span-2 {
      grid-column: span 2;
    }
    .mb-4 {
      margin-bottom: 16px;
    }
    .mb-6 {
      margin-bottom: 24px;
    }
    .mt-1 {
      margin-top: 4px;
    }
  `,
})
export class PromotionsDashboardComponent implements OnInit, OnDestroy {
  protected readonly store = inject(PromotionsStore);
  private readonly headerService = inject(HeaderService);

  constructor() {
    effect(() => {
      this.headerService.setLoading(this.store.loading());
    });
  }
  protected readonly displayedColumns = [
    'code',
    'discount',
    'scope',
    'min_order',
    'usage',
    'status',
    'dates',
    'actions',
  ];

  protected readonly isModalOpen = signal(false);
  protected readonly editingPromo = signal<Promotion | null>(null);
  protected readonly formData = signal<Partial<Promotion>>({});

  // Computed statistics
  protected readonly totalCoupons = computed(() => this.store.promotions().length);
  protected readonly activeCoupons = computed(
    () => this.store.promotions().filter((p) => p.status === 'ACTIVE').length,
  );
  protected readonly totalRedeemed = computed(() =>
    this.store.promotions().reduce((sum, p) => sum + p.usage_count, 0),
  );
  protected readonly totalSavings = computed(() =>
    this.store.promotions().reduce((sum, p) => sum + p.total_discount_amount, 0),
  );

  ngOnInit(): void {
    this.store.loadAll();
  }

  ngOnDestroy(): void {
    this.headerService.setLoading(false);
  }

  getUsagePercentage(promo: Promotion): number {
    if (!promo.max_usages) return 0;
    return Math.min((promo.usage_count / promo.max_usages) * 100, 100);
  }

  onOpenCreateModal(): void {
    this.editingPromo.set(null);
    this.formData.set({
      code: '',
      discount_type: 'PERCENTAGE',
      discount_value: 10,
      min_order_value: 10,
      max_usages: 100,
      restaurant_id: '',
      status: 'ACTIVE',
      start_date: new Date().toISOString().split('T')[0],
      end_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    });
    this.isModalOpen.set(true);
  }

  onOpenEditModal(promo: Promotion): void {
    this.editingPromo.set(promo);
    this.formData.set({ ...promo });
    this.isModalOpen.set(true);
  }

  onCloseModal(): void {
    this.isModalOpen.set(false);
    this.editingPromo.set(null);
  }

  onDelete(id: string): void {
    if (confirm('Are you sure you want to delete this promotion?')) {
      this.store.delete(id);
    }
  }

  onSubmit(formValues: Partial<Promotion>): void {
    const edit = this.editingPromo();
    if (edit) {
      this.store.update({ id: edit.id, updated: formValues });
    } else {
      this.store.create(formValues);
    }
    this.onCloseModal();
  }
}
