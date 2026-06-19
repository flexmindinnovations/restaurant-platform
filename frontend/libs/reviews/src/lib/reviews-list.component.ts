import { ChangeDetectionStrategy, Component, inject, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { PageHeader } from '../../../shared/src/lib/page-header';
import { EmptyState } from '../../../shared/src/lib/empty-state';
import { ReviewsStore } from './reviews.store';
import { Review } from './reviews.model';

@Component({
  selector: 'app-reviews-list',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatInputModule,
    MatFormFieldModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatProgressBarModule,
    MatTooltipModule,
    PageHeader,
    EmptyState,
  ],
  template: `
    <app-page-header title="Reviews & Moderation" subtitle="Monitor customer feedback, moderate flagged reviews, and manage owner replies">
    </app-page-header>

    <!-- Filters -->
    <div class="filters-row">
      <mat-form-field appearance="outline" class="search-field">
        <mat-label>Search reviews</mat-label>
        <mat-icon matPrefix>search</mat-icon>
        <input matInput [ngModel]="searchValue()" (ngModelChange)="searchValue.set($event)"
          placeholder="Search by restaurant, customer or comment..." />
      </mat-form-field>

      <mat-chip-listbox [ngModel]="statusFilter()" (ngModelChange)="statusFilter.set($event)"
        class="filter-chips" aria-label="Status filter">
        <mat-chip-option value="ALL">All Reviews</mat-chip-option>
        <mat-chip-option value="FLAGGED">Moderation Queue (Flagged)</mat-chip-option>
        <mat-chip-option value="APPROVED">Approved</mat-chip-option>
        <mat-chip-option value="PENDING">Pending</mat-chip-option>
      </mat-chip-listbox>
    </div>

    <!-- Loading bar -->
    @if (store.loading()) {
      <mat-progress-bar mode="indeterminate" class="mb-4" />
    }

    <!-- Table -->
    <div class="table-container mat-elevation-z1">
      @if (filteredReviews().length === 0) {
        <app-empty-state icon="star_rate" title="No reviews found"
          message="No reviews match your selected filters." />
      } @else {
        <table mat-table [dataSource]="filteredReviews()" class="full-width">
          <!-- Restaurant -->
          <ng-container matColumnDef="restaurant">
            <th mat-header-cell *matHeaderCellDef>Restaurant</th>
            <td mat-cell *matCellDef="let rev" class="font-semibold">{{ rev.restaurant_name }}</td>
          </ng-container>

          <!-- Customer -->
          <ng-container matColumnDef="customer">
            <th mat-header-cell *matHeaderCellDef>Customer</th>
            <td mat-cell *matCellDef="let rev">{{ rev.customer_name }}</td>
          </ng-container>

          <!-- Rating -->
          <ng-container matColumnDef="rating">
            <th mat-header-cell *matHeaderCellDef>Rating</th>
            <td mat-cell *matCellDef="let rev">
              <div class="rating-stars">
                @for (star of [1, 2, 3, 4, 5]; track star) {
                  <mat-icon class="star-icon" [class.star-filled]="star <= rev.rating">star</mat-icon>
                }
              </div>
            </td>
          </ng-container>

          <!-- Sentiment -->
          <ng-container matColumnDef="sentiment">
            <th mat-header-cell *matHeaderCellDef>Sentiment</th>
            <td mat-cell *matCellDef="let rev">
              <span class="custom-badge" [class]="'badge-sentiment--' + rev.sentiment.toLowerCase()">
                {{ rev.sentiment }}
              </span>
            </td>
          </ng-container>

          <!-- Status -->
          <ng-container matColumnDef="status">
            <th mat-header-cell *matHeaderCellDef>Status</th>
            <td mat-cell *matCellDef="let rev">
              <span class="custom-badge" [class]="'badge-status--' + rev.status.toLowerCase()">
                {{ rev.status }}
              </span>
            </td>
          </ng-container>

          <!-- Created At -->
          <ng-container matColumnDef="created_at">
            <th mat-header-cell *matHeaderCellDef>Date</th>
            <td mat-cell *matCellDef="let rev" class="text-sm opacity-85">
              {{ rev.created_at | date: 'shortDate' }}
            </td>
          </ng-container>

          <!-- Actions -->
          <ng-container matColumnDef="actions">
            <th mat-header-cell *matHeaderCellDef></th>
            <td mat-cell *matCellDef="let rev">
              <div class="actions-cell">
                <button mat-stroked-button (click)="onViewDetails(rev)">
                  Details & Reply
                </button>
                @if (rev.status === 'FLAGGED') {
                  <button mat-flat-button color="primary" (click)="onApprove(rev.id); $event.stopPropagation()">
                    Approve
                  </button>
                  <button mat-flat-button color="warn" (click)="onReject(rev.id); $event.stopPropagation()">
                    Reject
                  </button>
                }
              </div>
            </td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
          <tr mat-row *matRowDef="let row; columns: displayedColumns" class="table-row"></tr>
        </table>
      }
    </div>

    <!-- Review Details Modal -->
    @if (store.selectedReview(); as review) {
      <div class="modal-backdrop" (click)="onCloseDetails()">
        <div class="modal-card" (click)="$event.stopPropagation()">
          <div class="modal-header">
            <h3>Review Details</h3>
            <button mat-icon-button (click)="onCloseDetails()">
              <mat-icon>close</mat-icon>
            </button>
          </div>
          
          <div class="modal-body">
            <div class="review-detail-grid">
              <div>
                <p class="label">Restaurant</p>
                <p class="value font-semibold">{{ review.restaurant_name }}</p>
              </div>
              <div>
                <p class="label">Customer</p>
                <p class="value">{{ review.customer_name }}</p>
              </div>
              <div>
                <p class="label">Rating</p>
                <div class="rating-stars value">
                  @for (star of [1, 2, 3, 4, 5]; track star) {
                    <mat-icon class="star-icon" [class.star-filled]="star <= review.rating">star</mat-icon>
                  }
                </div>
              </div>
              <div>
                <p class="label">Date</p>
                <p class="value">{{ review.created_at | date: 'medium' }}</p>
              </div>
            </div>

            <div class="detail-section">
              <p class="label">Comment</p>
              <p class="comment-text">"{{ review.comment }}"</p>
            </div>

            <div class="detail-section">
              <p class="label">AI Sentiment & Tags</p>
              <div class="sentiment-chips">
                <span class="custom-badge" [class]="'badge-sentiment--' + review.sentiment.toLowerCase()">
                  {{ review.sentiment }} Sentiment
                </span>
                @for (tag of review.tags; track tag) {
                  <span class="tag-chip">{{ tag }}</span>
                }
              </div>
            </div>

            <!-- Owner Reply Section -->
            <div class="detail-section border-t pt-4">
              <p class="label font-semibold">Owner Reply</p>
              @if (review.owner_reply) {
                <div class="existing-reply">
                  <p class="reply-text">{{ review.owner_reply }}</p>
                  <button mat-button color="warn" (click)="replyText.set(review.owner_reply || '')">
                    Edit Reply
                  </button>
                </div>
              } @else {
                <div class="reply-form">
                  <mat-form-field appearance="outline" class="full-width">
                    <mat-label>Write owner reply...</mat-label>
                    <textarea matInput rows="3" [ngModel]="replyText()" (ngModelChange)="replyText.set($event)"></textarea>
                  </mat-form-field>
                  <div class="reply-actions">
                    <button mat-flat-button color="primary" [disabled]="!replyText().trim()" (click)="onSubmitReply(review.id)">
                      Submit Reply
                    </button>
                  </div>
                </div>
              }
            </div>
          </div>

          <div class="modal-footer">
            <div class="moderation-actions">
              <span class="label">Moderation:</span>
              <button mat-stroked-button color="primary" [disabled]="review.status === 'APPROVED'" (click)="onApprove(review.id)">
                Approve
              </button>
              <button mat-stroked-button color="warn" [disabled]="review.status === 'REJECTED'" (click)="onReject(review.id)">
                Reject
              </button>
              <button mat-stroked-button color="accent" [disabled]="review.status === 'FLAGGED'" (click)="onFlag(review.id)">
                Flag for Moderation
              </button>
            </div>
          </div>
        </div>
      </div>
    }
  `,
  styles: `
    .filters-row {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 16px;
      flex-wrap: wrap;
    }
    .search-field { flex: 1; min-width: 240px; }
    .filter-chips { display: flex; gap: 8px; }
    .table-container {
      border-radius: 8px;
      overflow: hidden;
      background: var(--mat-sys-surface, #fff);
    }
    .full-width { width: 100%; }
    .table-row:hover { background: var(--mat-sys-surface-variant, #f5f5f5); }

    .rating-stars {
      display: flex;
      align-items: center;
      gap: 2px;
    }
    .star-icon {
      font-size: 18px !important;
      width: 18px !important;
      height: 18px !important;
      color: #e0e0e0;
    }
    .star-filled {
      color: #ffb300;
    }
    
    .custom-badge {
      font-size: 0.72rem;
      font-weight: 600;
      padding: 3px 8px;
      border-radius: 4px;
      text-transform: uppercase;
      display: inline-block;
    }

    .badge-sentiment--positive { background: #e8f5e9; color: #2e7d32; }
    .badge-sentiment--neutral { background: #f5f5f5; color: #616161; }
    .badge-sentiment--negative { background: #ffebee; color: #c62828; }

    .badge-status--approved { background: #e8f5e9; color: #2e7d32; }
    .badge-status--pending { background: #fff8e1; color: #f57f17; }
    .badge-status--flagged { background: #fff3e0; color: #e65100; }
    .badge-status--rejected { background: #ffebee; color: #c62828; }

    .actions-cell {
      display: flex;
      gap: 8px;
      justify-content: flex-end;
      align-items: center;
    }

    .modal-backdrop {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0, 0, 0, 0.42);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 1000;
    }
    .modal-card {
      background: #fff;
      border-radius: 12px;
      width: 90%;
      max-width: 600px;
      display: flex;
      flex-direction: column;
      max-height: 85vh;
      box-shadow: 0 8px 32px rgba(0,0,0,0.2);
      overflow: hidden;
    }
    .modal-header {
      padding: 16px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #f0f0f0;
    }
    .modal-header h3 {
      margin: 0;
      font-size: 1.2rem;
      font-weight: 600;
    }
    .modal-body {
      padding: 20px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .review-detail-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
    }
    .label {
      font-size: 0.78rem;
      color: #757575;
      margin: 0 0 4px 0;
      text-transform: uppercase;
      font-weight: 500;
    }
    .value {
      margin: 0;
      font-size: 0.95rem;
    }
    .comment-text {
      font-style: italic;
      font-size: 1rem;
      color: #424242;
      background: #f9f9f9;
      padding: 12px 16px;
      border-radius: 8px;
      margin: 0;
    }
    .sentiment-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }
    .tag-chip {
      background: #efebe9;
      color: #4e342e;
      font-size: 0.75rem;
      font-weight: 500;
      padding: 4px 10px;
      border-radius: 100px;
    }
    .existing-reply {
      background: #f1f8e9;
      border-left: 4px solid #8bc34a;
      padding: 12px 16px;
      border-radius: 4px;
    }
    .reply-text {
      margin: 0 0 8px 0;
      font-size: 0.95rem;
      color: #33691e;
    }
    .reply-actions {
      display: flex;
      justify-content: flex-end;
      margin-top: 8px;
    }
    .modal-footer {
      padding: 16px 20px;
      border-top: 1px solid #f0f0f0;
      background: #fafafa;
    }
    .moderation-actions {
      display: flex;
      gap: 8px;
      align-items: center;
      flex-wrap: wrap;
    }
    .border-t { border-top: 1px solid #f0f0f0; }
    .pt-4 { padding-top: 16px; }
    .mb-4 { margin-bottom: 16px; }
  `,
})
export class ReviewsListComponent implements OnInit {
  protected readonly store = inject(ReviewsStore);
  protected readonly displayedColumns = [
    'restaurant',
    'customer',
    'rating',
    'sentiment',
    'status',
    'created_at',
    'actions',
  ];

  protected readonly searchValue = signal('');
  protected readonly statusFilter = signal<'ALL' | 'FLAGGED' | 'APPROVED' | 'PENDING'>('ALL');
  protected readonly replyText = signal('');

  protected readonly filteredReviews = computed(() => {
    let list = this.store.reviews();

    // Apply Search
    const search = this.searchValue().trim().toLowerCase();
    if (search) {
      list = list.filter((r) =>
        r.restaurant_name.toLowerCase().includes(search) ||
        r.customer_name.toLowerCase().includes(search) ||
        r.comment.toLowerCase().includes(search)
      );
    }

    // Apply Status Filter
    const filter = this.statusFilter();
    if (filter !== 'ALL') {
      list = list.filter((r) => r.status === filter);
    }

    return list;
  });

  ngOnInit(): void {
    this.store.loadAll();
  }

  onViewDetails(review: Review): void {
    this.store.selectReview(review);
    this.replyText.set('');
  }

  onCloseDetails(): void {
    this.store.selectReview(null);
  }

  onApprove(id: string): void {
    this.store.moderateReview({ id, status: 'APPROVED' });
  }

  onReject(id: string): void {
    if (confirm('Are you sure you want to reject/remove this review?')) {
      this.store.moderateReview({ id, status: 'REJECTED' });
    }
  }

  onFlag(id: string): void {
    this.store.moderateReview({ id, status: 'FLAGGED' });
  }

  onSubmitReply(id: string): void {
    const text = this.replyText().trim();
    if (text) {
      this.store.submitReply({ id, reply: text });
      this.replyText.set('');
    }
  }
}
