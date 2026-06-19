import { ChangeDetectionStrategy, Component, inject, OnInit, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { PageHeader } from '../../../shared/src/lib/page-header';
import { DeliveriesStore } from './deliveries.store';
import { ActiveDelivery, DeliveryPartner } from './deliveries.model';

@Component({
  selector: 'app-deliveries-map',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatIconModule,
    MatButtonModule,
    MatSelectModule,
    MatChipsModule,
    MatProgressBarModule,
    MatTooltipModule,
    PageHeader,
  ],
  template: `
    <app-page-header title="Delivery Operations" subtitle="Real-time map and partner assignment overrides">
      <button mat-flat-button color="primary" (click)="store.loadAll()">
        <mat-icon>refresh</mat-icon> Refresh Data
      </button>
    </app-page-header>

    @if (store.loading()) {
      <mat-progress-bar mode="indeterminate" class="mb-4" />
    }

    <div class="deliveries-layout">
      <!-- Interactive Map Panel -->
      <mat-card class="map-card mat-elevation-z1">
        <mat-card-header class="map-header">
          <mat-card-title>San Francisco Live Delivery Map</mat-card-title>
          <div class="map-legend">
            <span class="legend-item"><span class="dot dot--online"></span> Online</span>
            <span class="legend-item"><span class="dot dot--busy"></span> Busy</span>
            <span class="legend-item"><span class="dot dot--offline"></span> Offline</span>
          </div>
        </mat-card-header>
        <mat-card-content class="map-content">
          <svg viewBox="0 0 600 400" class="live-map-svg">
            <!-- Grid Background Lines / Representation of SF Streets -->
            <rect width="600" height="400" fill="#f0f2f5" rx="8" />
            
            <!-- Roads/Grid representation -->
            <g class="map-roads" stroke="#ffffff" stroke-width="4">
              <line x1="50" y1="0" x2="50" y2="400" />
              <line x1="150" y1="0" x2="150" y2="400" />
              <line x1="250" y1="0" x2="250" y2="400" />
              <line x1="350" y1="0" x2="350" y2="400" />
              <line x1="450" y1="0" x2="450" y2="400" />
              <line x1="550" y1="0" x2="550" y2="400" />
              
              <line x1="0" y1="50" x2="600" y2="50" />
              <line x1="0" y1="130" x2="600" y2="130" />
              <line x1="0" y1="210" x2="600" y2="210" />
              <line x1="0" y1="290" x2="600" y2="290" />
              <line x1="0" y1="370" x2="600" y2="370" />
            </g>

            <!-- Active Delivery Route Lines -->
            @for (del of store.deliveries(); track del.id) {
              @if (del.status !== 'DELIVERED') {
                <g class="route-group" [class.route-group--selected]="store.selectedDelivery()?.id === del.id">
                  <!-- Dashed line from restaurant to customer -->
                  <line 
                    [attr.x1]="lngToX(del.restaurant_location.lng)" 
                    [attr.y1]="latToY(del.restaurant_location.lat)"
                    [attr.x2]="lngToX(del.customer_location.lng)" 
                    [attr.y2]="latToY(del.customer_location.lat)"
                    class="route-line" 
                  />
                </g>
              }
            }

            <!-- Restaurant Pins -->
            @for (del of store.deliveries(); track del.id) {
              @if (del.status !== 'DELIVERED') {
                <g class="marker" 
                   [attr.transform]="getTransform(del.restaurant_location.lat, del.restaurant_location.lng)"
                   [matTooltip]="'Restaurant: ' + del.restaurant_name"
                   (click)="store.selectDelivery(del)">
                  <circle r="9" fill="#e65100" stroke="#ffffff" stroke-width="2" />
                  <text y="3" class="marker-label" text-anchor="middle" fill="#ffffff">R</text>
                </g>
              }
            }

            <!-- Customer Pins -->
            @for (del of store.deliveries(); track del.id) {
              @if (del.status !== 'DELIVERED') {
                <g class="marker" 
                   [attr.transform]="getTransform(del.customer_location.lat, del.customer_location.lng)"
                   [matTooltip]="'Delivery for Order ' + del.id"
                   (click)="store.selectDelivery(del)">
                  <circle r="9" fill="#1565c0" stroke="#ffffff" stroke-width="2" />
                  <text y="3" class="marker-label" text-anchor="middle" fill="#ffffff">C</text>
                </g>
              }
            }

            <!-- Partner Pins -->
            @for (pt of store.partners(); track pt.id) {
              <g class="marker marker--partner" 
                 [attr.transform]="getTransform(pt.current_location.lat, pt.current_location.lng)"
                 [matTooltip]="pt.name + ' (' + pt.status + ' - ' + pt.vehicle_type + ')'">
                <circle r="10" [attr.fill]="getPartnerColor(pt.status)" stroke="#ffffff" stroke-width="2" />
                <path d="M-4,-4 L4,0 L-4,4 Z" fill="#ffffff" transform="translate(1,0)" />
              </g>
            }
          </svg>
        </mat-card-content>
      </mat-card>

      <!-- Sidebar Controls Panel -->
      <div class="controls-panel">
        <!-- Active Deliveries List -->
        <mat-card appearance="outlined" class="deliveries-card">
          <mat-card-header>
            <mat-card-title>Active Orders</mat-card-title>
          </mat-card-header>
          <mat-card-content class="deliveries-list-content">
            <div class="delivery-items-container">
              @for (del of store.deliveries(); track del.id) {
                <div class="delivery-item" 
                     [class.delivery-item--selected]="store.selectedDelivery()?.id === del.id"
                     (click)="store.selectDelivery(del)">
                  <div class="delivery-item-header">
                    <span class="order-id font-semibold">{{ del.id }}</span>
                    <span class="delivery-status-badge" [class]="'badge--' + del.status.toLowerCase()">{{ del.status }}</span>
                  </div>
                  <div class="delivery-item-body">
                    <p class="text-sm"><strong>From:</strong> {{ del.restaurant_name }}</p>
                    <p class="text-sm"><strong>To:</strong> {{ del.customer_address }}</p>
                    <p class="text-sm">
                      <strong>Driver:</strong> {{ del.partner_name || 'Unassigned ⚠️' }}
                    </p>
                  </div>
                </div>
              }
            </div>
          </mat-card-content>
        </mat-card>

        <!-- Override Panel (Shows when a delivery is selected) -->
        @if (store.selectedDelivery(); as selected) {
          <mat-card appearance="outlined" class="override-card mt-4">
            <mat-card-header>
              <mat-card-title>Assignment Override</mat-card-title>
            </mat-card-header>
            <mat-card-content class="override-content">
              <p class="text-sm mb-2">Assign or override the courier for order <strong>{{ selected.id }}</strong>:</p>
              
              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Select Delivery Partner</mat-label>
                <mat-select [value]="selected.partner_id" (selectionChange)="onOverride(selected.id, $event.value)">
                  <mat-option [value]="null">-- Unassigned --</mat-option>
                  @for (p of availablePartners(); track p.id) {
                    <mat-option [value]="p.id">
                      {{ p.name }} ({{ p.vehicle_type }}) - {{ p.status }}
                    </mat-option>
                  }
                </mat-select>
              </mat-form-field>
              
              <div class="actions">
                <button mat-button color="primary" (click)="store.selectDelivery(null)">Cancel</button>
              </div>
            </mat-card-content>
          </mat-card>
        }
      </div>
    </div>
  `,
  styles: `
    .deliveries-layout {
      display: grid;
      grid-template-columns: 1fr 340px;
      gap: 16px;
      align-items: start;
    }

    .map-card {
      border-radius: 12px;
      overflow: hidden;
      background: var(--mat-sys-surface, #fff);
    }
    .map-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px !important;
    }
    .map-legend {
      display: flex;
      gap: 12px;
      font-size: 0.8rem;
    }
    .legend-item {
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      display: inline-block;
    }
    .dot--online { background: #43a047; }
    .dot--busy { background: #fb8c00; }
    .dot--offline { background: #757575; }

    .map-content {
      padding: 0 !important;
    }
    .live-map-svg {
      width: 100%;
      height: auto;
      display: block;
    }

    .route-line {
      stroke: #1e88e5;
      stroke-width: 3;
      stroke-dasharray: 6 4;
      opacity: 0.7;
    }
    .route-group--selected .route-line {
      stroke: #e53935;
      stroke-width: 4;
      opacity: 1;
    }

    .marker {
      cursor: pointer;
      transition: transform 0.2s;
    }
    .marker:hover {
      transform: scale(1.2) !important;
    }
    .marker-label {
      font-size: 8px;
      font-weight: 700;
      font-family: sans-serif;
    }

    .controls-panel {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .deliveries-card {
      border-radius: 12px;
    }
    .deliveries-list-content {
      padding: 12px !important;
    }
    .delivery-items-container {
      display: flex;
      flex-direction: column;
      gap: 8px;
      max-height: 380px;
      overflow-y: auto;
    }
    .delivery-item {
      padding: 12px;
      border: 1px solid var(--mat-sys-outline-variant, #e0e0e0);
      border-radius: 8px;
      cursor: pointer;
      background: var(--mat-sys-surface, #fff);
      transition: border-color 0.2s, background 0.2s;
    }
    .delivery-item:hover {
      background: var(--mat-sys-surface-variant, #f5f5f5);
    }
    .delivery-item--selected {
      border-color: var(--mat-sys-primary, #e65100);
      background: var(--mat-sys-surface-container-high, #fff3e0);
    }
    .delivery-item-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
    }
    .delivery-item-body p {
      margin: 2px 0;
    }

    .delivery-status-badge {
      font-size: 0.65rem;
      font-weight: 600;
      padding: 2px 6px;
      border-radius: 4px;
    }
    .badge--pending { background: #fce4ec; color: #c2185b; }
    .badge--assigned { background: #e8f5e9; color: #2b7a2e; }
    .badge--picked_up { background: #fff8e1; color: #f57f17; }
    .badge--delivered { background: #eceff1; color: #37474f; }

    .override-card {
      border-radius: 12px;
    }
    .override-content {
      padding: 16px !important;
    }
    .full-width { width: 100%; }
    .mb-4 { margin-bottom: 16px; }
    .mt-4 { margin-top: 16px; }
  `,
})
export class DeliveriesMapComponent implements OnInit {
  protected readonly store = inject(DeliveriesStore);

  // Filter partners that are not offline to serve as potential assignment targets
  protected readonly availablePartners = computed(() => {
    return this.store.partners().filter((p) => p.status !== 'OFFLINE');
  });

  ngOnInit(): void {
    this.store.loadAll();
  }

  // Projection logic: geo coordinates -> svg pixel coords
  // San Francisco bounds: Lat [37.75, 37.80], Lng [-122.45, -122.40]
  lngToX(lng: number): number {
    const minLng = -122.45;
    const maxLng = -122.40;
    return 50 + ((lng - minLng) / (maxLng - minLng)) * 500;
  }

  latToY(lat: number): number {
    const minLat = 37.75;
    const maxLat = 37.80;
    return 350 - ((lat - minLat) / (maxLat - minLat)) * 300;
  }

  getTransform(lat: number, lng: number): string {
    return `translate(${this.lngToX(lng)}, ${this.latToY(lat)})`;
  }

  getPartnerColor(status: string): string {
    if (status === 'ONLINE') return '#43a047';
    if (status === 'BUSY') return '#fb8c00';
    return '#757575';
  }

  onOverride(deliveryId: string, partnerId: string | null): void {
    this.store.assignPartner({ deliveryId, partnerId });
  }
}
