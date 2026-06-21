import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
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

@Component({
  selector: 'app-create-dialog',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    ReactiveFormsModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
  ],
  template: `
    <h2 mat-dialog-title>{{ data.title }}</h2>
    <mat-dialog-content>
      <form [formGroup]="form" class="create-form">
        <mat-form-field appearance="outline" class="full">
          <mat-label>{{ data.nameLabel }}</mat-label>
          <input
            matInput
            formControlName="name"
            id="dialog-name-input"
            [placeholder]="data.namePlaceholder"
          />
        </mat-form-field>

        <mat-form-field appearance="outline" class="full">
          <mat-label>{{ data.descriptionLabel || 'Description' }}</mat-label>
          <textarea
            matInput
            formControlName="description"
            rows="3"
            [placeholder]="data.descriptionPlaceholder || 'Optional description…'"
            id="dialog-desc-input"
          ></textarea>
        </mat-form-field>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cancel</button>
      <button
        mat-flat-button
        color="primary"
        (click)="onSave()"
        [disabled]="form.invalid"
        id="dialog-save-btn"
      >
        Submit
      </button>
    </mat-dialog-actions>
  `,
  styles: `
    .create-form {
      display: flex;
      flex-direction: column;
      gap: 8px;
      padding: 8px 0;
      min-width: 400px;
    }
    .full {
      width: 100%;
    }
  `,
})
export class CreateDialog {
  readonly data = inject<CreateDialogData>(MAT_DIALOG_DATA);
  private readonly dialogRef = inject(MatDialogRef<CreateDialog>);
  private readonly fb = inject(FormBuilder);

  protected readonly form = this.fb.nonNullable.group({
    name: ['', Validators.required],
    description: [''],
  });

  onSave(): void {
    if (this.form.invalid) return;
    const val = this.form.getRawValue();
    const result: CreateDialogResult = {
      name: val.name.trim(),
      description: val.description.trim(),
    };
    this.dialogRef.close(result);
  }
}
