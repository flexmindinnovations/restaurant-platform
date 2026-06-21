import {
  ChangeDetectionStrategy,
  Component,
  inject,
  OnInit,
  OnDestroy,
  effect,
  signal,
  computed,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import {
  LucideSearch,
  LucideStar,
  LucideEye,
  LucideCircleCheck,
  LucideBan,
} from '@lucide/angular';

import { PageHeader, HeaderService, EmptyState } from '@app/shared';
import { DatatableComponent, DatatableCellDirective, type DatatableColumn } from '@app/design-system';
import { ReviewsStore } from './reviews.store';
import { Review } from './reviews.model';
import { ReviewsDetailComponent } from './reviews-detail.component';

@Component({
  selector: 'app-reviews-list',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    FormsModule,
    MatInputModule,
    MatFormFieldModule,
    MatButtonModule,
    MatChipsModule,
    LucideSearch,
    LucideStar,
    LucideEye,
    LucideCircleCheck,
    LucideBan,
    MatTooltipModule,
    MatDialogModule,
    PageHeader,
    EmptyState,
    DatatableComponent,
    DatatableCellDirective,
  ],
  templateUrl: './reviews-list.component.html',
  styleUrl: './reviews-list.component.scss',
})
export class ReviewsListComponent implements OnInit, OnDestroy {
  protected readonly store = inject(ReviewsStore);
  private readonly headerService = inject(HeaderService);
  private readonly dialog = inject(MatDialog);

  protected readonly columns: DatatableColumn[] = [
    { key: 'restaurant', label: 'Restaurant', sortable: true },
    { key: 'customer', label: 'Customer', sortable: true },
    { key: 'rating', label: 'Rating', sortable: true },
    { key: 'sentiment', label: 'Sentiment', sortable: true },
    { key: 'status', label: 'Status', sortable: true },
    { key: 'created_at', label: 'Date', sortable: true },
    { key: 'actions', label: 'Actions' },
  ];

  protected readonly searchValue = signal('');
  protected readonly statusFilter = signal<'ALL' | 'FLAGGED' | 'APPROVED' | 'PENDING'>('ALL');

  protected readonly filteredReviews = computed(() => {
    let list = this.store.reviews();

    // Apply Search
    const search = this.searchValue().trim().toLowerCase();
    if (search) {
      list = list.filter(
        (r) =>
          r.restaurant_name.toLowerCase().includes(search) ||
          r.customer_name.toLowerCase().includes(search) ||
          r.comment.toLowerCase().includes(search),
      );
    }

    // Apply Status Filter
    const filter = this.statusFilter();
    if (filter !== 'ALL') {
      list = list.filter((r) => r.status === filter);
    }

    return list;
  });

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

  onViewDetails(review: Review): void {
    this.dialog.open(ReviewsDetailComponent, {
      data: { reviewId: review.id },
      width: '650px',
      maxWidth: '95vw',
    });
  }

  onRowClick(row: unknown): void {
    const review = row as Review;
    if (review && review.id) {
      this.onViewDetails(review);
    }
  }

  onApprove(id: string): void {
    this.store.moderateReview({ id, status: 'APPROVED' });
  }

  onReject(id: string): void {
    if (confirm('Are you sure you want to reject/remove this review?')) {
      this.store.moderateReview({ id, status: 'REJECTED' });
    }
  }
}
