import {
  ChangeDetectionStrategy,
  Component,
  inject,
  OnInit,
  input,
} from '@angular/core';
import { RouterLink } from '@angular/router';
import { DecimalPipe } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { PageHeader } from '../../../shared/src/lib/page-header';
import { StatusBadge } from '../../../shared/src/lib/status-badge';
import { RestaurantsStore } from './restaurants.store';
import { MenusStore } from './menus.store';

@Component({
  selector: 'app-restaurant-detail',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    RouterLink,
    DecimalPipe,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatDividerModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    PageHeader,
    StatusBadge,
  ],
  template: `
    @if (store.loading()) {
      <div class="center-spinner">
        <mat-spinner diameter="48" />
      </div>
    } @else {
      @if (store.selectedRestaurant(); as r) {
        <app-page-header [title]="r.name" [subtitle]="r.address_city + ', ' + r.address_state">
          <button mat-stroked-button [routerLink]="['menus']">
            <mat-icon>restaurant_menu</mat-icon> Manage Menus
          </button>
          @if (!r.is_verified) {
            <button mat-flat-button color="primary" (click)="store.verifyRestaurant(r.id)">
              <mat-icon>verified</mat-icon> Verify
            </button>
          }
        </app-page-header>

        <div class="detail-grid">
          <!-- Info card -->
          <mat-card appearance="outlined">
            <mat-card-header>
              <mat-card-title>Restaurant Info</mat-card-title>
            </mat-card-header>
            <mat-card-content>
              <dl class="info-list">
                <dt>Status</dt>
                <dd><app-status-badge [status]="r.is_active ? 'ACTIVE' : 'INACTIVE'" /></dd>

                <dt>Verified</dt>
                <dd><app-status-badge [status]="r.is_verified ? 'VERIFIED' : 'UNVERIFIED'" /></dd>

                <dt>Email</dt>
                <dd>{{ r.email }}</dd>

                <dt>Phone</dt>
                <dd>{{ r.phone }}</dd>

                <dt>Cuisine</dt>
                <dd>
                  @for (c of r.cuisine_types; track c) {
                    <mat-chip [disableRipple]="true" class="cuisine-chip">{{ c }}</mat-chip>
                  }
                </dd>
              </dl>
            </mat-card-content>
          </mat-card>

          <!-- Address card -->
          <mat-card appearance="outlined">
            <mat-card-header>
              <mat-card-title>Address</mat-card-title>
            </mat-card-header>
            <mat-card-content>
              <address class="address-block">
                {{ r.address_street }}<br />
                {{ r.address_city }}, {{ r.address_state }} {{ r.address_postal_code }}<br />
                {{ r.address_country }}
              </address>
              @if (r.address_latitude && r.address_longitude) {
                <p class="coords">
                  <mat-icon class="coords-icon">location_on</mat-icon>
                  {{ r.address_latitude | number: '1.4-6' }},
                  {{ r.address_longitude | number: '1.4-6' }}
                </p>
              }
            </mat-card-content>
          </mat-card>

          <!-- Menus summary card -->
          <mat-card appearance="outlined" class="menus-card">
            <mat-card-header>
              <mat-card-title>Menus</mat-card-title>
            </mat-card-header>
            <mat-card-content>
              @if (menusStore.loading()) {
                <mat-spinner diameter="32" />
              } @else if (menusStore.menus().length > 0) {
                <ul class="menu-preview-list">
                  @for (m of menusStore.menus(); track m.id) {
                    <li>
                      <span class="menu-name">{{ m.name }}</span>
                      <app-status-badge [status]="m.is_published ? 'ACTIVE' : 'INACTIVE'" />
                    </li>
                  }
                </ul>
              } @else {
                <p class="no-menus">No menus yet.</p>
              }
            </mat-card-content>
            <mat-card-actions>
              <button mat-stroked-button [routerLink]="['menus']">
                <mat-icon>restaurant_menu</mat-icon>
                Manage all menus
              </button>
            </mat-card-actions>
          </mat-card>
        </div>
      } @else if (store.error()) {
        <p class="error-text">{{ store.error() }}</p>
      }
    }
  `,
  styles: `
    .center-spinner { display: flex; justify-content: center; padding: 64px; }
    .detail-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 16px;
    }
    .menus-card { grid-column: 1 / -1; }
    .info-list { display: grid; grid-template-columns: 130px 1fr; gap: 8px 16px; margin: 0; }
    dt { font-weight: 500; color: var(--mat-sys-on-surface-variant, #666); align-self: center; }
    dd { margin: 0; align-self: center; display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }
    .cuisine-chip { font-size: 0.75rem !important; height: 22px !important; }
    address { font-style: normal; line-height: 1.8; }
    .coords { display: flex; align-items: center; gap: 4px; font-size: 0.8rem; opacity: 0.7; margin-top: 8px; }
    .coords-icon { font-size: 16px; width: 16px; height: 16px; }
    .menu-preview-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
    .menu-preview-list li { display: flex; align-items: center; justify-content: space-between; }
    .menu-name { font-weight: 500; }
    .no-menus { color: var(--mat-sys-on-surface-variant, #888); }
    .error-text { color: red; }
  `,
})
export class RestaurantDetail implements OnInit {
  readonly id = input.required<string>();

  protected readonly store = inject(RestaurantsStore);
  protected readonly menusStore = inject(MenusStore);

  ngOnInit(): void {
    this.store.loadRestaurant(this.id());
    this.menusStore.loadMenus(this.id());
  }
}
