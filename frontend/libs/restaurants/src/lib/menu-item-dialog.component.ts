import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormField, form, required, pattern, maxLength } from '@angular/forms/signals';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSelectModule } from '@angular/material/select';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { CommonModule } from '@angular/common';
import { ImagePicker } from '../../../shared/src/lib/image-picker';

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
    image_url?: string | null;
    dietary_labels?: string[];
    preparation_time_minutes?: number | null;
  };
  onSave: (result: MenuItemDialogResult) => import('rxjs').Observable<any>;
}

export interface MenuItemDialogResult {
  name: string;
  description: string | null;
  price_amount: string;
  price_currency: string;
  category_id: string;
  is_available: boolean;
  image_url: string | null;
  dietary_labels: string[];
  preparation_time_minutes: number | null;
}

interface MenuItemForm {
  name: string;
  description: string;
  priceAmount: string;
  priceCurrency: string;
  isAvailable: boolean;
  imageUrl: string;
  dietaryLabels: string[];
  preparationTimeMinutes: string;
}

@Component({
  selector: 'app-menu-item-dialog',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    FormField,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatCheckboxModule,
    MatSelectModule,
    MatProgressSpinnerModule,
    ImagePicker
  ],
  templateUrl: './menu-item-dialog.component.html',
  styleUrl: './menu-item-dialog.component.scss',
})
export class MenuItemDialog {
  readonly data = inject<MenuItemDialogData>(MAT_DIALOG_DATA);
  private readonly dialogRef = inject(MatDialogRef<MenuItemDialog>);

  readonly formModel = signal<MenuItemForm>({
    name: this.data.item?.name ?? '',
    description: this.data.item?.description ?? '',
    priceAmount: this.data.item?.price_amount ?? '',
    priceCurrency: this.data.item?.price_currency ?? 'INR',
    isAvailable: this.data.item?.is_available ?? true,
    imageUrl: this.data.item?.image_url ?? '',
    dietaryLabels: this.data.item?.dietary_labels ?? [],
    preparationTimeMinutes:
      this.data.item?.preparation_time_minutes !== null && this.data.item?.preparation_time_minutes !== undefined
        ? String(this.data.item.preparation_time_minutes)
        : '',
  });

  protected readonly initialImages = this.data.item?.image_url
    ? this.data.item.image_url.split('|').map((img) => img.trim()).filter(Boolean)
    : [];

  readonly itemForm = form(this.formModel, (fieldPath) => {
    required(fieldPath.name, { message: 'Item name is required' });
    required(fieldPath.priceAmount, { message: 'Price is required' });
    pattern(fieldPath.priceAmount, /^\d+(\.\d+)?$/, { message: 'Price must be a positive number' });
    required(fieldPath.priceCurrency, { message: 'Currency is required' });
    maxLength(fieldPath.priceCurrency, 3, { message: 'Currency must be 3 characters or less' });
    pattern(fieldPath.preparationTimeMinutes, /^[0-9]*$/, { message: 'Prep time must be a number' });
  });

  protected readonly availableLabels = [
    'vegetarian',
    'vegan',
    'non-vegetarian',
    'gluten-free',
    'dairy-free',
    'spicy',
    'nuts-free',
    'halal',
    'kosher',
  ];

  readonly saving = signal<boolean>(false);

  onImagesChanged(images: string[]): void {
    this.formModel.update((model) => ({
      ...model,
      imageUrl: images.join('|'),
    }));
  }

  isValid(): boolean {
    return !this.itemForm().invalid();
  }

  onSave(): void {
    if (!this.isValid()) {
      this.itemForm().markAsTouched();
      return;
    }

    this.saving.set(true);
    const model = this.formModel();
    const result: MenuItemDialogResult = {
      name: model.name.trim(),
      description: model.description.trim() || null,
      price_amount: parseFloat(model.priceAmount).toFixed(2),
      price_currency: model.priceCurrency.trim().toUpperCase(),
      category_id: this.data.categoryId,
      is_available: model.isAvailable,
      image_url: model.imageUrl.trim() || null,
      dietary_labels: model.dietaryLabels,
      preparation_time_minutes: model.preparationTimeMinutes ? parseInt(model.preparationTimeMinutes, 10) : null,
    };
    
    this.data.onSave(result).subscribe({
      next: () => {
        this.dialogRef.close(true);
      },
      error: () => {
        this.saving.set(false);
      }
    });
  }
}

