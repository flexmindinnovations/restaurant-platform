import { inject } from '@angular/core';
import { signalStore, withState, withMethods, patchState } from '@ngrx/signals';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { tapResponse } from '@ngrx/operators';
import { pipe, switchMap } from 'rxjs';
import { Review } from './reviews.model';
import { ReviewsService } from './reviews.service';

export interface ReviewsState {
  reviews: Review[];
  loading: boolean;
  error: string | null;
  selectedReview: Review | null;
}

const initialState: ReviewsState = {
  reviews: [],
  loading: false,
  error: null,
  selectedReview: null,
};

export const ReviewsStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),
  withMethods((store, service = inject(ReviewsService)) => ({
    loadAll: rxMethod<void>(
      pipe(
        switchMap(() => {
          patchState(store, { loading: true, error: null });
          return service.getReviews().pipe(
            tapResponse({
              next: (reviews) => patchState(store, { reviews, loading: false }),
              error: (err: unknown) => patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    moderateReview: rxMethod<{ id: string; status: 'APPROVED' | 'REJECTED' | 'FLAGGED' }>(
      pipe(
        switchMap(({ id, status }) => {
          patchState(store, { loading: true, error: null });
          return service.moderateReview(id, status).pipe(
            tapResponse({
              next: (reviews) => {
                const updatedSelected = reviews.find((r) => r.id === id) || null;
                patchState(store, {
                  reviews,
                  selectedReview: store.selectedReview()?.id === id ? updatedSelected : store.selectedReview(),
                  loading: false,
                });
              },
              error: (err: unknown) => patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    submitReply: rxMethod<{ id: string; reply: string }>(
      pipe(
        switchMap(({ id, reply }) => {
          patchState(store, { loading: true, error: null });
          return service.submitReply(id, reply).pipe(
            tapResponse({
              next: (reviews) => {
                const updatedSelected = reviews.find((r) => r.id === id) || null;
                patchState(store, {
                  reviews,
                  selectedReview: store.selectedReview()?.id === id ? updatedSelected : store.selectedReview(),
                  loading: false,
                });
              },
              error: (err: unknown) => patchState(store, { error: String(err), loading: false }),
            }),
          );
        }),
      ),
    ),

    selectReview(review: Review | null): void {
      patchState(store, { selectedReview: review });
    },
  })),
);

export type ReviewsStoreType = InstanceType<typeof ReviewsStore>;
