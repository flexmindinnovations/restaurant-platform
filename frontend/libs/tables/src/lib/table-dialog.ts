import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { Section, RestaurantTable, TableShape } from '@app/api-client';

export interface TableDialogData {
  table?: RestaurantTable;
  sections: Section[];
}

export interface TableDialogResult {
  number: string;
  section_id?: string;
  capacity_min: number;
  capacity_max: number;
  shape: string;
  turn_time_minutes: number;
  buffer_minutes: number;
}

const SHAPES: { value: TableShape; label: string }[] = [
  { value: 'ROUND', label: 'Round' },
  { value: 'SQUARE', label: 'Square' },
  { value: 'RECTANGULAR', label: 'Rectangular' },
  { value: 'BOOTH', label: 'Booth' },
  { value: 'BAR_SEAT', label: 'Bar Seat' },
];

@Component({
  selector: 'app-table-dialog',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
  ],
  template: `
    <h2 mat-dialog-title>{{ data.table ? 'Edit Table' : 'Add Table' }}</h2>
    <mat-dialog-content>
      <form [formGroup]="form" class="form-grid">
        <mat-form-field appearance="outline">
          <mat-label>Table Number</mat-label>
          <input matInput formControlName="number" placeholder="e.g. T1, A3" />
          @if (form.controls.number.hasError('required')) {
            <mat-error>Table number is required</mat-error>
          }
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Section</mat-label>
          <mat-select formControlName="section_id">
            <mat-option [value]="null">No section</mat-option>
            @for (section of data.sections; track section.id) {
              <mat-option [value]="section.id">{{ section.name }}</mat-option>
            }
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Min Capacity</mat-label>
          <input matInput type="number" formControlName="capacity_min" min="1" />
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Max Capacity</mat-label>
          <input matInput type="number" formControlName="capacity_max" min="1" />
          @if (form.controls.capacity_max.hasError('required')) {
            <mat-error>Max capacity is required</mat-error>
          }
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Shape</mat-label>
          <mat-select formControlName="shape">
            @for (s of shapes; track s.value) {
              <mat-option [value]="s.value">{{ s.label }}</mat-option>
            }
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Turn Time (min)</mat-label>
          <input matInput type="number" formControlName="turn_time_minutes" min="0" />
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Buffer (min)</mat-label>
          <input matInput type="number" formControlName="buffer_minutes" min="0" />
        </mat-form-field>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cancel</button>
      <button mat-flat-button color="primary" [disabled]="form.invalid" (click)="onSave()">
        {{ data.table ? 'Update' : 'Create' }}
      </button>
    </mat-dialog-actions>
  `,
  styles: `
    .form-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0 16px;
      min-width: 400px;
    }
    .form-grid mat-form-field:first-child {
      grid-column: 1 / -1;
    }
  `,
})
export class TableDialog {
  readonly data = inject<TableDialogData>(MAT_DIALOG_DATA);
  private readonly dialogRef = inject(MatDialogRef<TableDialog>);
  private readonly fb = inject(FormBuilder);

  readonly shapes = SHAPES;

  readonly form = this.fb.nonNullable.group({
    number: [this.data.table?.number ?? '', Validators.required],
    section_id: [this.data.table?.section_id ?? null as string | null],
    capacity_min: [this.data.table?.capacity_min ?? 1],
    capacity_max: [this.data.table?.capacity_max ?? 4, Validators.required],
    shape: [this.data.table?.shape ?? ('SQUARE' as string)],
    turn_time_minutes: [this.data.table?.turn_time_minutes ?? 90],
    buffer_minutes: [this.data.table?.buffer_minutes ?? 15],
  });

  onSave(): void {
    if (this.form.valid) {
      const value = this.form.getRawValue();
      const result: TableDialogResult = {
        number: value.number,
        capacity_min: value.capacity_min,
        capacity_max: value.capacity_max,
        shape: value.shape,
        turn_time_minutes: value.turn_time_minutes,
        buffer_minutes: value.buffer_minutes,
      };
      if (value.section_id) {
        result.section_id = value.section_id;
      }
      this.dialogRef.close(result);
    }
  }
}
