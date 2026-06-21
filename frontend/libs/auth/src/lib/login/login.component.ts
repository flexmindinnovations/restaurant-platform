import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  inject,
  signal,
  OnInit,
} from '@angular/core';
import { email, form, FormField, required, submit } from '@angular/forms/signals';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import {
  LucideUtensilsCrossed,
  LucideCircleAlert,
  LucideMail,
  LucideEye,
  LucideEyeOff,
} from '@lucide/angular';
import { AuthService, LoginCredentials } from '../auth.service';
import { SettingsStore } from '@app/settings';

interface LoginData {
  email: string;
  password: string;
}

@Component({
  selector: 'app-auth-login',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormField,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatProgressBarModule,
    LucideUtensilsCrossed,
    LucideCircleAlert,
    LucideMail,
    LucideEye,
    LucideEyeOff,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly cdr = inject(ChangeDetectorRef);
  protected readonly settingsStore = inject(SettingsStore);

  ngOnInit(): void {
    this.settingsStore.loadSettings();
  }

  // readonly loginForm: FormGroup = this.fb.group({
  //   email: ['', [Validators.required, Validators.email]],
  //   password: ['', [Validators.required, Validators.minLength(8)]],
  // });

  readonly loginModel = signal<LoginData>({
    email: '',
    password: '',
  });

  readonly loginForm = form(this.loginModel, (fieldPath) => {
    email(fieldPath.email, { message: 'Invalid email' });
    required(fieldPath.email, { message: 'Email is required' });
    required(fieldPath.password, { message: 'Password is required' });
  });

  loading = false;
  errorMessage: string | null = null;
  hidePassword = true;
  passwordHasValue = false;

  onSubmit(event: Event): void {
    event.preventDefault();
    if (this.loginForm().invalid()) {
      this.loginForm().markAsTouched();
      return;
    }

    submit(this.loginForm, async () => {
      this.loading = true;
      this.errorMessage = null;
      this.cdr.markForCheck();
      const credentials = this.loginModel();
      this.authService.login(credentials).subscribe({
        next: () => {
          this.loading = false;
          this.cdr.markForCheck();
          this.router.navigate(['/dashboard']);
        },
        error: (err: any) => {
          this.loading = false;
          this.errorMessage =
            err?.error?.error?.message ??
            err?.error?.message ??
            err?.error?.detail ??
            err?.message ??
            'Login failed. Please check your credentials.';
          this.cdr.markForCheck();
        },
      });
    });
  }
}
