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
import { Router } from '@angular/router';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatCardModule } from '@angular/material/card';
import {
  LucideSearch,
  LucideChevronRight,
  LucideRefreshCw,
} from '@lucide/angular';
import {
  HeaderService,
  PageHeader,
  StatusBadge,
  EmptyState,
} from '@app/shared';
import {
  DatatableComponent,
  DatatableCellDirective,
  DatatableColumn,
} from '@app/design-system';
import { DeliveriesStore } from './deliveries.store';
import { ActiveDelivery } from './deliveries.model';

@Component({
  selector: 'app-deliveries-list',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    FormsModule,
    MatInputModule,
    MatFormFieldModule,
    MatButtonModule,
    MatChipsModule,
    MatTooltipModule,
    MatCardModule,
    LucideSearch,
    LucideChevronRight,
    LucideRefreshCw,
    PageHeader,
    StatusBadge,
    EmptyState,
    DatatableComponent,
    DatatableCellDirective,
  ],
  templateUrl: './deliveries-list.component.html',
  styleUrl: './deliveries-list.component.scss',
})
export class DeliveriesListComponent implements OnInit, OnDestroy {
  protected readonly store = inject(DeliveriesStore);
  private readonly headerService = inject(HeaderService);
  private readonly router = inject(Router);

  protected readonly columns: DatatableColumn[] = [
    { key: 'id', label: 'Order ID', sortable: true },
    { key: 'restaurant_name', label: 'Restaurant', sortable: true },
    { key: 'customer_address', label: 'Destination', sortable: true },
    { key: 'partner_name', label: 'Courier', sortable: true },
    { key: 'status', label: 'Status', sortable: true },
    { key: 'actions', label: 'Actions' },
  ];

  protected readonly searchValue = signal('');
  protected readonly statusFilter = signal<string>('ALL');

  constructor() {
    effect(() => {
      this.headerService.setLoading(this.store.loading());
    });
  }

  ngOnInit(): void {
    this.store.loadAll();
  }

  ngOnDestroy(): void {
    this.headerService.setLoading(false);
  }

  protected readonly filteredDeliveries = computed(() => {
    const list = this.store.deliveries();
    const search = this.searchValue().toLowerCase().trim();
    const status = this.statusFilter();

    return list.filter((del) => {
      const matchesSearch =
        !search ||
        del.restaurant_name.toLowerCase().includes(search) ||
        del.customer_address.toLowerCase().includes(search) ||
        del.id.toLowerCase().includes(search);

      const matchesStatus = status === 'ALL' || del.status === status;

      return matchesSearch && matchesStatus;
    });
  });

  onSearch(value: string): void {
    this.searchValue.set(value);
  }

  onStatusFilter(value: string): void {
    this.statusFilter.set(value);
  }

  onRowClick(row: unknown): void {
    const delivery = row as ActiveDelivery;
    this.router.navigate(['/deliveries', delivery.id]);
  }
}
