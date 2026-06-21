import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormField, form, required } from '@angular/forms/signals';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

export interface CreateDialogData {
  title: string;
  nameLabel: string;
  namePlaceholder: string;
  descriptionLabel?: string;
  descriptionPlaceholder?: string;
}

export interface CreateDialogResult {
  name: string;
  description: string;
}

interface CreateDialogForm {
  name: string;
  description: string;
}

@Component({
  selector: 'app-create-dialog',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    FormField,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
  ],
  templateUrl: './create-dialog.component.html',
  styleUrl: './create-dialog.component.scss',
})
export class CreateDialog {
  readonly data = inject<CreateDialogData>(MAT_DIALOG_DATA);
  private readonly dialogRef = inject(MatDialogRef<CreateDialog>);

  readonly formModel = signal<CreateDialogForm>({
    name: '',
    description: '',
  });

  readonly createForm = form(this.formModel, (fieldPath) => {
    required(fieldPath.name, { message: 'Name is required' });
  });

  onSave(): void {
    if (this.createForm().invalid()) {
      this.createForm().markAsTouched();
      return;
    }

    const trimmedName = this.formModel().name.trim();
    if (!trimmedName) return;

    const result: CreateDialogResult = {
      name: trimmedName,
      description: this.formModel().description.trim(),
    };
    this.dialogRef.close(result);
  }
}

