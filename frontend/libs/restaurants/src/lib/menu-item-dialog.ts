import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCheckboxModule } from '@angular/material/checkbox';

export interface MenuItemDialogData {
  menuId: string;
  categoryId: string;
  categoryName: string;
  item?: {
    id: string;
    name: string;
    description: string | null;
    price_amount: string;
    price_currency: string;
    is_available: boolean;
  };
}

export interface MenuItemDialogResult {
  name: string;
  description: string | null;
  price_amount: string;
  price_currency: string;
  category_id: string;
  is_available: boolean;
}

@Component({
  selector: 'app-menu-item-dialog',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    ReactiveFormsModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatCheckboxModule,
  ],
  template: `
    <h2 mat-dialog-title>{{ data.item ? 'Edit' : 'Add' }} Menu Item</h2>
    <mat-dialog-content>
      <form [formGroup]="form" class="item-form">
        <mat-form-field appearance="outline" class="full">
          <mat-label>Item name</mat-label>
          <input matInput formControlName="name" id="item-name" placeholder="e.g. Grilled Salmon" />
        </mat-form-field>

        <mat-form-field appearance="outline" class="full">
          <mat-label>Description</mat-label>
          <textarea
            matInput
            formControlName="description"
            rows="3"
            placeholder="Brief description…"
            id="item-description"
          ></textarea>
        </mat-form-field>

        <div class="price-row">
          <mat-form-field appearance="outline" class="price-amount">
            <mat-label>Price</mat-label>
            <input
              matInput
              formControlName="price_amount"
              type="number"
              min="0"
              step="0.01"
              id="item-price"
              placeholder="0.00"
            />
          </mat-form-field>

          <mat-form-field appearance="outline" class="price-currency">
            <mat-label>Currency</mat-label>
            <input
              matInput
              formControlName="price_currency"
              placeholder="INR"
              id="item-currency"
              maxlength="3"
            />
          </mat-form-field>
        </div>

        <mat-checkbox formControlName="is_available" id="item-available">
          Available for ordering
        </mat-checkbox>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cancel</button>
      <button
        mat-flat-button
        color="primary"
        (click)="onSave()"
        [disabled]="form.invalid"
        id="item-save-btn"
      >
        {{ data.item ? 'Save changes' : 'Add item' }}
      </button>
    </mat-dialog-actions>
  `,
  styles: `
    .item-form {
      display: flex;
      flex-direction: column;
      gap: 8px;
      padding: 8px 0;
      min-width: 400px;
    }
    .full {
      width: 100%;
    }
    .price-row {
      display: flex;
      gap: 12px;
    }
    .price-amount {
      flex: 2;
    }
    .price-currency {
      flex: 1;
    }
  `,
})
export class MenuItemDialog {
  readonly data = inject<MenuItemDialogData>(MAT_DIALOG_DATA);
  private readonly dialogRef = inject(MatDialogRef<MenuItemDialog>);
  private readonly fb = inject(FormBuilder);

  protected readonly form = this.fb.nonNullable.group({
    name: [this.data.item?.name ?? '', Validators.required],
    description: [this.data.item?.description ?? ''],
    price_amount: [this.data.item?.price_amount ?? '', [Validators.required, Validators.min(0)]],
    price_currency: [this.data.item?.price_currency ?? 'INR', Validators.required],
    is_available: [this.data.item?.is_available ?? true],
  });

  onSave(): void {
    if (this.form.invalid) return;
    const val = this.form.getRawValue();
    const result: MenuItemDialogResult = {
      name: val.name,
      description: val.description || null,
      price_amount: parseFloat(val.price_amount).toFixed(2),
      price_currency: val.price_currency.toUpperCase(),
      category_id: this.data.categoryId,
      is_available: val.is_available,
    };
    this.dialogRef.close(result);
  }
}
