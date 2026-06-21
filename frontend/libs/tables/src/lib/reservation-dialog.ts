import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { CreateReservationRequest, ReservationSource } from '@app/api-client';

export interface ReservationDialogData {
  restaurantId: string;
}

const SOURCES: { value: ReservationSource; label: string }[] = [
  { value: 'PLATFORM', label: 'Platform' },
  { value: 'PHONE', label: 'Phone' },
  { value: 'WALK_IN', label: 'Walk-in' },
  { value: 'THIRD_PARTY', label: 'Third Party' },
];

@Component({
  selector: 'app-reservation-dialog',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatDatepickerModule,
  ],
  template: `
    <h2 mat-dialog-title>New Reservation</h2>
    <mat-dialog-content>
      <form [formGroup]="form" class="form-grid">
        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Customer Name</mat-label>
          <input matInput formControlName="customer_name" />
          @if (form.controls.customer_name.hasError('required')) {
            <mat-error>Customer name is required</mat-error>
          }
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Phone</mat-label>
          <input matInput formControlName="customer_phone" type="tel" />
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Email</mat-label>
          <input matInput formControlName="customer_email" type="email" />
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Date</mat-label>
          <input matInput formControlName="date" type="date" />
          @if (form.controls.date.hasError('required')) {
            <mat-error>Date is required</mat-error>
          }
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Start Time</mat-label>
          <input matInput formControlName="start_time" type="time" />
          @if (form.controls.start_time.hasError('required')) {
            <mat-error>Start time is required</mat-error>
          }
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Party Size</mat-label>
          <input matInput type="number" formControlName="party_size" min="1" />
          @if (form.controls.party_size.hasError('required')) {
            <mat-error>Party size is required</mat-error>
          }
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Source</mat-label>
          <mat-select formControlName="source">
            @for (s of sources; track s.value) {
              <mat-option [value]="s.value">{{ s.label }}</mat-option>
            }
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Special Requests</mat-label>
          <textarea matInput formControlName="special_requests" rows="3"></textarea>
        </mat-form-field>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cancel</button>
      <button mat-flat-button color="primary" [disabled]="form.invalid" (click)="onSave()">
        Create Reservation
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
    .full-width {
      grid-column: 1 / -1;
    }
  `,
})
export class ReservationDialog {
  readonly data = inject<ReservationDialogData>(MAT_DIALOG_DATA);
  private readonly dialogRef = inject(MatDialogRef<ReservationDialog>);
  private readonly fb = inject(FormBuilder);

  readonly sources = SOURCES;

  readonly form = this.fb.nonNullable.group({
    customer_name: ['', Validators.required],
    customer_phone: [''],
    customer_email: [''],
    date: ['', Validators.required],
    start_time: ['', Validators.required],
    party_size: [2, [Validators.required, Validators.min(1)]],
    source: ['PLATFORM' as string],
    special_requests: [''],
  });

  onSave(): void {
    if (this.form.valid) {
      const value = this.form.getRawValue();
      const result: CreateReservationRequest = {
        restaurant_id: this.data.restaurantId,
        date: value.date,
        start_time: value.start_time,
        party_size: value.party_size,
        customer_name: value.customer_name,
        source: value.source,
      };
      if (value.customer_phone) result.customer_phone = value.customer_phone;
      if (value.customer_email) result.customer_email = value.customer_email;
      if (value.special_requests) result.special_requests = value.special_requests;
      this.dialogRef.close(result);
    }
  }
}
