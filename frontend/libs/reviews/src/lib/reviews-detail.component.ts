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
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { LucideStar, LucideX } from '@lucide/angular';
import { HeaderService } from '@app/shared';
import { ReviewsStore } from './reviews.store';
import { Review } from './reviews.model';

@Component({
  selector: 'app-reviews-detail',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatInputModule,
    MatFormFieldModule,
    MatTooltipModule,
    MatDialogModule,
    LucideStar,
    LucideX,
  ],
  templateUrl: './reviews-detail.component.html',
  styleUrl: './reviews-detail.component.scss',
})
export class ReviewsDetailComponent implements OnInit {
  protected readonly store = inject(ReviewsStore);
  private readonly headerService = inject(HeaderService);
  private readonly dialogRef = inject(MatDialogRef<ReviewsDetailComponent>);
  private readonly dialogData = inject<{ reviewId: string }>(MAT_DIALOG_DATA);

  protected readonly reviewId = signal<string | null>(null);
  protected readonly replyText = signal<string>('');

  protected readonly currentReview = computed<Review | null>(() => {
    const id = this.reviewId();
    if (!id) return null;
    return this.store.reviews().find((r) => r.id === id) || null;
  });

  constructor() {
    effect(() => {
      this.headerService.setLoading(this.store.loading());
    });

    // Populate reply text when review loads/changes and already has a reply
    effect(() => {
      const review = this.currentReview();
      if (review && review.owner_reply) {
        this.replyText.set(review.owner_reply);
      } else {
        this.replyText.set('');
      }
    });
  }

  ngOnInit(): void {
    this.store.loadAll();
    this.reviewId.set(this.dialogData.reviewId);
  }

  goBack(): void {
    this.dialogRef.close();
  }

  onApprove(id: string): void {
    this.store.moderateReview({ id, status: 'APPROVED' });
  }

  onReject(id: string): void {
    if (confirm('Are you sure you want to reject/remove this review?')) {
      this.store.moderateReview({ id, status: 'REJECTED' });
      this.dialogRef.close();
    }
  }

  onFlag(id: string): void {
    this.store.moderateReview({ id, status: 'FLAGGED' });
  }

  onSubmitReply(id: string): void {
    const text = this.replyText().trim();
    if (text) {
      this.store.submitReply({ id, reply: text });
    }
  }
}
