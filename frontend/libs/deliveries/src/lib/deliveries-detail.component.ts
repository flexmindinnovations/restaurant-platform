import {
  ChangeDetectionStrategy,
  Component,
  inject,
  OnInit,
  OnDestroy,
  computed,
  effect,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatFormFieldModule } from '@angular/material/form-field';
import { LucideRefreshCw, LucideArrowLeft } from '@lucide/angular';
import { HeaderService, PageHeader, StatusBadge } from '@app/shared';
import { DeliveriesStore } from './deliveries.store';
import { DeliveryPartner, PartnerStatus, ActiveDelivery } from './deliveries.model';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-deliveries-detail',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatSelectModule,
    MatTooltipModule,
    MatFormFieldModule,
    LucideRefreshCw,
    LucideArrowLeft,
    PageHeader,
    StatusBadge,
  ],
  templateUrl: './deliveries-detail.component.html',
  styleUrl: './deliveries-detail.component.scss',
})
export class DeliveriesDetailComponent implements OnInit, OnDestroy {
  protected readonly store = inject(DeliveriesStore);
  private readonly headerService = inject(HeaderService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  protected readonly deliveryId = signal<string | null>(null);
  private routeSub?: Subscription;

  // Filter partners that are not offline to serve as potential assignment targets
  protected readonly availablePartners = computed<DeliveryPartner[]>(() => {
    return this.store.partners().filter((p: DeliveryPartner) => p.status !== 'OFFLINE');
  });

  protected readonly currentDelivery = computed<ActiveDelivery | null>(() => {
    const id = this.deliveryId();
    if (!id) return null;
    return this.store.deliveries().find((d) => d.id === id) || null;
  });

  constructor() {
    effect(() => {
      this.headerService.setLoading(this.store.loading());
    });
  }

  ngOnInit(): void {
    this.store.loadAll();
    this.routeSub = this.route.paramMap.subscribe((params) => {
      this.deliveryId.set(params.get('id'));
    });
  }

  ngOnDestroy(): void {
    this.headerService.setLoading(false);
    this.routeSub?.unsubscribe();
  }

  goBack(): void {
    this.router.navigate(['/deliveries']);
  }

  // Projection logic: geo coordinates -> svg pixel coords
  // San Francisco bounds: Lat [37.75, 37.80], Lng [-122.45, -122.40]
  lngToX(lng: number): number {
    const minLng = -122.45;
    const maxLng = -122.4;
    return 50 + ((lng - minLng) / (maxLng - minLng)) * 500;
  }

  latToY(lat: number): number {
    const minLat = 37.75;
    const maxLat = 37.8;
    return 350 - ((lat - minLat) / (maxLat - minLat)) * 300;
  }

  getTransform(lat: number, lng: number): string {
    return `translate(${this.lngToX(lng)}, ${this.latToY(lat)})`;
  }

  getPartnerColor(status: PartnerStatus): string {
    if (status === 'ONLINE') return '#43a047';
    if (status === 'BUSY') return '#fb8c00';
    return '#757575';
  }

  onOverride(deliveryId: string, partnerId: string | null): void {
    this.store.assignPartner({ deliveryId, partnerId });
  }
}
