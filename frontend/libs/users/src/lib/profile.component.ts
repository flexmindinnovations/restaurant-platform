import { ChangeDetectionStrategy, Component, effect, inject, OnInit, OnDestroy, signal, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import {
  LucideCircleCheck,
  LucideCircleAlert,
  LucideSave,
  LucideLoaderCircle,
  LucideUser,
} from '@lucide/angular';
import { PageHeader, HeaderService, ImagePicker } from '@app/shared';
import { ProfileStore } from './profile.store';
import { UserProfile } from './users.model';

@Component({
  selector: 'app-profile',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    LucideCircleCheck,
    LucideCircleAlert,
    LucideSave,
    LucideLoaderCircle,
    LucideUser,
    PageHeader,
    ImagePicker,
  ],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.scss',
})
export class ProfileComponent implements OnInit, OnDestroy {
  protected readonly store = inject(ProfileStore);
  private readonly headerService = inject(HeaderService);
  private readonly platformId = inject(PLATFORM_ID);
  protected readonly avatarUrl = signal<string | null>(null);

  constructor() {
    this.store.clearMessages();
    effect(() => {
      this.headerService.setLoading(this.store.loading());
    });

    effect(() => {
      const profile = this.store.profile();
      if (profile) {
        this.avatarUrl.set(profile.avatar_url);
      }
    });
  }

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.store.loadProfile();
    }
  }

  ngOnDestroy(): void {
    this.headerService.setLoading(false);
  }

  onAvatarChanged(images: string[]): void {
    if (images.length > 0) {
      this.avatarUrl.set(images[0]);
    } else {
      this.avatarUrl.set(null);
    }
  }

  onSubmit(formValues: Partial<UserProfile>): void {
    const payload: Partial<UserProfile> = {
      first_name: formValues.first_name || '',
      last_name: formValues.last_name || '',
      display_name: formValues.display_name || '',
      preferred_language: formValues.preferred_language || 'en',
      avatar_url: this.avatarUrl(),
    };
    this.store.updateProfile(payload);

    // Auto clear success alert after 4 seconds
    setTimeout(() => {
      this.store.clearMessages();
    }, 4000);
  }
}
