import { inject } from '@angular/core';
import { signalStore, withState, withMethods, patchState } from '@ngrx/signals';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { tapResponse } from '@ngrx/operators';
import { pipe, switchMap, exhaustMap, of } from 'rxjs';
import { HttpErrorResponse } from '@angular/common/http';
import { UserProfile } from './users.model';
import { UsersService } from './users.service';

function getErrorMessage(err: unknown): string {
  if (err instanceof HttpErrorResponse) {
    const body = err.error;
    if (body && typeof body === 'object') {
      if ('error' in body && body.error && typeof body.error === 'object' && 'message' in body.error) {
        return String(body.error.message);
      }
      if ('message' in body && body.message) {
        return String(body.message);
      }
    }
    return err.message;
  }
  if (err instanceof Error) {
    return err.message;
  }
  return String(err);
}

export interface ProfileState {
  profile: UserProfile | null;
  loading: boolean;
  saving: boolean;
  successMessage: string | null;
  error: string | null;
}

const initialState: ProfileState = {
  profile: null,
  loading: true,
  saving: false,
  successMessage: null,
  error: null,
};

export const ProfileStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),
  withMethods((store, service = inject(UsersService)) => ({
    loadProfile: rxMethod<void>(
      pipe(
        exhaustMap(() => {
          if (store.profile() !== null) {
            patchState(store, { loading: false });
            return of(store.profile());
          }
          patchState(store, { loading: true, error: null });
          return service.getProfile().pipe(
            tapResponse({
              next: (profile) => patchState(store, { profile, loading: false }),
              error: (err) => {
                patchState(store, { error: getErrorMessage(err), loading: false });
              },
            }),
          );
        }),
      ),
    ),

    updateProfile: rxMethod<Partial<UserProfile>>(
      pipe(
        switchMap((profileData) => {
          patchState(store, { saving: true, error: null, successMessage: null });
          return service.updateProfile(profileData).pipe(
            tapResponse({
              next: (res) => {
                const current = store.profile();
                const updated = current ? { ...current, ...profileData } : null;
                patchState(store, {
                  profile: updated,
                  saving: false,
                  successMessage: res.message || 'Profile saved successfully!',
                });
              },
              error: (err) => {
                patchState(store, { error: getErrorMessage(err), saving: false });
              },
            }),
          );
        }),
      ),
    ),

    clearMessages(): void {
      patchState(store, { successMessage: null, error: null });
    },
  })),
);
