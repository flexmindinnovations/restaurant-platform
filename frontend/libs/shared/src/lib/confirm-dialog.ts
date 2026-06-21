import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Observable } from 'rxjs';
import {
  LucideTriangleAlert,
  LucideInfo,
  LucideTrash2,
} from '@lucide/angular';

export type ConfirmDialogVariant = 'danger' | 'warning' | 'info';

export interface ConfirmDialogData {
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: ConfirmDialogVariant;
  onConfirm?: () => Observable<unknown>;
}

@Component({
  selector: 'app-confirm-dialog',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    LucideTriangleAlert,
    LucideInfo,
    LucideTrash2,
  ],
  template: `
    <div class="confirm-dialog">
      <div class="dialog-header">
        <div class="confirm-icon" [ngClass]="'confirm-icon--' + variant">
          @switch (variant) {
            @case ('danger') {
              <svg lucideTrash2 [size]="18"></svg>
            }
            @case ('warning') {
              <svg lucideAlertTriangle [size]="18"></svg>
            }
            @default {
              <svg lucideInfo [size]="18"></svg>
            }
          }
        </div>
        <h2 class="confirm-title">{{ data.title }}</h2>
      </div>

      <p class="confirm-message">{{ data.message }}</p>

      @if (error()) {
        <p class="confirm-error">{{ error() }}</p>
      }

      <div class="confirm-actions">
        <button mat-button [disabled]="loading()" (click)="dialogRef.close(false)">
          {{ data.cancelLabel || 'Cancel' }}
        </button>
        <button
          mat-flat-button
          [class]="confirmBtnClass"
          [disabled]="loading()"
          (click)="onConfirm()"
        >
          @if (loading()) {
            <mat-spinner diameter="18" strokeWidth="2"></mat-spinner>
          }
          {{ data.confirmLabel || 'Confirm' }}
        </button>
      </div>
    </div>
  `,
  styles: `
    .confirm-dialog {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      text-align: left;
      padding: 18px;
    }

    .dialog-header {
      width: 100%;
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 16px;

      .confirm-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .confirm-icon--danger {
        background-color: var(--color-error-bg);
        color: var(--color-error);
      }

      .confirm-icon--warning {
        background-color: var(--color-warning-bg);
        color: var(--color-warning);
      }

      .confirm-icon--info {
        background-color: var(--color-info-bg);
        color: var(--color-info);
      }

      .confirm-title {
        margin: 0;
        font-weight: 600;
        color: var(--color-text-primary);
      }
    }

    .confirm-message {
      // padding: 0 10px;
      margin: 0 0 24px;
      color: var(--color-text-secondary);
    }

    .confirm-error {
      margin: 0 0 12px;
      color: var(--color-error);
      font-size: 13px;
    }

    .confirm-actions {
      display: flex;
      gap: 8px;
      width: 100%;
      justify-content: flex-end;

      button {
        display: flex;
        align-items: center;
        gap: 6px;
      }
    }
  `,
})
export class ConfirmDialog {
  readonly data = inject<ConfirmDialogData>(MAT_DIALOG_DATA);
  readonly dialogRef = inject(MatDialogRef<ConfirmDialog>);

  protected readonly loading = signal(false);
  protected readonly error = signal<string | null>(null);

  protected get variant(): ConfirmDialogVariant {
    return this.data.variant ?? 'danger';
  }

  private static readonly VARIANT_CLASS: Record<ConfirmDialogVariant, string> = {
    danger: 'mat-btn-danger',
    warning: 'mat-btn-warning',
    info: 'mat-btn-info',
  };

  protected get confirmBtnClass(): string {
    return ConfirmDialog.VARIANT_CLASS[this.variant];
  }

  onConfirm(): void {
    if (!this.data.onConfirm) {
      this.dialogRef.close(true);
      return;
    }

    this.loading.set(true);
    this.error.set(null);
    this.dialogRef.disableClose = true;

    this.data.onConfirm().subscribe({
      next: () => this.dialogRef.close(true),
      error: (err: unknown) => {
        this.loading.set(false);
        this.dialogRef.disableClose = false;
        const msg =
          err instanceof HttpErrorResponse
            ? err.error?.error?.message || err.error?.detail || 'Operation failed'
            : 'An unexpected error occurred';
        this.error.set(msg);
      },
    });
  }
}
